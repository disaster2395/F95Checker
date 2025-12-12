# F95Checker Project-Specific Information

## Project History and Context

### Development Background
- **Creator**: WillyJL (primary developer)
- **License**: GPLv3 (GNU General Public License v3)
- **Platform**: F95zone.to gaming community
- **Purpose**: Game library management and update tracking for NSFW games
- **Community**: Active development with community contributions

### Key Contributors
- **r37r05p3C7**: Tab customization, timeline, extension features
- **littleraisins**: Features from defunct 'X' fork
- **FaceCrap**: Multiple fixes and improvements
- **blackop**: Proxy support, rate limiting fixes
- **GR3ee3N**: Optimized build workflows
- **batblue**: macOS support
- **unroot**: Linux support

## Technical Architecture Details

### Core Components
1. **Main Application** (`main.py`)
   - Entry point with singleton pattern
   - Async/await event loop setup
   - Platform-specific optimizations (uvloop on non-Windows)
   - Subprocess handling for webviews and notifications

2. **GUI System** (`modules/gui.py`)
   - Dear ImGui-based interface
   - Multiple view modes (list, grid, kanban)
   - Custom widgets and controls
   - Cross-platform rendering

3. **API Integration** (`modules/api.py`)
   - F95zone API wrapper
   - Rate limiting and caching
   - Async HTTP requests
   - Error handling and retries

4. **Database Layer** (`modules/db.py`)
   - SQLite3 with aiosqlite
   - Game data management
   - Settings persistence
   - Migration from legacy formats

### External Dependencies
- **F95Indexer API**: `api.f95checker.dev` (independent cache API)
- **F95zone Forum**: Primary data source
- **Browser Extensions**: Chrome and Firefox addons
- **Platform APIs**: Windows Registry, Linux desktop files, macOS plist

## Data Models and Structures

### Core Data Types (`common/structs.py`)
```python
class Game:
    """Represents a game in the library."""
    id: int
    name: str
    version: str
    developer: str
    thread_url: str
    last_update: datetime
    # ... many more fields

class Settings:
    """Application settings and preferences."""
    # GUI preferences
    # API settings
    # Notification preferences
    # ... configuration options

class Browser:
    """Represents an available web browser."""
    name: str
    args: List[str]
    # Browser detection and management
```

### Database Schema
- **games**: Main game information table
- **settings**: Application settings
- **labels**: Custom game labels
- **history**: Update history tracking
- **cookies**: Session management

## Platform-Specific Implementations

