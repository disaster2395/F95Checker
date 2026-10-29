# PROJECT KNOWLEDGE BASE

**Generated:** 2026-10-29
**Commit:** 51b1dec
**Branch:** customized

## OVERVIEW
F95Checker is a cross-platform F95zone game-library/update checker with a Python desktop app, companion browser extensions, and a separate Redis-backed indexer.
The desktop uses ImGui/GLFW/OpenGL, Qt WebEngine, async networking, and SQLite; the indexer uses FastAPI/Uvicorn.

## STRUCTURE
```text
F95Checker/
|-- main.py                 # Desktop startup and subprocess dispatch
|-- main-debug.py           # Enables debug before normal startup
|-- indexer-main.py         # Independent API service entry point
|-- modules/                # Desktop runtime; scoped AGENTS.md
|-- common/                 # Shared models/parser; scoped AGENTS.md
|-- indexer/                # Backend/cache/auth; scoped AGENTS.md
|-- browser/                # Chrome, Firefox, and embedded-WebEngine variants
|-- external/               # Bundled helper code, often with upstream provenance
|-- resources/              # Fonts, icons, and packaged assets
|-- setup.py                # cx_Freeze build and extension packaging
|-- docker-compose*.yml     # Production image vs development build
`-- .github/, .gitlab/       # Desktop builds and indexer image pipeline
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Startup order or child processes | `main.py` | `_start()` dispatches; `main()` owns setup scopes |
| Desktop UI, persistence, networking | `modules/AGENTS.md` | Runtime subsystem map |
| Shared field/parser contracts | `common/AGENTS.md` | Used across desktop and service |
| Indexer behavior or deployment | `indexer/AGENTS.md`, `indexer/README.md` | Operational details stay in README |
| Browser behavior | `browser/chrome/extension.js`, `browser/firefox/extension.js` | Parallel implementations |
| Embedded browser injection | `browser/integrated.js`, `modules/webview.py` | QWebChannel instead of extension APIs |
| Extension/Desktop RPC contract | `modules/rpc_thread.py`, `common/meta.py` | Loopback HTTP, port 57095 |
| Binary packaging | `setup.py`, `.github/workflows/build.yml` | Resources, native libraries, platform workarounds |
| Backend container pipeline | `.gitlab/indexer.yml`, `Dockerfile` | Separate from desktop packaging |
| Dependency changes | `requirements*.txt` | Desktop, build tools, and indexer differ |

## CODE MAP
LSP outlines and structural import searches verified these boundaries.
Reference count is measured only where shown; `unmeasured` is not zero.

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `_start` | Function | `main.py` | unmeasured | Patches, daemon dispatch, singleton startup |
| `main` | Function | `main.py` | unmeasured | Desktop resource lifetimes and GUI loop |
| `Game` | Class | `common/structs.py:1020` | >20 | Persisted game model and UI/runtime state |
| `thread` | Function | `common/parser.py:96` | unmeasured | Shared forum HTML extraction |
| `setup` | Function | `modules/api.py:227` | unmeasured | Desktop network session lifetime |
| `f95zone` | Module | `indexer/f95zone.py` | >20 | Shared forum constants/errors/client lifetime |
| `fast_request` | Function | `indexer/threads.py:17` | unmeasured | Batched change timestamps |

## CONVENTIONS
- This is a flat Python namespace-package layout: `modules`, `common`, and `indexer` lack `__init__.py`.
- Use source-root entry points; directory names do not imply independently installed packages.
- Platform-specific dependency markers and native packaging matter; Python 3.11/3.12 is documented.
- Many `external/` helpers cite upstream gists; `cpuinfo.py` and `imgui_glfw.py` also identify upstream sources.
- No checked-in automated tests, test runner configuration, or CI test job were found.

## ANTI-PATTERNS (THIS PROJECT)
- The README excludes automatic game-update downloads and automatic game-folder management from the product.
- Keep local `*.env` values out of checked-in examples and documentation.
- Do not introduce top-level `let`/`const` into `browser/integrated.js`: reinjection can redeclare them and fail.
- Do not use Chrome extension APIs in the integrated script; Qt WebEngine invokes its functions explicitly.

## UNIQUE STYLES
- Chrome uses manifest V3 and `chrome.action`; Firefox uses manifest V2 and `chrome.browserAction`.
- Keep matching extension behavior aligned while preserving browser API/manifest differences.
- Embedded JavaScript uses QWebChannel `rpcproxy.handle`; extensions use loopback HTTP RPC.
- `browser/.prettierrc`: four-space indent, width 100, single quotes.

## COMMANDS
Run from the repository root. These are documented commands, not a test suite.
```sh
pip3 install -U -r requirements.txt
python3 main.py
python3 main-debug.py
pip install -r requirements-dev.txt
python setup.py build
python setup.py bdist_mac
python setup.py browser
docker compose -f docker-compose.dev.yml --env-file indexer.env up --build -d
docker compose --env-file indexer.env up -d
```

## NOTES
- Copy `indexer.env-example` to `indexer.env` and configure it before Compose use.
- Production Compose requires `INDEXER_IMAGE`; development Compose builds locally.
- Dev Compose exposes Redis on host port 6379; production keeps Redis internal.
- `setup.py browser` builds both extension ZIPs and copies the bundled icon font.
- Desktop GitHub push builds require `+ BUILD` in the commit message; dispatch/releases also trigger.
- The GitLab indexer image job runs on `customized` and builds amd64/arm64 images.
- Packaging pulls native components and is platform-dependent; it is not a lightweight validation command.
