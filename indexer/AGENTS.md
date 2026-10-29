# INDEXER SERVICE

## OVERVIEW
Redis-backed forum indexing service; score 9: code ratio 2, symbol density 2, imported surface 2, reference centrality 3.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Server startup and lifecycle | `../indexer-main.py` | Composes cache, forum, and watcher lifespans |
| Public API | `threads.py` | `/fast`, `/full/{id}`, `/raw/{id}` |
| Cache shape and expiration | `cache.py` | Redis keys, locks, last-change metadata |
| Thread data acquisition | `scraper.py` | Fetches and invokes shared parser |
| Polling and invalidation | `watcher.py` | Background forum updates/version checking |
| Forum errors and constants | `f95zone.py` | Body classification and error flags |
| Shared authenticated requests | `client.py` | Login coordination and request retry |
| Login, CSRF, TOTP | `auth.py` | Authentication flow |
| Native/proxy/browser transport | `transport.py` | FlareSolverr session and response adaptation |
| Deployment/auth configuration | `README.md`, `../indexer.env-example` | Full operational contracts |

## CONVENTIONS
- Runtime configuration lives in root `indexer.env`; the example documents variable names.
- Uvicorn runs one worker; cache/forum/watcher resources belong to async lifespans.
- `/fast` accepts at most 10 comma-separated IDs; valid IDs are 1 through 999999.
- `/full/{id}` requires `ts` and rejects future timestamps with 406.
- `/raw/{id}` permits stale cached data.
- Missing threads produce 404; other cached index errors produce 500.
- Empty `/fast?ids=` checks API availability, not successful forum authentication.
- Automatic login is lazy; concurrent requests share one login attempt.
- Login retries apply to login/two-factor forms, not every network or forum failure.
- FlareSolverr traffic is serialized through a persistent browser session.
- Shared parsing lives in `../common/parser.py`, not a second service-only parser.

## ANTI-PATTERNS
- Preserve original request call sites in `scraper.py` and `watcher.py`; the README names upstream merge compatibility as the reason.
- Do not write credentials or generated cookies to disk; authentication state is in memory.
- Do not silently fall back to anonymous authentication or another transport on failure.
- Do not enable FlareSolverr `session_ttl_minutes`: documented session rotation loses proxy configuration.
- Do not treat the solver's HTTP status alone as authoritative; classify the response body.
- Do not confuse production Compose's prebuilt image with the development local build.
