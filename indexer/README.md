# Indexer

## GitLab image builds

The existing desktop pipeline includes the isolated `.gitlab/indexer.yml` job.
`build::indexer` runs on the `customized` branch and builds the root `Dockerfile`
for `linux/amd64` and `linux/arm64`, using Docker-in-Docker and Buildx.
It publishes exactly two tags to the project's GitLab Container Registry:

- `$CI_REGISTRY_IMAGE:yyyymmdd-shortsha`: UTC build date and `CI_COMMIT_SHORT_SHA`.
- `$CI_REGISTRY_IMAGE:latest`.

Registry authentication uses the job's predefined `CI_REGISTRY_USER` and
`CI_REGISTRY_PASSWORD`; no registry password belongs in the repository.
The job uses Docker 29.0.2 from `registry.nexus.blackopdev.com` and the
`DIND_DNS`/`DIND_DNS_EFFECTIVE` variables, defaulting to upstream DNS `1.0.0.1`.
It needs a runner tagged `docker` with privileged DinD enabled and support for
the two target architectures (native workers or configured emulation).
Existing desktop build, package and deploy jobs are unchanged.

## Docker Compose

From the repository root, copy `indexer.env-example` to `indexer.env`.
Configure either `COOKIE_XF_USER` or the automatic login credentials described
below so the indexer can fetch forum threads. Optionally set `REDIS_PASSWORD`.

### Production: prebuilt image

Set `INDEXER_IMAGE` in `indexer.env` to the full published registry reference,
using either `latest` or a dated commit tag. The repository prefix is the value
of `CI_REGISTRY_IMAGE` shown in the GitLab build job/Container Registry.
Authenticate with `docker login` to that registry if it is private.
The production file has no local build; it always pulls the selected indexer image.

```sh
docker compose --env-file indexer.env up -d
docker compose --env-file indexer.env logs -f indexer
```

Run `up -d` again to pull an updated `latest` image and recreate the indexer
when its image changes. To pin a build, set `INDEXER_IMAGE` to its dated tag.

### Development: local build

The original local-build configuration is retained as `docker-compose.dev.yml`.
It does not require `INDEXER_IMAGE`.

```sh
docker compose -f docker-compose.dev.yml --env-file indexer.env up --build -d
docker compose -f docker-compose.dev.yml --env-file indexer.env logs -f indexer
```

### Shared services and data

The API is available at `http://localhost:8069`. For example,
`GET /fast?ids=` returns an empty JSON object without fetching forum threads.
Set `BIND_PORT` in `indexer.env` to change the published host port.
Compose always uses `redis:6379`, the `default` Redis user, and port 8069
inside the indexer container. It passes the same `REDIS_PASSWORD` to both services.
Production keeps Redis internal; the dev configuration retains host port 6379.
Its data is persisted in the `redis-data` volume. Both Compose variants use the
same project/volume names when run from this directory, so switching between
them does not discard the cache. Both services have health checks, and the
indexer starts after Redis becomes healthy.

```sh
docker compose --env-file indexer.env down
# For the dev configuration:
docker compose -f docker-compose.dev.yml --env-file indexer.env down
```

Stopping the services keeps the cached data. Add `--volumes` to remove it.
The dev configuration can start without authentication, but fetching forum
threads still requires a valid cookie or login credentials.

## F95zone authentication

Choose either mode in `indexer.env`:

- Set `COOKIE_XF_USER` to the `xf_user` cookie of a logged-in F95zone account.
- Leave `COOKIE_XF_USER` empty and set `F95_USERNAME` (username or email) and
  `F95_PASSWORD` for automatic login. If the account uses authenticator-based
  two-factor authentication, also set `F95_TOTP_SECRET` to its Base32 secret,
  not a current six-digit code.

```dotenv
COOKIE_XF_USER=""
F95_USERNAME="your-username-or-email"
F95_PASSWORD="your-password"
F95_TOTP_SECRET=""
```

The automatic login follows the forum's CSRF-protected form and, when requested,
completes the TOTP step. Keep the host clock synchronized for TOTP.
The resulting `xf_user` cookie is stored in the same runtime variable used by
cookie-based authentication; session and two-factor cookies are retained in the
HTTP session. Credentials and generated cookies are not written to disk.

