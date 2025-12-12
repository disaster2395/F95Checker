# F95Checker Development Commands

## Development Setup

### Install Dependencies
```bash
# Install production dependencies
pip install -U -r requirements.txt

# Install development dependencies (includes cx_Freeze for building)
pip install -U -r requirements-dev.txt
```

### Run Application
```bash
# Run from source (main entry point)
python main.py

# Run in debug mode
python main-debug.py

# Run with debug environment variable
F95DEBUG=1 python main.py
```

## Building Executables

### Build for Current Platform
```bash
# Build executable using cx_Freeze
python setup.py build

# Build macOS app bundle
python setup.py bdist_mac

# Build browser extensions
python setup.py browser
```

### Platform-Specific Build Commands
```bash
# Windows
python setup.py build
# Output: build/exe.win-amd64-*/ (contains F95Checker.exe)

# Linux  
python setup.py build
# Output: build/exe.linux-x86_64-*/ (contains F95Checker)

# macOS
python setup.py bdist_mac
# Output: build/*.app/ (F95Checker.app)
```

## Git and Version Control

### Standard Git Commands (Windows)
```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/your-feature-name

# Switch branches
git checkout main
```

### Build Trigger
```bash
# Trigger CI build (include +BUILD in commit message)
git commit -m "Your changes +BUILD"
git push origin main
```

## Development Utilities

### Python Environment
```bash
# Check Python version (requires 3.11+)
python --version

# Install/update pip
python -m pip install --upgrade pip

# List installed packages
pip list

# Show package info
pip show package-name
```

### File Operations (Windows)
```bash
# List directory contents
dir

# Navigate directories
cd C:\path\to\project

# Find files
dir /s *.py

# Search in files
findstr /R /N "search_term" *.py
```

### Archive Operations
```bash
# 7-Zip commands (if available)
7z a archive.7z folder/
7z x archive.7z

# Extract with Python
python -c "import py7zr; py7zr.SevenZipFile('archive.7z').extractall()"
```

## Debugging and Testing

### Debug Mode
```bash
# Enable debug logging
set F95DEBUG=1
python main.py

# Run debug version
python main-debug.py
```

### Error Handling
```bash
# Check for unhandled exceptions
# Debug mode will pause on errors and show traceback
# Press Enter to quit after viewing error
```

### Performance Monitoring
```bash
# Monitor resource usage
# Check task manager for memory usage
# Monitor network activity during refresh operations
```

## CI/CD Commands

### GitHub Actions
```bash
# Manual workflow trigger (via GitHub web interface)
# Or push with +BUILD in commit message

# Check workflow status
# Visit: https://github.com/WillyJL/F95Checker/actions
```

### Release Process
```bash
# Create release tag
git tag v11.1.x
git push origin v11.1.x

# Create GitHub release
# This triggers automated build process
```

## Browser Extension Development

### Chrome Extension
```bash
# Package extension
python setup.py browser
# Creates: browser/chrome.zip

# Install in Chrome
# 1. Open chrome://extensions/
# 2. Enable Developer mode
# 3. Drag chrome.zip into page
```

### Firefox Extension
```bash
# Package extension  
python setup.py browser
# Creates: browser/firefox.zip

# Install in Firefox
# 1. Visit about:debugging
# 2. Load Temporary Add-on
# 3. Select manifest.json from firefox folder
```

## Database Operations

### SQLite3 Commands
```bash
# Open database
sqlite3 %APPDATA%\f95checker\db.sqlite3

# Common SQLite commands
.tables
.schema table_name
SELECT * FROM table_name LIMIT 10;
.quit
```

### Data Migration
```bash
# Legacy config migration happens automatically on startup
# Old files: f95checker.json, config.ini
# New format: db.sqlite3
```

## Platform-Specific Commands

### Windows
```bash
# Check Windows version
winver

# Registry operations (if needed)
reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# PowerShell commands
Get-Process python*
Get-EventLog -LogName Application -Source "F95Checker"
```

### Linux
```bash
# Check Linux distribution
lsb_release -a

# Package management (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip

# Desktop integration
xdg-mime query default x-scheme-handler/http
```

### macOS
```bash
# Check macOS version
sw_vers

# Remove quarantine attribute (if needed)
xattr -d com.apple.quarantine F95Checker.app

# Launch services
launchctl list | grep f95checker
```