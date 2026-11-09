# Contributing

1. Search issues and discussions before starting.
2. Open an issue before large architectural changes.
3. Never publish private prompts, credentials, customer data, or secrets.

## Setup
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Checks
```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Keep PRs focused, add tests, update docs, explain limitations, and do not claim semantic equivalence from heuristics. Contributions are licensed under Apache-2.0.
