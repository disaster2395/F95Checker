import asyncio
import configparser
import contextlib
import dataclasses
import enum
import json
import pathlib
import re
import shutil
import sqlite3
import time
import types
import typing

import aiosqlite

from common.structs import (
    Browser,
    DefaultStyle,
    DisplayMode,
    Game,
    Label,
    MsgBox,
    ProxyType,
    SearchResult,
    Settings,
    Status,
    Tab,
    TexCompress,
    ThreadMatch,
    TimelineEvent,
    TimelineEventType,
    Timestamp,
    Type,
)
from common import parser
from external import (
    async_thread,
    error,
)
from modules import (
    api,
    colors,
    globals,
    msgbox,
    utils,
)


async def connect():
    await create_table(
        table_name="cookies",
        columns={
            "key":                         f'TEXT    PRIMARY KEY',
            "value":                       f'TEXT    DEFAULT ""',
        }
    )


def sql_to_py(value: str | int | float, data_type: typing.Type):
    args = getattr(data_type, "__args__", None)
    match getattr(data_type, "__name__", None):
        case "dict":
            try:
                value = data_type(json.loads(value))
                if args:
                    key_type = args[0]
                    value_type = args[1]
                    value = data_type((key_type(int(k) if (type(k) is str and k.isdigit()) else k), value_type(v)) for k, v in value.items())
            except json.JSONDecodeError:
                value = data_type([("", value)]) if value else data_type()
        case "list" | "tuple":
            if isinstance(value, str) and args and args[0] is float and re.fullmatch(r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})', value):
                value = colors.hex_to_rgba_0_1(value)
            else:
                try:
                    value = data_type(json.loads(value))
                except json.JSONDecodeError:
                    value = data_type([value]) if value else data_type()
                if args:
                    content_type = args[0]
                    if hasattr(content_type, "__dataclass_fields__"):
                        value = data_type(x for x in (content_type(**x) for x in value) if x is not None)
                    else:
                        value = data_type(x for x in (content_type(x) for x in value) if x is not None)
        case _:
            if isinstance(data_type, types.UnionType):
                if (
                    isinstance(value, str) and args and
                    getattr(args[0], "__name__", None) == "tuple" and
                    getattr(args[0], "__args__", [None])[0] is float and
                    re.fullmatch(r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})', value)
                ):
                    value = colors.hex_to_rgba_0_1(value)
                elif args and not (args[-1] is types.NoneType and value is None):
                    value = args[0](value)
                else:
                    value = None
            else:
                value = data_type(value)
    return value


def row_to_cls(row: sqlite3.Row, cls: typing.Type):
    types = cls.__annotations__
    data = {key: sql_to_py(value, types[key]) for key, value in dict(row).items() if key in types}
    return cls(**data)


async def load():
    cursor = await connection.execute("""
        SELECT *
        FROM cookies
    """)
    globals.cookies = {cookie["key"]: cookie["value"] for cookie in await cursor.fetchall()}


def py_to_sql(value: enum.Enum | Timestamp | bool | list | tuple | typing.Any):
    if hasattr(value, "value"):
        value = value.value
    elif hasattr(value, "hash"):
        value = value.hash
    elif hasattr(value, "id"):
        value = value.id
    elif type(value) is bool:
        value = int(value)
    elif isinstance(value, dict):
        value = value.copy()
        value = {getattr(k, "value", getattr(k, "id", k)): getattr(v, "value", getattr(v, "id", v)) for k, v in value.items()}
        value = json.dumps(value)
    elif isinstance(value, list):
        value = value.copy()
        value = [getattr(item, "value", getattr(item, "id", item)) for item in value]
        if value and hasattr(value[0], "__dataclass_fields__"):
            value = [dataclasses.asdict(item) for item in value]
        value = json.dumps(value)
    elif isinstance(value, tuple):
        if 3 <= len(value) <= 4 and all(type(item) in (float, int) for item in value):
            value = colors.rgba_0_1_to_hex(value)
        else:
            value = [getattr(item, "value", getattr(item, "id", item)) for item in value]
            if value and hasattr(value[0], "__dataclass_fields__"):
                value = [dataclasses.asdict(item) for item in value]
            value = json.dumps(value)
    return value


async def update_game_id(game: Game, new_id):
    await connection.execute(f"""
        UPDATE games
        SET
            id={new_id}
        WHERE id={game.id}
    """)
    globals.games[new_id] = game
    if game.id != new_id:
        del globals.games[game.id]

    await connection.execute(f"""
        UPDATE timeline_events
        SET
            game_id={new_id}
        WHERE game_id={game.id}
    """)
    for event in game.timeline_events:
        event.game_id = new_id

    for img in globals.images_path.glob(f"{game.id}.*"):
        try:
            shutil.move(img, img.with_name(f"{new_id}{''.join(img.suffixes)}"))
        except Exception:
            pass
    game.id = new_id
    game.refresh_image()


async def delete_label(label: Label):
    await connection.execute(f"""
        DELETE FROM labels
        WHERE id={label.id}
    """)
    for game in globals.games.values():
        if label in game.labels:
            game.remove_label(label)
    for flt in list(globals.gui.filters):
        if flt.match is label:
            globals.gui.filters.remove(flt)
    Label.remove(label)


async def delete_tab(tab: Tab):
    await connection.execute(f"""
        DELETE FROM tabs
        WHERE id={tab.id}
    """)
    for game in globals.games.values():
        if game.tab is tab:
            game.tab = None
    if globals.settings.display_tab is tab:
        globals.settings.display_tab = None
        await update_settings("display_tab")
    Tab.remove(tab)
    if globals.gui:
        globals.gui.recalculate_ids = True


async def delete_timeline_events(game_id: int):
    await connection.execute(f"""
        DELETE FROM timeline_events
        WHERE game_id={game_id}
    """)


async def update_cookies(new_cookies: dict[str, str]):
    await connection.execute(f"""
        DELETE FROM cookies
    """)
    for key, value in new_cookies.items():
        await connection.execute("""
            INSERT INTO cookies
            (key, value)
            VALUES
            (?, ?)
            ON CONFLICT DO NOTHING
        """, (key, value))
    globals.cookies = new_cookies
