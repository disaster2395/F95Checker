# F95Checker Code Style and Conventions

## Python Code Style

### General Guidelines
- **Python Version**: Python 3.11+ required
- **Line Length**: Keep lines reasonably short (typically under 88 characters)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8 encoding for all source files
- **Line Endings**: LF (\\n) for cross-platform compatibility

### Naming Conventions
- **Variables**: snake_case (e.g., `game_library`, `refresh_total`)
- **Functions**: snake_case (e.g., `get_game_info()`, `refresh_games()`)
- **Classes**: PascalCase (e.g., `MainGUI`, `GameManager`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `RPC_PORT`, `MAX_RETRIES`)
- **Private Methods**: prefix with underscore (e.g., `_internal_method()`)
- **Magic Methods**: double underscore (e.g., `__init__()`, `__str__()`)

### Import Organization
```python
# Standard library imports
import asyncio
import contextlib
import sys
import pathlib
import re

# Third-party imports
from concurrent.futures import Future
from functools import partial
from logging import Logger

# Local imports (relative imports preferred)
from common.structs import (
    Browser,
    Game,
    OldGame,
    Os,
    Popup,
    Settings,
)
from modules import globals
```

### Type Hints
- **Required**: Use type hints for function parameters and return values
- **Union Types**: Use `|` syntax for Python 3.10+ or `Union[]` for compatibility
- **Optional**: Use `| None` or `Optional[]`
- **Generic Types**: Use appropriate generic types like `List[str]`, `Dict[int, Game]`

```python
def get_game_by_id(game_id: int) -> Game | None:
    """Get game by ID, returns None if not found."""
    return games.get(game_id)

def refresh_games(self, force: bool = False) -> Future[None]:
    """Refresh game data asynchronously."""
    pass
```

### Docstring Style
- **Format**: Google-style docstrings
- **Required**: For all public functions and classes
- **Parameters**: Document all parameters with types
- **Returns**: Document return values and types
- **Raises**: Document exceptions that may be raised

```python
def fetch_game_data(url: str, timeout: float = 30.0) -> dict[str, Any]:
    """Fetch game data from F95zone thread.
    
    Args:
        url: The F95zone thread URL
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing parsed game information
        
    Raises:
        requests.RequestException: If the HTTP request fails
        ValueError: If the URL is invalid
    """
    pass
```

## Project Structure Conventions

### Module Organization
```
modules/
├── api.py              # API communication
├── gui.py              # Main GUI interface
├── db.py               # Database operations
├── globals.py          # Global variables and state
├── utils.py            # Utility functions
├── patches.py          # Monkey patches and fixes
├── webview.py          # Web view handling
├── notification_proc.py # Notification processing
└── rpc_thread.py       # RPC communication thread
```

