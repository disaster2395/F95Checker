# F95Checker — Task Completion Checklist

## After Code Changes
1. **Run the desktop app**: `python main.py` — verify no import/crash on startup.
2. **Check for syntax errors**: `python -m py_compile <changed_file.py>` for each changed file.
3. **Verify no broken references**: run the app and exercise the affected UI flow if possible.

## No Automated Tests
- There is no committed test suite. Manual QA is required for behavioral changes.

## Before Committing (if user requests)
- Ensure `common/meta.py` `release` flag is appropriate (usually `False` for dev work).
- If a build is intended, include `+ BUILD` in the commit message to trigger CI.

## Notes
- No linter or formatter is configured; matching existing code style is sufficient.
- The most common breakage is an import error due to deferred import paths or a missing dependency.
