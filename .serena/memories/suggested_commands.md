# F95Checker — Suggested Commands

## Development / Run from Source
```bash
# Install deps
pip3 install -U -r requirements.txt

# Run desktop app
python3 main.py

# Run indexer service
pip3 install -U -r requirements-indexer.txt
python3 indexer-main.py
```

## Build / Package
```bash
# Build desktop binaries
python setup.py build               # Windows / Linux
python setup.py bdist_mac           # macOS

# Build browser extension zips
python setup.py browser             # or: python setup.py extension
```

## Windows Shell Notes
- Use `python` / `pip` instead of `python3` / `pip3` if those are not on PATH.
- `setup.py build` produces binaries in `build/`.
- `pywin32` and `cx_Logging` are required for Windows builds.

## Git
- Build triggers on commit messages containing `+ BUILD`.
- CI rewrites `common/meta.py` with `sed` to set `release = True` and inject build numbers.