### File Naming
- **Modules**: snake_case (e.g., `api_client.py`, `game_manager.py`)
- **Classes**: PascalCase (e.g., `GameManager`, `APIClient`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`, `MAX_RETRIES`)

### Circular Import Prevention
- Use late imports within functions when possible
- Import common modules at the top level
- Use `TYPE_CHECKING` for type-only imports

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.gui import MainGUI

def setup_gui() -> MainGUI:
    from modules.gui import MainGUI  # Late import
    return MainGUI()
```

## Async/Await Patterns

### Async Function Design
- **Naming**: Use async def for asynchronous functions
- **Error Handling**: Use try/except within async functions
- **Cancellation**: Handle asyncio.CancelledError appropriately
- **Timeout**: Use asyncio.timeout() for timeout handling

```python
async def fetch_with_timeout(url: str, timeout: float = 30.0) -> str:
    """Fetch URL content with timeout."""
    try:
        async with asyncio.timeout(timeout):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
    except asyncio.TimeoutError:
        logger.warning(f"Request timed out: {url}")
        raise
```

### Event Loop Management
- **Platform-specific**: Use uvloop on non-Windows platforms
- **Error Handling**: Graceful fallback if uvloop unavailable
- **Setup**: Configure in main() function

```python
def main():
    from common.structs import Os
    if globals.os is not Os.Windows:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except Exception:
            pass  # Fallback to default event loop
```

## Error Handling

### Exception Handling Patterns
- **Specific Exceptions**: Catch specific exceptions when possible
- **Logging**: Log errors with appropriate level
- **User Feedback**: Provide meaningful error messages to users
- **Graceful Degradation**: Continue operation when non-critical errors occur

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return default_value
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

### Debug Mode Handling
- **Environment Variable**: Check `F95DEBUG` environment variable
- **Debug Output**: Conditional debug logging and output
- **Error Display**: Show detailed tracebacks in debug mode

```python
debug = not (frozen or release)
if not sys.stdout or not sys.stderr or os.devnull in (sys.stdout.name, sys.stderr.name):
    debug = False

if "F95DEBUG" not in os.environ:
    os.environ["F95DEBUG"] = str(int(debug))
```

## Cross-Platform Compatibility

### Platform Detection
```python
from common.structs import Os

if sys.platform.startswith("win"):
    os = Os.Windows
elif sys.platform.startswith("linux"):
    os = Os.Linux
elif sys.platform.startswith("darwin"):
    os = Os.MacOS
```

### Platform-Specific Code
- **Conditional Imports**: Use platform checks for imports
- **Path Handling**: Use pathlib for cross-platform paths
- **System Calls**: Use platform-appropriate system calls

```python
if os is Os.Windows:
    import winreg
    data_path = "AppData/Roaming/f95checker"
elif os is Os.Linux:
    import configparser
    data_path = ".config/f95checker"
elif os is Os.MacOS:
    import plistlib
    data_path = "Library/Application Support/f95checker"
```

## Database Patterns

### SQLite3 Usage
- **Async Operations**: Use aiosqlite for async database operations
- **Connection Management**: Use context managers for connections
- **Error Handling**: Handle database errors gracefully
- **Migration**: Support legacy data migration

```python
async def get_game(game_id: int) -> Game | None:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM games WHERE id = ?", (game_id,)) as cursor:
            row = await cursor.fetchone()
            return Game.from_row(row) if row else None
```

## GUI Patterns

### Dear ImGui Integration
- **State Management**: Maintain GUI state in class instances
- **Event Handling**: Handle user interactions through callbacks
- **Resource Management**: Properly manage textures and fonts
- **Threading**: GUI operations must be on main thread

### Main GUI Structure
```python
class MainGUI:
    def __init__(self):
        self.running = False
        self.refresh_callbacks = []
        
    def main_loop(self):
        """Main GUI event loop."""
        self.running = True
        while self.running:
            # Process GUI events
            # Render frame
            pass
            
    def add_refresh_callback(self, callback: Callable):
        """Add callback for refresh events."""
        self.refresh_callbacks.append(callback)
```

## Performance Considerations

### Memory Management
- **Lazy Loading**: Load resources only when needed
- **Resource Cleanup**: Properly dispose of resources
- **Caching**: Implement appropriate caching strategies
- **Large Data**: Handle large datasets efficiently

### Async Performance
- **Concurrent Operations**: Use asyncio.gather() for concurrent operations
- **Rate Limiting**: Implement rate limiting for API calls
- **Connection Pooling**: Use connection pools for HTTP requests
- **Background Tasks**: Use background tasks for non-blocking operations

## Testing Patterns

### Test Structure
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Async Tests**: Use pytest-asyncio for async testing
- **Mocking**: Mock external dependencies

### Example Test Pattern
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_game_data():
    """Test game data fetching."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.text.return_value = "<html>test</html>"
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await fetch_game_data("https://f95zone.to/test")
        assert "test" in result
```

## Security Considerations

### Input Validation
- **URL Validation**: Validate URLs before making requests
- **Data Sanitization**: Sanitize user input
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Sanitize HTML content

### Credential Management
- **Environment Variables**: Store sensitive data in environment variables
- **Secure Storage**: Use platform-appropriate secure storage
- **Token Management**: Handle authentication tokens securely

## Documentation Standards

### Code Comments
- **Complex Logic**: Comment complex algorithms and business logic
- **Workarounds**: Explain why workarounds are necessary
- **TODOs**: Mark future improvements with TODO comments
- **FIXMEs**: Mark known issues that need fixing

### Example Comments
```python
# TODO: Implement caching for frequently accessed games
# FIXME: Handle network timeouts more gracefully
# NOTE: This workaround is needed due to F95zone API limitations
```

## Version Control Practices

### Commit Messages
- **Conventional Commits**: Use conventional commit format
- **Descriptive**: Provide clear description of changes
- **Build Triggers**: Include "+BUILD" in commit message to trigger CI

### Branch Strategy
- **Feature Branches**: Create branches for new features
- **Hotfix Branches**: Create branches for critical fixes
- **Main Branch**: Keep main branch stable

### Example Commit Messages
```
feat: add game filtering by developer
fix: resolve timeout issue in API client
docs: update installation instructions
build: update cx_Freeze version +BUILD
```