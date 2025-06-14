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
