import asyncio
import contextlib
import datetime as dt
import json
import multiprocessing
import re
import socket
import time
from typing import Coroutine, Any

import aiofiles
import aiohttp
import async_timeout
import asynciolimiter

from common import legacy_parser
from common.structs import Game, MsgBox, Status, TimelineEventType, MultiProcessPipe, OldGame
from external import error, async_thread
from modules import globals, msgbox, icons, callbacks, utils, db, api

full_interval = dt.timedelta(days=7)
part_interval = dt.timedelta(days=2)


@contextlib.asynccontextmanager
async def request(method: str, url: str, read=True, no_cookies=False, **kwargs):
    timeout = kwargs.pop("timeout", None)
    if not timeout:
        timeout = globals.settings.request_timeout
    retries = globals.settings.max_retries + 1
    req_opts = dict(
        timeout=timeout,
        allow_redirects=True,
        max_redirects=None,
        ssl=api.ssl_context
    )
    for insecure_ssl_allowed_host in api.insecure_ssl_allowed_hosts:
        if url.startswith(insecure_ssl_allowed_host):
            req_opts["ssl"] = False
            break
    if no_cookies:
        cookies = {}
    else:
        cookies = globals.cookies
    ddos_guard_cookies = {}
    ddos_guard_first_challenge = False
    while retries:
        try:
            async with api.session.request(
                method,
                url,
                cookies=cookies | ddos_guard_cookies,
                **req_opts,
                **kwargs
            ) as req:
                if not read:
                    yield b"", req
                    break
                res = await req.read()
                if req.headers.get("server") in ("ddos-guard", "", None) and re.search(rb"<title>DDOS-GUARD</title>", res, flags=re.IGNORECASE):
                    # Attempt DDoS-Guard bypass (credits to https://git.gay/a/ddos-guard-bypass)
                    ddos_guard_cookies.update(api.cookiedict(req.cookies))
                    if not ddos_guard_first_challenge:
                        # First challenge: repeat original request with new cookies
                        ddos_guard_first_challenge = True
                        continue
                    # First challenge failed, attempt manual bypass and retry original request
                    referer = f"{req.url.scheme}://{req.url.host}"
                    headers = {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate",
                        "Referer": referer,
                        "Sec-Fetch-Mode": "no-cors"
                    }
                    for script in re.finditer(rb'loadScript\(\s*"(.+?)"', await req.read()):
                        script = str(script.group(1), encoding="utf-8")
                        async with api.session.request(
                            "GET",
                            f"{referer if script.startswith('/') else ''}{script}",
                            cookies=cookies | ddos_guard_cookies,
                            headers=headers | {
                                "Sec-Fetch-Dest": "script",
                                "Sec-Fetch-Site": "same-site" if "ddos-guard.net/" in script else "cross-site"
                            },
                            **req_opts
                        ) as script_req:
                            ddos_guard_cookies.update(api.cookiedict(script_req.cookies))
                            for image in re.finditer(rb"\.src\s*=\s*'(.+?)'", await script_req.read()):
                                image = str(image.group(1), encoding="utf-8")
                                async with api.session.request(
                                    "GET",
                                    f"{referer if image.startswith('/') else ''}{image}",
                                    cookies=cookies | ddos_guard_cookies,
                                    headers=headers | {
                                        "Sec-Fetch-Dest": "image",
                                        "Sec-Fetch-Site": "same-origin"
                                    },
                                    **req_opts
                                ) as image_req:
                                    ddos_guard_cookies.update(api.cookiedict(image_req.cookies))
                    async with api.session.request(
                        "POST",
                        f"{referer}/.well-known/ddos-guard/mark/",
                        json=api.ddos_guard_bypass_fake_mark,
                        cookies=cookies | ddos_guard_cookies,
                        headers=headers | {
                            "Content-Type": "text/plain;charset=UTF-8",
                            "DNT": "1",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin"
                        },
                        **req_opts
                    ) as mark_req:
                        ddos_guard_cookies.update(api.cookiedict(mark_req.cookies))
                    continue
                yield res, req
            break
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            if globals.settings.ignore_semaphore_timeouts and isinstance(exc, OSError) and exc.errno == 121:
                continue
            retries -= 1
            if not retries:
                raise


