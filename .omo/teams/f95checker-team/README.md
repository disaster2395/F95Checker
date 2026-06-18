# F95Checker Development Team

This directory contains the team spec for opencode/OMO team-mode.

## Usage

To recreate the team in a new session, use the spec from `config.json` or run:

```json
{
  "team_mode": {
    "enabled": true,
    "max_parallel_members": 4,
    "max_members": 8,
    "tmux_visualization": false
  }
}
```

Then create the team with the spec in `config.json`.

## Members

| Member | Category | Focus |
|--------|----------|-------|
| `ui-specialist` | `visual-engineering` | PyQt6 + Dear ImGui desktop UI, browser extension |
| `backend-specialist` | `deep` | FastAPI indexer, API client, SQLite database |
| `python-specialist` | `unspecified-high` | General Python logic, build scripts, refactoring |

## Notes

- Team specs created via `inline_spec` are **session-bound** unless saved to disk like this file.
- The `oh-my-openagent.json` in the parent `.opencode/` folder only enables the `team_mode` feature flag.
