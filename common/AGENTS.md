# SHARED MODELS AND PARSING

## OVERVIEW
Shared metadata, domain structures, and forum parsing; score 9: code ratio 2, symbol density 2, imported surface 2, reference centrality 3.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Version, build identity, paths | `meta.py` | Source/frozen detection and RPC metadata |
| Game and settings fields | `structs.py:Game`, `Settings` | Desktop persistence and UI consume these |
| Tags, status, type values | `structs.py` | Shared enums also used by parser/indexer |
| Labels, tabs, browser records | `structs.py:Label`, `Tab`, `Browser` | Stateful desktop-facing structures |
| Pipe/process helpers | `structs.py:AbstractPipe`, `DaemonPipe`, `ChildPipe` | Parent/child communication |
| Forum thread extraction | `parser.py:thread` | Returns `ParsedThread` or `ParserError` |
| Review extraction | `parser.py:reviews` | Structured review result |
| Text/date/image normalization | `parser.py` | Shared helpers feeding parsed results |

## CONVENTIONS
- `parser.py` is consumed by both desktop and indexer code.
- Parsed payloads use slotted dataclasses, including `ParsedThread` and review records.
- Parsing failures can be returned as `ParserError` values; inspect the result contract.
- `ParserError` carries a message and optional dump, not just an exception string.
- `structs.py` includes behavior and deferred desktop imports, not only passive schemas.
- `Game` fields connect to database serialization and GUI state.
- `Game` has more than 20 reference locations in the inspected LSP map.
- `meta.py` increments the upstream patch version and adds the fork's `(b-mod)` identity.
- `meta.self_path` handles both source execution and frozen binaries.
- `meta.rpc_port` defines the desktop/browser port, currently 57095.
- Debug state also propagates through the `F95DEBUG` environment variable.

## ANTI-PATTERNS
- Do not assume `parser.thread()` always returns a parsed record or raises on failure.
- Do not replace frozen-path logic with paths relative to the current working directory.
- Do not treat enum/model changes as desktop-only; check indexer serialization and parsing.
- Do not move deferred desktop imports to module scope without checking cycles.
- Do not normalize parsed dates to local midnight: `datestamp()` uses UTC noon.