async def fetch(method: str, url: str, **kwargs):
    async with request(method, url, **kwargs) as (res, _):
        return res


async def fast_check(games: list[Game], full_queue: list[tuple[Game, str]]=None, full=False):
    games = list(filter(lambda game: not game.custom, games))

    async with api.xenforo_ratelimit, (api.fast_checks_sem or asyncio.Semaphore(1)):

        try:
            res = await fetch("GET", api.f95_fast_check_endpoint.format(threads=",".join(str(game.id) for game in games)), no_cookies=True)
            api.raise_f95zone_error(res)
            res = json.loads(res)
            if res["msg"] in ("Missing threads data", "Thread not found"):
                res["status"] = "ok"
                res["msg"] = {}
            api.raise_f95zone_error(res)
            versions = res["msg"]
        except Exception as exc:
            if isinstance(exc, msgbox.Exc):
                raise exc
            async with aiofiles.open(globals.self_path / "check_broken.bin", "wb") as f:
                await f.write(json.dumps(res).encode() if isinstance(res, (dict, list)) else res)
            raise msgbox.Exc(
                "Fast check error",
                "Something went wrong checking some of your games:\n"
                f"{error.text()}\n"
                "\n"
                "The response body has been saved to:\n"
                f"{globals.self_path / 'check_broken.bin'}\n"
                "Please submit a bug report on F95Zone or GitHub including this file.",
                MsgBox.error,
                more=error.traceback()
            )

        for game in games:

            version = versions.get(str(game.id))
            if not version or version == "Unknown":
                version = None
                # Full check games with no version data more often
                interval = part_interval
            else:
                interval = full_interval

            delta = dt.datetime.fromtimestamp(time.time()) - dt.datetime.fromtimestamp(game.last_full_check)

            interval_expired = (delta.total_seconds() > interval.total_seconds())

            game_is_unchecked = game.status is Status.Unchecked

            if interval_expired and not full and not game_is_unchecked:
                game.add_timeline_event(TimelineEventType.RecheckExpired, delta.days)

            this_full = full or (
                interval_expired or
                game_is_unchecked or
                (version and version != game.version) or
                (game.image.missing and game.image_url.startswith("http")) or
                api.last_check_before("10.1.1", game.last_check_version)  # Switch away from HEAD requests, new version parsing
            )
            if not this_full:
                globals.refresh_progress += 1
                continue

            full_queue.append((game, version))

async def full_check(game: Game, version: str):
    result = await full_check_internal(game, version)
    if result is not None:
        await result


