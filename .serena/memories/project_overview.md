# F95Checker Project Overview

## Project Purpose
F95Checker is an update checker and library tool for (NSFW) games on the F95zone platform. It helps users track game updates, manage their game library, and stay informed about new releases and changes.

## Key Features
- Blazing fast™ and reliable update checking
- Cross-platform support (Windows, Linux, macOS)
- Beautiful and customizable interface with multiple view modes (compact list, grid, kanban)
- 2FA account support
- Alert and inbox checking
- Track installed and played versions
- Launch games directly from the tool
- Custom labels and organization
- Archive games to temporarily mute updates
- Comprehensive game details tracking (name, version, developer, status, etc.)
- Sorting and filtering capabilities
- Browser extension for easy game adding
- Background mode with desktop notifications
- Auto-updating (tool itself, not games)

## Tech Stack
- **Language**: Python 3.11+
- **GUI Framework**: imgui (Dear ImGui) with PyOpenGL and glfw
- **Web Engine**: PyQt6 WebEngine (different versions for different platforms)
- **Async Framework**: asyncio with uvloop (non-Windows), aiohttp, aiosqlite
- **Database**: SQLite3
- **Web Scraping**: BeautifulSoup4, lxml
- **Image Processing**: Pillow with AVIF plugin support
- **Archive Support**: py7zr, rarfile, zipfile-deflate64
- **Notifications**: desktop-notifier with platform-specific implementations
- **Build System**: cx_Freeze for creating executables
- **Proxy Support**: python-socks, aiohttp-socks

## Architecture
- **Main Entry**: `main.py` (with `main-debug.py` for debugging)
- **Module Structure**:
  - `modules/`: Core application logic
  - `common/`: Shared utilities and data structures
  - `external/`: Third-party integrations and custom implementations
- **Cross-platform compatibility** with platform-specific optimizations
- **Singleton pattern** to prevent multiple instances
- **Subprocess handling** for webviews and notifications
- **Async/await patterns** throughout for performance

## Data Storage
- **Database**: SQLite3 at platform-specific paths:
  - Windows: `%APPDATA%\f95checker\db.sqlite3`
  - Linux: `~/.config/f95checker/db.sqlite3`
  - macOS: `~/Library/Application Support/f95checker/db.sqlite3`
- **Images**: Stored as `thread-id.ext` in images folder
- **Settings**: imgui.ini for interface preferences
- **Legacy configs**: f95checker.json and config.ini (migrated on startup)

## Browser Extension
- **Chrome**: Packaged as chrome.zip, drag-and-drop installation
- **Firefox**: Available on AMO (Add-ons.mozilla.org)
- **Features**: Add games by clicking extension icon, right-clicking links, or right-clicking page background
- **Integration**: Shows added games with icons on forum pages