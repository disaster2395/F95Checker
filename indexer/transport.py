import contextlib
import dataclasses
import logging
import uuid
from collections.abc import AsyncGenerator, Mapping
from typing import Literal, NotRequired, TypedDict
from urllib.parse import quote, unquote, urlencode, urlsplit

import aiohttp
import aiohttp_socks
import anyio
import bs4
import pydantic
import soupsieve
from yarl import URL

logger = logging.getLogger(__name__)


class RequestError(RuntimeError):
    """A request failed, with no credentials or response body in its message."""

    status: int | None
    cloudflare: bool

    def __init__(
        self, reason: str, *, status: int | None = None, cloudflare: bool = False
    ) -> None:
        self.status = status
        self.cloudflare = cloudflare
        super().__init__(reason)


@dataclasses.dataclass(frozen=True, slots=True)
class Response:
    status: int
    real_url: URL
    body: bytes
    encoding: str = "utf-8"

    async def read(self) -> bytes:
        return self.body

    async def text(self) -> str:
        return self.body.decode(self.encoding)

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise RequestError("Forum request failed", status=self.status)


class _Cookie(pydantic.BaseModel, frozen=True):
    name: str
    value: str


class _Solution(pydantic.BaseModel, frozen=True):
    status: int
    url: pydantic.AnyHttpUrl
    response: str
    cookies: tuple[_Cookie, ...] = ()


class _Reply(pydantic.BaseModel, frozen=True):
    status: Literal["ok", "error"]
    message: str = ""
    session: str | None = None
    sessions: tuple[str, ...] | None = None
    solution: _Solution | None = None


class _Proxy(TypedDict):
    url: str
    username: NotRequired[str]
    password: NotRequired[str]


class _BrowserCookie(TypedDict):
    name: str
    value: str
    expiry: NotRequired[int]


class _Command(TypedDict):
    cmd: str
    session: NotRequired[str]
    maxTimeout: NotRequired[int]
    proxy: NotRequired[_Proxy]
    url: NotRequired[str]
    postData: NotRequired[str]
    cookies: NotRequired[list[_BrowserCookie]]


def _proxy_config(url: str) -> _Proxy:
    try:
        parts = urlsplit(url)
        host, port = parts.hostname, parts.port
        if parts.scheme not in ("http", "socks4", "socks5") or not host or not port:
            raise RequestError("F95_PROXY must be an HTTP or SOCKS URL with a host and port")
        authority = f"[{host}]:{port}" if ":" in host else f"{host}:{port}"
        proxy: _Proxy = {"url": f"{parts.scheme}://{authority}"}
        if parts.username is not None:
            proxy["username"] = unquote(parts.username)
        if parts.password is not None:
            proxy["password"] = unquote(parts.password)
        return proxy
    except ValueError:
        raise RequestError("F95_PROXY contains an invalid proxy address") from None


