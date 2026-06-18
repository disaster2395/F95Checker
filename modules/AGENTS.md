# modules/ KNOWLEDGE BASE

## OVERVIEW
Core desktop application logic: UI shell, database, API client, notifications, webviews, and browser-extension RPC.

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Change UI layout / screens | gui.py | 5571-line ImGui/Qt shell; contains fragile ImGui hacks — do not refactor without visual QA |
| Add a game property or DB field | db.py | SQLite schema + migrations; check `setup()` and table defs |
| Modify refresh / download logic | api.py | HTTP session, ratelimiter, thread data fetching |
| Qt WebEngine popups | webview.py | Subprocess bridge for web content |
| Desktop notifications | notification_proc.py | Runs as `notification-daemon` subprocess |
| Browser extension comms | rpc_thread.py | Localhost RPC server for extension integration |
| UI callbacks / event wiring | callbacks.py | Glues GUI events to backend actions |
| RPDL.net torrents | rpdl.py | Separate download integration module |
| Colors / theming | colors.py | UI color definitions |
| Icons / image helpers | icons.py | Icon mapping and loading |

## CONVENTIONS
- Deferred imports inside functions are common here to avoid circular deps with gui.py.
- gui.py uses raw ImGui API heavily; many workarounds are documented as inline `Hack:` comments.
