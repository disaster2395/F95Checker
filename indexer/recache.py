import asyncio
import contextlib
import logging
import os
from collections.abc import AsyncIterator, Iterable

import redis.exceptions

from indexer import cache

logger = logging.getLogger(__name__)
queue: asyncio.PriorityQueue[tuple[int, str]] = asyncio.PriorityQueue()
pending: dict[str, int] = {}


@contextlib.asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    """Own background refresh tasks within the cache and forum lifetimes."""
    global queue
    interval = int(os.environ.get("CACHE_REFRESH_INTERVAL", "86400"))
    if interval <= 0:
        raise ValueError("CACHE_REFRESH_INTERVAL must be a positive number of seconds")
    queue = asyncio.PriorityQueue()
    pending.clear()
    tasks = (
        asyncio.create_task(refresh_threads()),
        asyncio.create_task(watch_expired(interval)),
    )
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        pending.clear()


def enqueue(names: Iterable[str], *, expired: bool = False) -> None:
    """Deduplicate refreshes, promoting watcher invalidations over TTL work."""
    priority = int(expired)
    for name in names:
        if name in pending and pending[name] <= priority:
            continue
        pending[name] = priority
        queue.put_nowait((priority, name))


async def refresh_threads() -> None:
    """Refresh sequentially, sharing freshness checks and locks with API calls."""
    while True:
        priority, name = await queue.get()
        try:
            if pending.get(name) != priority:
                continue
            del pending[name]
            id = int(name.split(":")[1])
            await cache._maybe_update_thread_cache(id, name)
        except redis.exceptions.RedisError:
            logger.exception("Error refreshing cached %s", name)
        finally:
            queue.task_done()


async def watch_expired(interval: int) -> None:
    """Recover stale entries on startup and periodically without forcing TTLs."""
    while True:
        try:
            logger.info("Expired cache scan start")
            count = 0
            async for name in cache.redis.scan_iter("thread:*", 1000, "hash"):
                id = int(name.split(":")[1])
                if await cache._is_thread_cache_outdated(id, name):
                    enqueue((name,), expired=True)
                    count += 1
            logger.info("Expired cache scan queued %s threads", count)
        except redis.exceptions.RedisError:
            logger.exception("Error scanning expired thread cache")
        await asyncio.sleep(interval)