class Session:
    """Own one HTTP client and, when configured, one serialized browser session."""

    def __init__(
        self, http: aiohttp.ClientSession, solver_url: str | None,
        proxy: _Proxy | None, solver_timeout: int,
    ) -> None:
        self._http: aiohttp.ClientSession = http
        self._endpoint: str | None = solver_url.rstrip("/") + "/v1" if solver_url else None
        self._proxy: _Proxy | None = proxy
        self._timeout: int = solver_timeout * 1000
        self._browser_id: str = "f95checker-" + uuid.uuid4().hex
        self._started: bool = False
        self._lock: anyio.Lock = anyio.Lock()
        self._cookies: dict[str, str] = {}
        self._pending: dict[str, _BrowserCookie] = {}

    async def start(self) -> None:
        if self._endpoint is not None:
            command: _Command = {
                "cmd": "sessions.create", "session": self._browser_id,
                "maxTimeout": self._timeout,
            }
            if self._proxy is not None:
                command["proxy"] = self._proxy
            self._started = True
            reply = await self._call(command)
            if reply.session != self._browser_id:
                raise RequestError("FlareSolverr returned an invalid session identifier")

    async def close(self) -> None:
        if self._started:
            try:
                with anyio.fail_after(10, shield=True):
                    async with self._lock:
                        _ = await self._call({"cmd": "sessions.destroy", "session": self._browser_id})
            except (RequestError, aiohttp.ClientError, TimeoutError):
                logger.warning("Could not close the FlareSolverr browser session")
            self._started = False

    def cookie(self, name: str, url: str) -> str | None:
        if self._endpoint is not None:
            return self._cookies.get(name)
        cookie = self._http.cookie_jar.filter_cookies(URL(url)).get(name)
        return cookie.value if cookie is not None else None

    async def clear_auth(self) -> None:
        """Clear forum login cookies, retaining independent Cloudflare clearance."""
        async with self._lock:
            if self._endpoint is None:
                self._http.cookie_jar.clear(lambda cookie: cookie.key.startswith("xf_"))
            else:
                for name in tuple(self._cookies):
                    if name.startswith("xf_"):
                        self._pending[name] = {"name": name, "value": "", "expiry": 1}
                        del self._cookies[name]

    async def _call(self, command: _Command) -> _Reply:
        assert self._endpoint is not None
        async with self._http.post(self._endpoint, json=command) as response:
            try:
                reply = _Reply.model_validate_json(await response.read())
            except pydantic.ValidationError:
                raise RequestError("FlareSolverr returned an invalid API response") from None
            match reply.status:
                case "error":
                    message = reply.message.lower()
                    blocked = "timeout after" in message or "cloudflare has blocked" in message
                    reason = (
                        "FlareSolverr timed out while processing the forum page/challenge"
                        if "timeout after" in message
                        else "FlareSolverr could not complete the request"
                    )
                    raise RequestError(reason, cloudflare=blocked)
                case "ok":
                    if response.status >= 400:
                        raise RequestError("FlareSolverr API request failed")
                    return reply

    async def get(
        self, url: str, *, params: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> Response:
        return await self._request(url, params=params, cookies=cookies)

    async def post(self, url: str, *, data: Mapping[str, str]) -> Response:
        return await self._request(url, data=data)

    async def _request(
        self, url: str, *, params: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None, data: Mapping[str, str] | None = None,
    ) -> Response:
        if self._endpoint is None:
            try:
                async with self._http.request(
                    "GET" if data is None else "POST", url,
                    params=params, cookies=cookies, data=data,
                ) as response:
                    body = await response.read()
                    return Response(response.status, response.real_url, body, response.get_encoding())
            except (
                aiohttp_socks.ProxyError, aiohttp_socks.ProxyConnectionError,
                aiohttp_socks.ProxyTimeoutError,
            ):
                raise RequestError("Could not connect through the forum proxy") from None

        async with self._lock:
            sessions = (await self._call({"cmd": "sessions.list"})).sessions
            if sessions is None:
                raise RequestError("FlareSolverr returned no browser session list")
            if self._browser_id not in sessions:
                await self.start()
                self._cookies.clear()
                self._pending.clear()
                logger.warning("Recreated a missing FlareSolverr session with configured routing")
                if data is not None:
                    raise RequestError(
                        "FlareSolverr session was lost during login; start login again"
                    )
            command: _Command = {
                "cmd": "request.get" if data is None else "request.post",
                "session": self._browser_id, "maxTimeout": self._timeout,
                "url": str(URL(url).update_query(params)) if params else url,
            }
            if cookies:
                for name, value in cookies.items():
                    if self._cookies.get(name) != value:
                        self._pending[name] = {"name": name, "value": value}
            if data is None and self._pending:
                command["cookies"] = list(self._pending.values())
            if data is not None:
                # FlareSolverr decodes percent escapes, but not '+' as a space.
                command["postData"] = urlencode(data, quote_via=quote)
            reply = await self._call(command)
            solution = reply.solution
            if solution is None:
                raise RequestError("FlareSolverr returned no browser response")
            self._pending.clear()
            self._cookies = {cookie.name: cookie.value for cookie in solution.cookies}
            text = solution.response
            document = bs4.BeautifulSoup(text, "lxml")
            pre = soupsieve.select_one("body > pre", document)
            if pre is not None and document.body is not None:
                content = pre.get_text()
                if (
                    content.lstrip().startswith(("{", "["))
                    and document.body.get_text().strip() == content.strip()
                ):
                    text = content
            return Response(solution.status, URL(str(solution.url)), text.encode())


@contextlib.asynccontextmanager
async def lifespan(
    *, proxy_url: str | None, solver_url: str | None, solver_timeout: int,
    user_agent: str, timeout: aiohttp.ClientTimeout,
) -> AsyncGenerator[Session, None]:
    proxy = _proxy_config(proxy_url) if proxy_url else None
    connector = None
    if solver_url:
        endpoint = URL(solver_url)
        if endpoint.scheme not in ("http", "https") or not endpoint.host:
            raise RequestError("F95_FLARESOLVERR_URL must be an HTTP or HTTPS base URL")
        timeout = aiohttp.ClientTimeout(total=solver_timeout + 10, connect=timeout.connect)
    elif proxy_url:
        connector = aiohttp_socks.ProxyConnector.from_url(proxy_url, rdns=True)
    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers={"User-Agent": user_agent},
    ) as http:
        session = Session(http, solver_url, proxy, solver_timeout)
        try:
            await session.start()
            yield session
        finally:
            await session.close()
