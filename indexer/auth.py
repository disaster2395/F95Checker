import binascii
from typing import ClassVar

import aiohttp
import pydantic
import pyotp
import soupsieve

from common import parser
from indexer import transport


class _LoginHTML(pydantic.BaseModel):
    model_config: ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(frozen=True)
    content: str


class _LoginForm(pydantic.BaseModel):
    model_config: ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(frozen=True)
    html: _LoginHTML


class LoginError(RuntimeError):
    """Authentication failed without exposing credentials or response bodies."""

    reason: str

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def _csrf(html: str, selector: str, attribute: str = "value") -> str:
    element = soupsieve.select_one(selector, parser.html(html))
    value = element.get(attribute) if element is not None else None
    if not isinstance(value, str) or not value:
        raise LoginError("F95zone login page is missing a CSRF token")
    return value


async def login(
    session: transport.Session,
    host: str,
    username: str,
    password: str,
    totp_secret: str = "",
) -> str:
    """Log in using the XenForo form and retain cookies in the shared session."""
    try:
        response = await session.get(host)
        response.raise_for_status()
        initial_csrf = _csrf(await response.text(), "[data-csrf]", "data-csrf")

        response = await session.get(
            f"{host}/login/",
            params={
                "_xfRequestUri": "/",
                "_xfWithData": "1",
                "_xfToken": initial_csrf,
                "_xfResponseType": "json",
            },
        )
        response.raise_for_status()
        try:
            form = _LoginForm.model_validate_json(await response.read())
        except pydantic.ValidationError:
            raise LoginError("F95zone returned an invalid login form") from None
        form_csrf = _csrf(form.html.content, 'input[name="_xfToken"]')

        response = await session.post(
            f"{host}/login/login",
            data={
                "login": username,
                "password": password,
                "remember": "1",
                "_xfToken": form_csrf,
                "_xfRedirect": host,
            },
        )
        response.raise_for_status()
        result = await response.text()

        two_step_selector = 'form[action="/login/two-step"]'
        if soupsieve.select_one(two_step_selector, parser.html(result)) is not None:
            if not totp_secret:
                raise LoginError("F95zone requires two-factor login; set F95_TOTP_SECRET")
            try:
                code = pyotp.TOTP(totp_secret).now()
            except (binascii.Error, ValueError):
                raise LoginError("F95_TOTP_SECRET must be a valid Base32 secret") from None
            two_step_csrf = _csrf(
                result, f'{two_step_selector} input[name="_xfToken"]'
            )
            response = await session.post(
                f"{host}/login/two-step",
                data={
                    "code": code,
                    "_xfToken": two_step_csrf,
                    "trust": "1",
                    "remember": "1",
                    "confirm": "1",
                    "provider": "totp",
                },
            )
            response.raise_for_status()
            result = await response.text()
            if soupsieve.select_one(two_step_selector, parser.html(result)) is not None:
                raise LoginError("F95zone rejected the two-factor login")

        cookie = session.cookie("xf_user", host)
        if not cookie:
            raise LoginError(
                "F95zone login failed; check credentials and account challenges"
            )
        return cookie
    except transport.RequestError as exc:
        if exc.status is not None:
            raise LoginError(f"F95zone login request failed (HTTP {exc.status})") from None
        raise
    except (aiohttp.ClientError, TimeoutError):
        raise LoginError("Could not complete the F95zone login request") from None
