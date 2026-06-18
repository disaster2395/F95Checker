# F95Checker — Code Conventions

## Python Style
- Modern Python 3.11+: use `|` unions, dataclasses with `slots=True` where appropriate.
- Deferred imports: heavy or circular imports are placed inside functions, not at top level.
- No formal linter/formatter config; style is implicit in existing code.
- Type hints are used but not enforced by a checker.

## Naming
- Modules use `snake_case`.
- Classes use `PascalCase`.
- Functions/variables use `snake_case`.
- Constants at module level use `UPPER_CASE`.

## JavaScript (Browser Extension)
- `browser/integrated.js` is reinjected at runtime.
- **Use top-level `var` only** — `const`/`let` cause SyntaxError on re-injection.

## Architecture Patterns
- Desktop app uses subprocesses for Qt webviews (`webview-daemon`) and notifications (`notification-daemon`) because Qt and desktop-notifier don't handle threading well.
- RPC over localhost HTTP (`127.0.0.1:57095`) for browser extension communication.
- SQLite database with manual migration logic in `modules/db.py`.
- Async thread wrapper in `external/async_thread.py` to bridge sync and async code.

## Design Patterns
- Globals module (`modules/globals.py`) holds runtime mutable state.
- Context managers for setup/teardown of subsystems (`db.setup()`, `api.setup()`, etc.).
- Patches applied early via `modules/patches.py`.

## Version / Meta
- `common/meta.py` holds `version`, `release`, `build_number`, `frozen`, `debug`, `self_path`.
- `version` is modified at import time via `mod_version()` (increments patch by 1).
- `release = False` in source; CI flips to `True` for builds.