Automatic login runs on the first forum request, not during API startup.
An unsuccessful login or forum challenge is reported through the existing
`INDEX_ERROR` response instead of terminating the API process. A later request
can retry login; concurrent requests share the outcome of the same login attempt.
The `/fast?ids=` health check verifies API availability, not forum authentication.

If both modes are configured, the supplied cookie is used first. When a request
returns a login or two-factor form, the indexer performs a complete login
(including TOTP when requested), replaces the runtime cookie and retries that
request once. Concurrent failures share one login. Without credentials, the
existing `SESSION_LOGGED_OUT` behavior is preserved.
Network failures, rate limits and missing threads do not trigger logins.

Invalid credentials, missing required TOTP configuration, and unsupported
interactive challenges cause an explicit login error. They do not silently
switch the indexer to an anonymous session.

## Connection modes

Choose the transport independently of cookie or automatic login authentication:

| `F95_FLARESOLVERR_URL` | `F95_PROXY` | Forum connection |
| --- | --- | --- |
| Empty | Empty | Native direct connection |
| Empty | Set | Native proxy connection |
| Set | Empty | FlareSolverr browser connection |
| Set | Set | FlareSolverr browser using the upstream proxy |

`F95_PROXY` routes forum traffic, including login, TOTP and session refresh,
through one upstream proxy. With FlareSolverr enabled, the proxy is passed to
the browser; indexer-to-FlareSolverr API traffic stays direct. Redis connections
are unaffected.

```dotenv
# HTTP CONNECT, without authentication:
F95_PROXY="http://proxy.example:3128"
# SOCKS5, without authentication:
F95_PROXY="socks5://proxy.example:1080"
```

Use one proxy URL. Percent-encode special characters in the
proxy username and password (for example, `@` becomes `%40`).
Native mode supports authenticated SOCKS5 and resolves destination hostnames
through the proxy. Chromium does not support authenticated SOCKS5; in browser
mode, use an HTTP relay in front of an authenticated SOCKS5 proxy instead.
In Docker, `localhost` refers to the container; use addresses reachable from the
indexer, or from FlareSolverr for the browser's upstream proxy.

### FlareSolverr

Set `F95_FLARESOLVERR_URL` to a base URL, without `/v1`. To use the external
solver supplied for testing:

```dotenv
F95_FLARESOLVERR_URL="http://192.168.2.6:8191"
F95_FLARESOLVERR_TIMEOUT=60
```

Start the indexer with the ordinary Compose command above. An external solver
does not require the local profile. To run the bundled solver instead, set
`F95_FLARESOLVERR_URL="http://flaresolverr:8191"` and start:

```sh
docker compose --env-file indexer.env --profile flaresolverr up -d
# For local builds:
docker compose -f docker-compose.dev.yml --env-file indexer.env --profile flaresolverr up --build -d
```

The optional profile uses `ghcr.io/flaresolverr/flaresolverr:v3.5.2`, with
`HEADLESS=false` under `xvfb-run`, `LOG_LEVEL=warning` and `LOG_HTML=false`.
Chromium uses a virtual display inside the container, not an external desktop.
It publishes no host port; the indexer
reaches it over the Compose network. It is not a required dependency for native
direct or proxy modes. Enabling the profile alone does not select browser mode:
the URL must also be configured.

Browser mode keeps a persistent browser session for cookies and serializes
requests through that session, including authentication. Restarting the
indexer or solver can require a new session and login. Before each browser
request, the indexer checks `sessions.list` and explicitly recreates a missing
session with the configured proxy. A supplied `xf_user` cookie is reapplied on
the next GET. If a session disappears during login, the pending POST is not
submitted; a later login starts again with a fresh CSRF flow.

FlareSolverr 3.5.2 ignores request-level `proxy` when `session` is set, including
when it implicitly recreates a missing session. Its `session_ttl_minutes`
rotation also loses the session proxy, so the indexer does not enable that TTL.
The existence check and navigation are separate API calls: a solver restart
between them can still trigger that upstream behavior. An atomic routing
guarantee requires a FlareSolverr-side fix, not another client-side proxy field.

