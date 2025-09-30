# Testing (deepwiki_to_md)

- Tools
  - pytest and pytest-cov are defined under optional-dependencies (test/dev extras).
  - Quick start:
    - python -m venv .venv && source .venv/bin/activate  (Windows: .venv\\Scripts\\activate)
    - Minimal deps: python -m pip install -e .[test]
    - Full dev deps: python -m pip install -e .[dev]

- Important: test directory layout
  - pyproject.toml configures pytest with testpaths = ["tests"].
  - However, this repo’s actual test materials live under test/ (e.g., test/chat.py).
  - Therefore, default pytest may report “no tests found” unless you direct it. Options:
    1) Ignore testpaths at runtime and target the directory explicitly: pytest test
    2) Set PYTHONPATH=src to resolve imports and rely on recursion: PYTHONPATH=src pytest -q
    3) Or create a tests/ directory and place tests there (recommended for consistency).

- Import resolution
  - This repository uses the "src" layout. To import deepwiki_to_md, cli, chat in tests:
    - Export PYTHONPATH=src, or
    - Install the package in editable mode (pip install -e .).

- Coverage caveat
  - [tool.pytest.ini_options].addopts includes --cov=src.html_formatter and --cov=src.deepwiki_to_md.
  - src/html_formatter.py does not exist, which triggers a CoverageWarning and can break report generation in strict setups.
  - Options (documentation only; no repo change unless requested):
    - Remove or replace --cov=src.html_formatter, and/or
    - Align testpaths/test directory to ensure modules import during coverage collection.

- Example smoke test run (manual validation flow)
  - Create a temporary tests/test_smoke.py that:
    - Verifies import of deepwiki_to_md
    - Asserts cli.main(["--help"]) exits with SystemExit(0) and the help text contains “Extract Markdown”
  - Run: PYTHONPATH=src pytest -q
  - Expected: 2 passed in ~0.04s

- Network-dependent tests
  - test/chat.py assumes real requests/websockets. For CI, mock them (unittest.mock/pytest-mock). Provide stubbed responses and avoid hitting external services.
  - test/config.json and test/out.json are auxiliary and may be absent/invalid in your environment; avoid making unit tests depend on them.