async def full_check_internal(game: Game, version: str) -> Coroutine | None: # NOSONAR
    async with api.full_checks_counter, (api.full_checks_sem or asyncio.Semaphore(1)):
        if api.s429_sem.locked():
            await api.s429_sem.acquire()
            api.s429_sem.release()
        async with api.xenforo_ratelimit, request("GET", game.url, timeout=globals.settings.request_timeout * 2) as (res, req):
            if req.status == 429 and globals.settings.retry_on_429:
                async with api.s429_sem:
                    if globals.debug and globals.logger:
                        globals.logger.warning(
                            "[%s] Got 429 error during \"%s\" update, retry in 1 minute, %s game(s) left",
                            dt.datetime.now().astimezone(),
                            game.name,
                            api.full_checks_counter.count,
                        )
                    await asyncio.sleep(globals.settings.api_rate_limit_pause)
                    return full_check(game, version)

            api.raise_f95zone_error(res)
            if req.status in (403, 404):
                if not game.archived:
                    buttons = {
                        f"{icons.cancel} Do nothing": None,
                        f"{icons.trash_can_outline} Remove": lambda: callbacks.remove_game([game], bypass_confirm=True),
                        f"{icons.puzzle_outline} Convert": lambda: callbacks.convert_f95zone_to_custom(game)
                    }
                    utils.push_popup(
                        msgbox.msgbox, "Thread not found",
                        "The F95Zone thread for this game could not be found:\n"
                        f"{game.name}\n"
                        "It might have been privated, moved or deleted, maybe for breaking forum rules.\n"
                        "\n"
                        "You can remove this game from your library, or convert it to a custom game.\n"
                        "Custom games are untied from F95Zone and are not checked for updates, so\n"
                        "you won't get this error anymore. You can later convert it back to an F95Zone\n"
                        "game from its info popup. You can also find more details there.",
                        MsgBox.error,
                        buttons=buttons
                    )
                globals.refresh_progress += 1
                return
            url = utils.clean_thread_url(str(req.real_url))

        old_name = game.name
        old_version = game.version
        old_status = game.status

        parse = legacy_parser.thread
        args = (game.id, res, True)
        if globals.settings.use_parser_processes:
            # Using multiprocessing can help with interface stutters
            with (pipe := MultiProcessPipe())(multiprocessing.Process(target=parse, args=(*args, pipe))):
                try:
                    async with async_timeout.timeout(globals.settings.request_timeout):
                        ret = await pipe.get_async()
                except TimeoutError:
                    raise msgbox.Exc(
                        "Parser process timeout",
                        "The thread parser process did not respond in time.",
                        MsgBox.error
                    )
        else:
            ret = parse(*args)
        if isinstance(ret, legacy_parser.ParserException):
            raise msgbox.Exc(*ret.args, **ret.kwargs)

        if not version:
            if ret.thread_version:
                version = ret.thread_version
            else:
                version = "N/A"

        if old_status is not Status.Unchecked:
            if game.developer != ret.developer:
                game.add_timeline_event(TimelineEventType.ChangedDeveloper, game.developer, ret.developer)

            if game.type != ret.type:
                game.add_timeline_event(TimelineEventType.ChangedType, game.type.name, ret.type.name)

            if game.tags != ret.tags:
                if difference := [tag.text for tag in ret.tags if tag not in game.tags]:
                    game.add_timeline_event(TimelineEventType.TagsAdded, ", ".join(difference))
                if difference := [tag.text for tag in game.tags if tag not in ret.tags]:
                    game.add_timeline_event(TimelineEventType.TagsRemoved, ", ".join(difference))

            if game.score != ret.score:
                if game.score < ret.score:
                    game.add_timeline_event(TimelineEventType.ScoreIncreased, game.score, game.votes, ret.score, ret.votes)
                else:
                    game.add_timeline_event(TimelineEventType.ScoreDecreased, game.score, game.votes, ret.score, ret.votes)

        breaking_name_parsing    = api.last_check_before("9.6.4", game.last_check_version)  # Skip name change in update popup
        breaking_version_parsing = api.last_check_before("10.1.1",  game.last_check_version)  # Skip update popup and keep installed/finished checkboxes
        breaking_keep_old_image  = api.last_check_before("9.0",   game.last_check_version)  # Keep existing image files

        last_full_check = int(time.time())
        last_check_version = globals.version

        # Skip update popup and don't reset finished/installed checkboxes if refreshing with braking changes
        finished = game.finished
        installed = game.installed
        updated = game.updated
        if breaking_version_parsing or old_status is Status.Unchecked:
            if old_version == finished:
                finished = version  # Is breaking and was previously finished, mark again as finished
            if old_version == installed:
                installed = version  # Is breaking and was previously installed, mark again as installed
            old_version = version  # Don't include version change in popup for simple parsing adjustments
        else:
            if version != old_version:
                if not game.archived:
                    updated = True

        # Don't include name change in popup for simple parsing adjustments
        if breaking_name_parsing:
            old_name = ret.name

        fetch_image = game.image.missing
        if game.image_url != "custom" and not breaking_keep_old_image:
            fetch_image = fetch_image or (ret.image_url != game.image_url)

        unknown_tags_flag = game.unknown_tags_flag
        if len(ret.unknown_tags) > 0 and game.unknown_tags != ret.unknown_tags:
            unknown_tags_flag = True

        async def update_game():
            game.name = ret.name
            game.version = version
            game.developer = ret.developer
            game.type = ret.type
            game.status = ret.status
            game.url = url
            game.last_updated = ret.last_updated
            game.last_full_check = last_full_check
            game.last_check_version = last_check_version
            game.score = ret.score
            game.votes = ret.votes
            game.finished = finished
            game.installed = installed
            game.updated = updated
            game.description = ret.description
            game.changelog = ret.changelog
            game.tags = ret.tags
            game.unknown_tags = ret.unknown_tags
            game.unknown_tags_flag = unknown_tags_flag
            game.image_url = ret.image_url
            game.downloads = ret.downloads

            changed_name = ret.name != old_name
            changed_status = ret.status != old_status
            changed_version = version != old_version

            if old_status is not Status.Unchecked:
                if changed_name:
                    game.add_timeline_event(TimelineEventType.ChangedName, old_name, game.name)
                if changed_status:
                    game.add_timeline_event(TimelineEventType.ChangedStatus, old_status.name, game.status.name)
                if changed_version:
                    game.add_timeline_event(TimelineEventType.ChangedVersion, old_version, game.version)

            if not game.archived and old_status is not Status.Unchecked and (
                changed_name or changed_status or changed_version
            ):
                old_game = OldGame(
                    id=game.id,
                    name=old_name,
                    version=old_version,
                    status=old_status,
                )
                globals.updated_games[game.id] = old_game

        if fetch_image and game.image_url and game.image_url.startswith("http"):
            with api.images_counter:
                try:
                    res = await fetch("GET", game.image_url, timeout=globals.settings.request_timeout * 4, raise_for_status=True)
                except aiohttp.ClientResponseError as exc:
                    if exc.status < 400:
                        raise  # Not error status
                    if game.image_url.startswith("https://i.imgur.com"):
                        game.image_url = "blocked"
                    else:
                        game.image_url = "dead"
                    res = b""
                except aiohttp.ClientConnectorError as exc:
                    if not isinstance(exc.os_error, socket.gaierror):
                        raise  # Not a dead link
                    if api.is_f95zone_url(game.image_url):
                        raise  # Not a foreign host, raise normal connection error message
                    f95zone_ok = True
                    foreign_ok = True
                    try:
                        await async_thread.loop.run_in_executor(None, socket.gethostbyname, api.f95_domain)
                    except Exception:
                        f95zone_ok = False
                    try:
                        await async_thread.loop.run_in_executor(None, socket.gethostbyname, re.search(r"^https?://([^/]+)", ret.image_url).group(1))
                    except Exception:
                        foreign_ok = False
                    if f95zone_ok and not foreign_ok:
                        game.image_url = "dead"
                        res = b""
                    else:
                        raise  # Foreign host might not actually be dead
                async def set_image_and_update_game():
                    await game.set_image_async(res)
                    await update_game()
                await asyncio.shield(set_image_and_update_game())
        else:
            await asyncio.shield(update_game())
        globals.refresh_progress += 1

