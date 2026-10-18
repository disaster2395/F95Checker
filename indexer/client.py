import contextlib
import logging
import os
import sys
from collections.abc import AsyncGenerator, Callable, Mapping

import aiohttp
import anyio

from common import meta
from indexer import auth, transport
from indexer.auth import LoginError as LoginError
from indexer.transport import RequestError as RequestError

logger = logging.getLogger(__name__)


class Client:
    """Keep forum login state and retry one expired request after a shared login."""

    def __init__(
        self, session: transport.Session, host: str,
        credentials: tuple[str, str, str] | None, cookies: dict[str, str],
        needs_login: Callable[[bytes], bool],
    ) -> None:
        self._session: transport.Session = session
        self._host: str = host
        self._credentials: tuple[str, str, str] | None = credentials
        self.cookies: dict[str, str] = cookies
        self._needs_login: Callable[[bytes], bool] = needs_login
        self._login_lock: anyio.Lock = anyio.Lock()
        self._generation: int = 0
        self._login_error: LoginError | RequestError | None = None

    async def authenticate(self) -> None:
        credentials = self._credentials
        assert credentials is not None
        self.cookies.clear()
        await self._session.clear_auth()
        try:
            cookie = await auth.login(self._session, self._host, *credentials)
        except (LoginError, RequestError) as exc:
            self._login_error = exc
            self._generation += 1
            raise
        self._login_error = None
        self.cookies["xf_user"] = cookie
        self._generation += 1
        logger.info("Authenticated to F95zone using login credentials")

    @contextlib.asynccontextmanager
    async def get(
        self, url: str, *, params: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AsyncGenerator[transport.Response, None]:
        generation = self._generation
        if self._credentials is not None and not self.cookies:
            async with self._login_lock:
                if generation == self._generation:
                    await self.authenticate()
                elif self._login_error is not None:
                    raise self._login_error
            generation = self._generation
        request_cookies = self.cookies if cookies is None else cookies
        response = await self._session.get(url, params=params, cookies=request_cookies)
        if self._credentials is not None and self._needs_login(await response.read()):
            async with self._login_lock:
                if generation == self._generation:
                    await self.authenticate()
                elif self._login_error is not None:
                    raise self._login_error
            retry_cookies = dict(request_cookies)
            retry_cookies.update(self.cookies)
            response = await self._session.get(url, params=params, cookies=retry_cookies)
        cookie = self._session.cookie("xf_user", url)
        if cookie and generation == self._generation:
            self.cookies["xf_user"] = cookie
        yield response


@contextlib.asynccontextmanager
async def lifespan(
    host: str, *, timeout: aiohttp.ClientTimeout,
    needs_login: Callable[[bytes], bool],
) -> AsyncGenerator[Client, None]:
    cookie = os.environ.get("COOKIE_XF_USER")
    username = os.environ.get("F95_USERNAME", "")
    password = os.environ.get("F95_PASSWORD", "")
    secret = os.environ.get("F95_TOTP_SECRET", "")
    if not cookie and (username or password or secret) and not (username and password):
        raise LoginError("Set both F95_USERNAME and F95_PASSWORD for automatic login")
    try:
        solver_timeout = int(os.environ.get("F95_FLARESOLVERR_TIMEOUT", "60"))
    except ValueError:
        raise RequestError("F95_FLARESOLVERR_TIMEOUT must be a positive number of seconds") from None
    if solver_timeout <= 0:
        raise RequestError("F95_FLARESOLVERR_TIMEOUT must be a positive number of seconds")
    proxy_url = os.environ.get("F95_PROXY") or None
    solver_url = os.environ.get("F95_FLARESOLVERR_URL") or None
    credentials = (username, password, secret) if username and password else None
    user_agent = (
        f"F95Indexer/{meta.version} Python/{sys.version.split(' ')[0]} "
        f"aiohttp/{aiohttp.__version__}"
    )
    custom_user_agent = os.environ.get("F95_USER_AGENT")
    if custom_user_agent:
        if solver_url:
            logger.warning(
                "F95_USER_AGENT only applies to native HTTP; FlareSolverr uses its browser User-Agent"
            )
        else:
            user_agent = custom_user_agent
    mode = ("flaresolverr+proxy" if proxy_url else "flaresolverr") if solver_url else (
        "proxy" if proxy_url else "direct"
    )
    logger.info("Indexer connection mode: %s", mode)
    async with transport.lifespan(
        proxy_url=proxy_url, solver_url=solver_url, solver_timeout=solver_timeout,
        user_agent=user_agent, timeout=timeout,
    ) as session:
        client = Client(
            session, host, credentials, {"xf_user": cookie} if cookie else {}, needs_login,
        )
        yield client
