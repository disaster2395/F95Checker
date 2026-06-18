# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-18
**Commit:** a4ed1aa
**Branch:** custom-changes-2

## OVERVIEW
F95Checker is a cross-platform desktop library manager and update checker for F95zone games. Built with Python 3.11+ using PyQt6 + PyOpenGL + glfw + Dear ImGui for the native UI, plus a companion FastAPI cache indexer and a WebExtension browser addon.

## STRUCTURE
```
.
├── browser/          # WebExtension source (Chrome + Firefox)
├── common/           # Shared types, parsers, metadata
├── external/         # Vendored helpers (async/sync threads, image, zip, etc.)
├── indexer/          # FastAPI cache API service (F95Indexer)
├── modules/          # Core desktop app logic
├── resources/        # Fonts and icons
├── main.py           # Desktop app entrypoint
├── indexer-main.py   # FastAPI/uvicorn server entrypoint
└── setup.py          # cx_Freeze build + browser extension packager
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add/modify UI | modules/gui.py | 5571-line ImGui/Qt shell; most complex file |
| API client / refresh | modules/api.py | HTTP session, ratelimiter, thread data fetching |
| Database schema | modules/db.py | SQLite persistence, migrations |
| Browser extension | browser/ | manifest v3/v2 + extension.js + integrated.js |
| Cache API / indexer | indexer/ | FastAPI service scraping F95zone |
| Shared types | common/structs.py | Dataclasses, enums, pipe structs |
| Build / packaging | setup.py | cx_Freeze executables and custom commands |

## CODE MAP

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| MainGUI | class | modules/gui.py | Central | Desktop UI shell and event loop |
| api | module | modules/api.py | High | HTTP client, ratelimiter, refresh |
| db | module | modules/db.py | High | SQLite setup and persistence |
| globals | module | modules/globals.py | High | Runtime state, OS detection |
| webview | module | modules/webview.py | Med | Qt WebEngine wrapper |
| notification_proc | module | modules/notification_proc.py | Med | Notification subprocess bridge |
| rpc_thread | module | modules/rpc_thread.py | Med | Browser extension localhost RPC |
| callbacks | module | modules/callbacks.py | Med | UI callbacks |
| rpdl | module | modules/rpdl.py | Low | RPDL.net integration |
| structs | module | common/structs.py | High | Shared dataclasses |
| parser | module | common/parser.py | Med | Thread/page parsing |
| meta | module | common/meta.py | High | Version, paths, build flags |

## CONVENTIONS
- Deferred imports: heavy or circular imports are placed inside functions.
- Typing: modern Python 3.11+ (`|` unions, dataclasses with `slots=True`).
- JS in `browser/integrated.js`: use top-level `var` only (reinjected script; `const`/`let` cause SyntaxError on re-injection).
- `.gitattributes` enforces LF everywhere except `.bat`/`.ps1`/`.cmd`.
- No linter/formatter config; style is implicit in code.

## ANTI-PATTERNS (THIS PROJECT)
- Never call `external/cpuinfo.py` functions directly that warn they can crash the Python runtime; use the safe wrapper.
- Do not place app install files inside the app data directory (or symlink app data into install files); will cause irreversible data loss on update (see modules/db.py).
- `modules/gui.py` contains documented HACKs for ImGui limitations (text wrapping, column toggles, sort specs); treat as fragile.

## UNIQUE STYLES
- Desktop app uses Dear ImGui over OpenGL via PyOpenGL/glfw, not a standard web/Electron stack.
- UI subprocesses: webviews and notifications run as separate processes (`webview-daemon`, `notification-daemon`) because Qt and desktop-notifier don't handle threading well.
- Build triggers on commit messages containing `+ BUILD`.
- CI rewrites `common/meta.py` with `sed` to flip `release = True` and inject build numbers.

## COMMANDS
```bash
# Run from source
pip3 install -U -r requirements.txt
python3 main.py

# Build desktop binaries
python setup.py build               # Windows/Linux
python setup.py bdist_mac           # macOS

# Build browser extension zips
python setup.py browser             # or python setup.py extension
```

## NOTES
- No automated test suite is committed to the repo.
- `build/`, `__pycache__/`, and `.venv/` are present in-repo (not gitignored cleanly).
- The repo mixes three distinct deliverables in one tree: desktop app, browser extension, and FastAPI indexer service.
