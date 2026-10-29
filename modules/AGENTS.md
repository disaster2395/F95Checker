# DESKTOP RUNTIME

## OVERVIEW
Desktop application subsystems; score 9: code ratio 2, symbol density 2, imported surface 2, reference centrality 3.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Render loop, list/grid/kanban | `gui.py:MainGUI` | Largest file; UI state and drawing live together |
| Forum login, refresh, downloads | `api.py` | Sessions, rate limits, checks, and updater |
| SQLite schema and persistence | `db.py` | `connect`, `create_table`, `load`, and save loop |
| Runtime state and data paths | `globals.py` | OS detection, settings, games, browser discovery |
| User actions and launching | `callbacks.py` | Connects UI operations to persistence and platform work |
| Browser RPC | `rpc_thread.py` | HTTP endpoint handlers and origin policy |
| Embedded browser | `webview.py` | Qt process and QWebChannel RPC proxy |
| Notification subprocess | `notification_proc.py` | Parent lifecycle and daemon entry |
| Runtime compatibility patches | `patches.py` | Applied by `main._start()` before normal initialization |
| Wine/Proton launch support | `wine.py` | Platform-specific launch integration |
| RPDL downloads | `rpdl.py` | Torrent integration |

## CONVENTIONS
- `globals.py` is runtime state, not a side-effect-free constants module.
- Its repeated `_()` initialization functions intentionally stage platform setup.
- Local imports break real cycles between GUI, state, models, API, and persistence.
- `db.setup()` blocks on async connect/load before the GUI is constructed.
- Its context exit cancels periodic saving and closes the database.
- `api.setup()`, notification setup, and RPC setup also own resource lifetimes.
- Async work is scheduled through `external.async_thread`; the GUI loop stays on its own thread.
- Qt webviews and notifications have subprocess entry paths in root `main.py`.
- Browser-visible RPC changes span this directory and root `browser/`.

## ANTI-PATTERNS
- Do not move Qt webviews into an ordinary worker thread: startup explicitly uses a subprocess.
- Do not treat daemon command-line markers as independent executables; they reuse `main.py`.
- Do not flatten staged imports without checking startup and circular dependencies.
- Do not assume a model field change is isolated to UI: check SQLite schema/load/save conversion.
- Do not bypass RPC origin handling when adding browser-facing endpoints.