JSON endpoints may arrive
as HTML-wrapped JSON; the transport normalizes these responses before parsing.
`F95_FLARESOLVERR_TIMEOUT` is an integer request timeout in seconds, defaulting
to `60`. An unavailable solver, timeout or solver error is reported as a request
failure rather than silently switching transport. FlareSolverr cannot guarantee
challenge bypass, and interactive challenges can still prevent login or fetching.
The origin status is only what the solver reports, often `200`; response-body
classification remains authoritative for login, challenge and missing-thread
pages.

### User-Agent

`F95_USER_AGENT` overrides the HTTP User-Agent in native direct and proxy modes.
Leave it empty to retain the generated `F95Indexer/...` value.

In browser mode the forum sees Chromium's own User-Agent, not the indexer's
header on RPC calls to FlareSolverr. Version 3.5.2 does not support overriding
the browser through the request `userAgent` or `headers` fields. The indexer
ignores `F95_USER_AGENT` in browser mode and logs a warning if it is set.
Changing a native User-Agent alone does not reproduce Chromium's TLS or
JavaScript behavior and does not guarantee passing Cloudflare.

## Code layout

- `client.py` owns configuration, the shared login cookie and authentication retries.
- `auth.py` implements the CSRF/password/TOTP login flow.
- `transport.py` implements native HTTP and the FlareSolverr API adapter.

The existing `f95zone.py` contains only the integration in `lifespan()` and error
classification. The original request call sites in `scraper.py` and `watcher.py`
remain unchanged to reduce upstream merge conflicts.

## Standalone container

```sh
docker build -t f95checker-indexer .
docker run --rm --env-file indexer.env -e BIND_HOST=0.0.0.0 -p 8069:8069 f95checker-indexer
```

For this mode, set `REDIS_HOST` to a Redis server reachable from the container
(`localhost` would refer to the container itself). No desktop dependencies
are needed.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `INDEXER_IMAGE` | Empty | Required by production Compose: full published registry image reference; unused by dev Compose |
| `COOKIE_XF_USER` | Empty | F95zone session cookie |
| `F95_USERNAME` | Empty | Username or email for automatic login |
| `F95_PASSWORD` | Empty | Password for automatic login |
| `F95_TOTP_SECRET` | Empty | Base32 authenticator secret, if the account requires TOTP |
| `F95_PROXY` | Empty | HTTP CONNECT or SOCKS5 proxy URL, with optional credentials |
| `F95_USER_AGENT` | Generated `F95Indexer/...` | Native HTTP User-Agent override; ignored in browser mode |
| `F95_FLARESOLVERR_URL` | Empty | FlareSolverr base URL; empty selects native transport |
| `F95_FLARESOLVERR_TIMEOUT` | `60` | FlareSolverr request timeout in integer seconds |
| `BIND_HOST` | `127.0.0.1` locally, `0.0.0.0` in Docker | API listening address |
| `BIND_PORT` | `8069` | API listening port; published host port in Compose |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_USERNAME` | Unset | Redis ACL username, if required |
| `REDIS_PASSWORD` | Unset | Redis password, if required |

An empty username or password means no corresponding authentication parameter.
Custom ACL usernames require a Redis server with that user configured; the
bundled Compose service uses the `default` user.
The Docker build includes only the indexer and its required source files,
not environment files or credentials.

## Background cache refresh

Both update watchers enqueue existing threads after invalidating their cache.
A separate async worker refreshes them without making the polling tasks wait for
scraping. Duplicate queued IDs are coalesced, and watcher updates take priority
over periodic expired-cache work. Refreshes share the API's per-thread locks,
freshness checks and error retry deadlines.

The indexer also scans existing cached threads at startup and periodically,
refreshing only expired or invalidated entries. Set `CACHE_REFRESH_INTERVAL`
to a positive integer number of seconds (default `86400`, one day).
Both Compose variants pass this setting through. This is the scan interval,
not the cache TTL: successful data still uses the existing seven-day TTL
(two days when relying on a parsed thread version).

On a version change, the forum's parsed update date is used when it is positive,
not older than the cached date and not beyond today's UTC date. Otherwise the
indexer uses today's date. Dates are normalized to UTC noon, so today's noon
is accepted even before noon. Without a version change, the previous update
date is preserved. `LAST_CHANGE` remains the time the cache change was recorded
for client update detection.