async def refresh(*games: list[Game], full=False, notifs=True, force_completed=False, force_archived=False):
    if globals.debug:
        globals.logger.warning("Run refresh via f95zone.to")

    if not await api.assert_login():
        return

    fast_queue: list[list[Game]] = [[]]
    full_queue: list[tuple[Game, str]] = []
    for game in (games or globals.games.values()):
        if game.custom:
            continue
        if not games and game.status is Status.Completed and not globals.settings.refresh_completed_games and not force_completed:
            continue
        if not games and game.archived and not globals.settings.refresh_archived_games and not force_archived:
            continue
        if len(fast_queue[-1]) == 100:
            fast_queue.append([])
        fast_queue[-1].append(game)

    notifs = notifs and globals.settings.check_notifs
    globals.refresh_progress += 1
    globals.refresh_total += sum(len(chunk) for chunk in fast_queue) + bool(notifs)

    # global fast_checks_sem, full_checks_sem
    api.fast_checks_sem = asyncio.Semaphore(globals.settings.refresh_workers)
    api.full_checks_sem = asyncio.Semaphore(int(max(1, globals.settings.refresh_workers / 10)))
    tasks: list[asyncio.Task] = []
    try:
        tasks = [asyncio.create_task(fast_check(chunk, full_queue, full=full)) for chunk in fast_queue]
        await asyncio.gather(*tasks)

        tasks = [asyncio.create_task(full_check(game, version)) for game, version in full_queue]
        await asyncio.gather(*tasks)
    except Exception:
        for task in tasks:
            task.cancel()
        api.fast_checks_sem = None
        api.full_checks_sem = None
        raise
    api.fast_checks_sem = None
    api.full_checks_sem = None

    if notifs:
        await api.check_notifs(standalone=False)

    if not games:
        globals.settings.last_successful_refresh.update(time.time())
        await db.update_settings("last_successful_refresh")