### Windows
- **Registry Integration**: Autostart via Windows Registry
- **Notifications**: WinRT-based desktop notifications
- **File Paths**: `%APPDATA%\f95checker\`
- **Browser Detection**: Windows Registry browser keys

### Linux
- **Desktop Integration**: XDG desktop files
- **Autostart**: `~/.config/autostart/F95Checker.desktop`
- **File Paths**: `~/.config/f95checker/`
- **Browser Detection**: XDG MIME type handlers

### macOS
- **App Bundle**: Native .app structure
- **Launch Services**: macOS launch agent integration
- **File Paths**: `~/Library/Application Support/f95checker/`
- **Browser Detection**: macOS application bundle parsing

## Build System Details

### cx_Freeze Configuration
- **Platform Matrix**: Windows, Linux, macOS builds
- **Dependency Management**: Platform-specific package inclusion
- **Resource Bundling**: Icons, fonts, browser extensions
- **System Libraries**: Platform-specific system library linking

### Build Process
1. **Setup Phase**: Install cx_Freeze and dependencies
2. **Mark Version**: Set release flag or build number
3. **Build Executable**: Platform-specific build commands
4. **Bundle Resources**: Include icons, extensions, libraries
5. **Package**: Create distributable archives

### CI/CD Pipeline
- **GitHub Actions**: Multi-platform builds
- **Matrix Strategy**: Windows, Ubuntu, macOS runners
- **Artifact Management**: Platform-specific executables
- **Release Automation**: GitHub release creation

## API Integration Details

### F95Indexer API
- **Purpose**: Independent cache API for F95zone data
- **URL**: `api.f95checker.dev`
- **Caching Strategy**: 7-day cache with smart refresh
- **Rate Limiting**: 10 threads at a time processing
- **Update Monitoring**: 5-minute intervals for latest updates

### API Endpoints
- **Thread Data**: Fetch parsed thread information
- **Update Check**: Check for changes since last refresh
- **Search**: Search games by name or criteria
- **Metadata**: Get thread metadata and statistics

### Error Handling
- **Network Errors**: Retry with exponential backoff
- **Rate Limiting**: Respect API rate limits
- **Data Validation**: Validate API responses
- **Fallback**: Graceful degradation on API failures

## Browser Extension Architecture

### Chrome Extension
- **Manifest V3**: Modern Chrome extension format
- **Content Scripts**: Inject into F95zone pages
- **Background Scripts**: Handle extension logic
- **Popup Interface**: Quick game adding interface

### Firefox Extension
- **WebExtensions**: Cross-browser compatible
- **Native Messaging**: Communication with desktop app
- **AMO Distribution**: Mozilla Add-ons store
- **Update Mechanism**: Automatic updates via AMO

### Integration Protocol
- **Local RPC**: HTTP-based communication
- **Port**: 57095 (configurable)
- **Message Format**: JSON-based protocol
- **Security**: Local-only communication

## Performance Optimizations

### Async Architecture
- **Event Loop**: uvloop for non-Windows platforms
- **Concurrent Requests**: Parallel API calls
- **Database**: Async SQLite operations
- **File I/O**: Async file operations

### Caching Strategy
- **Memory Cache**: Frequently accessed data
- **Disk Cache**: Image and resource caching
- **API Cache**: F95Indexer data caching
- **Browser Cache**: Extension communication cache

### Resource Management
- **Memory Monitoring**: Track memory usage
- **Texture Management**: GUI texture lifecycle
- **Connection Pooling**: HTTP connection reuse
- **Background Tasks**: Non-blocking operations

## Security Considerations

### Data Protection
- **Local Storage**: Sensitive data stored locally
- **Encryption**: No encryption of local database
- **Network Security**: HTTPS for all API calls
- **Credential Handling**: Secure token management

### Privacy Features
- **Anonymous Mode**: Use without F95zone login
- **Local Data**: No cloud synchronization
- **User Control**: Full control over data
- **Transparency**: Open source code

### Security Measures
- **Input Validation**: Sanitize all user inputs
- **SQL Injection**: Parameterized queries only
- **XSS Prevention**: HTML content sanitization
- **CSRF Protection**: Token-based request validation

## Development Workflow

### Git Strategy
- **Main Branch**: Stable release branch
- **Feature Branches**: Individual feature development
- **Commit Messages**: Conventional commit format
- **Build Triggers**: "+BUILD" in commit message

### Code Review Process
- **Pull Requests**: All changes via PR
- **Automated Testing**: CI/CD pipeline checks
- **Manual Review**: Human code review
- **Cross-Platform Testing**: Multiple OS verification

### Release Process
- **Version Bumping**: Manual version updates
- **Changelog**: Detailed change documentation
- **Tag Creation**: Git tags for releases
- **GitHub Releases**: Automated release creation

## Common Development Tasks

### Adding New Features
1. **Design Phase**: Understand requirements and impact
2. **Implementation**: Follow coding conventions
3. **Testing**: Comprehensive test coverage
4. **Documentation**: Update docs and examples
5. **Review**: Code review and approval

### Bug Fixes
1. **Reproduction**: Consistent bug reproduction
2. **Root Cause**: Identify underlying issue
3. **Fix Implementation**: Minimal, targeted fix
4. **Testing**: Regression testing
5. **Documentation**: Update if needed

### Performance Improvements
1. **Profiling**: Identify performance bottlenecks
2. **Optimization**: Targeted performance improvements
3. **Testing**: Verify improvements
4. **Monitoring**: Track performance metrics

## Troubleshooting Guide

### Common Issues
1. **Import Errors**: Check Python path and virtual environment
2. **GUI Crashes**: Update graphics drivers, check OpenGL
3. **Network Issues**: Check firewall, proxy settings
4. **Database Errors**: Check file permissions, disk space
5. **Build Failures**: Verify dependencies, check platform

### Debug Mode Features
- **Detailed Logging**: Comprehensive debug output
- **Error Tracebacks**: Full exception details
- **Performance Metrics**: Timing and memory usage
- **Network Monitoring**: Request/response logging

### Platform-Specific Issues
- **Windows**: Graphics driver issues, antivirus interference
- **Linux**: Missing system libraries, desktop environment compatibility
- **macOS**: Gatekeeper quarantine, Rosetta 2 for Intel Macs

## Community and Support

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **F95zone Thread**: Community discussion and support
- **GitHub Discussions**: Technical discussions
- **Discord**: Real-time community chat

### Contributing Guidelines
- **Code Style**: Follow project conventions
- **Testing**: Include tests for new features
- **Documentation**: Update relevant documentation
- **Communication**: Discuss major changes first

### Support Resources
- **FAQ**: Comprehensive frequently asked questions
- **Wiki**: Detailed technical documentation
- **Video Guides**: Visual tutorials for common tasks
- **Community**: Active user community for help