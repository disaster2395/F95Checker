# F95Checker — Tech Stack

## Desktop App
- **Language**: Python 3.11+ (uses `|` unions, dataclasses with `slots=True`)
- **UI Framework**: Dear ImGui via `imgui==2.0.0` over OpenGL via `PyOpenGL==3.1.7` + `glfw==2.8.0`
- **Qt Shell**: `PyQt6==6.7.1` (Win/Linux), `PyQt6==6.4.2` (macOS); `PyQt6-WebEngine` for webviews
- **Notifications**: `desktop-notifier==6.0.0` + platform-specific winrt packages on Windows
- **Async**: `aiohttp==3.11.11`, `aiolimiter==1.2.0`, `aiosqlite==0.20.0`, `aiofiles==24.1.0`
- **Optional event loop**: `uvloop==0.21.0` on non-Windows
- **Archive extraction**: `py7zr==0.22.0`, `rarfile==4.2`, `zipfile-deflate64`
- **Parsing**: `beautifulsoup4==4.12.3`, `lxml==5.3.0`
- **Images**: `pillow==11.0.0`, `pillow-avif-plugin==1.4.6`
- **Other**: `bencode2==0.3.17`, `zstd==1.5.6.2`, `python-dateutil==2.9.0.post0`, `python-socks[asyncio]==2.5.3`, `aiohttp-socks==0.9.1`
- **Windows-only**: `pywin32==308`, multiple `winrt-*==2.3.0` packages
- **macOS-only**: `rubicon-objc==0.5.0`

## Indexer Service
- **Framework**: `fastapi==0.115.5` + `uvicorn[standard]==0.32.1`
- **Cache**: `redis[hiredis]==5.2.0`
- **Scraping**: same `aiohttp`, `aiolimiter`, `beautifulsoup4`, `lxml` as desktop

## Build / Packaging
- **Freezer**: `cx-Freeze==7.0.0`
- **Build tool**: `setuptools==69.5.1`
- `setup.py` defines two executables: `F95Checker` (gui base) and `F95Checker-Debug` (console base)

## Browser Extension
- Manifest v3 (Chrome) and v2 (Firefox)
- Injected script `browser/integrated.js` must use top-level `var` only

## Package Management
- `requirements.txt` — runtime deps for desktop app
- `requirements-dev.txt` — includes `requirements.txt` + `cx-Freeze`, `setuptools`
- `requirements-indexer.txt` — FastAPI/uvicorn/redis for indexer service
- No lockfile (pip freeze not committed).
