# F95Checker — Project Core

## Overview
Cross-platform desktop library manager and update checker for F95zone games. Three deliverables in one repo:
- **Desktop app**: Python 3.11+ with PyQt6 + PyOpenGL + glfw + Dear ImGui native UI
- **Indexer**: FastAPI cache API service (`api.f95checker.dev`) scraping F95zone
- **Browser extension**: Chrome + Firefox WebExtension companion

## Source Map

### Desktop App
- `main.py` — entrypoint, singleton lock, subprocess routing (webview-daemon, notification-daemon)
- `modules/gui.py` — 5500+ line ImGui/Qt shell; most complex file; contains documented HACKs for ImGui limitations
- `modules/api.py` — HTTP client, ratelimiter, refresh logic
- `modules/db.py` — SQLite persistence, migrations
- `modules/globals.py` — runtime state, OS detection
- `modules/webview.py` — Qt WebEngine wrapper (runs as subprocess)
- `modules/notification_proc.py` — notification subprocess bridge
- `modules/rpc_thread.py` — browser extension localhost RPC
- `modules/callbacks.py` — UI callbacks
- `modules/rpdl.py` — RPDL.net integration

### Shared
- `common/structs.py` — dataclasses, enums, pipe structs
- `common/parser.py` — thread/page parsing
- `common/meta.py` — version, paths, build flags

### Browser Extension
- `browser/` — manifest v3/v2, extension.js, integrated.js
- `setup.py` has `browser`/`extension` command to pack chrome.zip / firefox.zip

### Indexer Service
- `indexer-main.py` — FastAPI/uvicorn server entrypoint
- `indexer/` — cache, scraper, watcher, f95zone client, thread routes

### External / Vendored
- `external/` — async/sync threads, image helpers, zip utils, cpuinfo (unsafe; use safe wrapper only)

## Project-Wide Invariants
- **Never** call `external/cpuinfo.py` functions directly (can crash Python runtime); use safe wrapper.
- Do not place app install files inside app data directory (or symlink app data into install files); causes irreversible data loss on update (see `modules/db.py`).
- `modules/gui.py` contains documented HACKs for ImGui limitations (text wrapping, column toggles, sort specs); treat as fragile.
- JS in `browser/integrated.js`: use top-level `var` only (reinjected script; `const`/`let` cause SyntaxError on re-injection).
- `.gitattributes` enforces LF everywhere except `.bat`/`.ps1`/`.cmd`.
- No automated test suite committed.
- Build triggers on commit messages containing `+ BUILD`.
- CI rewrites `common/meta.py` with `sed` to flip `release = True` and inject build numbers.

## Data Storage Paths
- Windows: `%APPDATA%\f95checker\` (usually `C:\Users\<user>\AppData\Roaming\f95checker\`)
- Linux: `~/.config/f95checker/`
- macOS: `~/Library/Application Support/f95checker/`
- Database: `db.sqlite3` in the above directory
- Images: `images/thread-id.ext` in the same directory
- Legacy configs (`f95checker.json`, `config.ini`) are migrated on startup and ignored afterwards

## References
- Tech stack and dependencies: `mem:tech_stack`
- Commands to run: `mem:suggested_commands`
- Code conventions: `mem:conventions`
- Task completion checklist: `mem:task_completion`
