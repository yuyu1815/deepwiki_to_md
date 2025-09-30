# Project Development Guidelines (deepwiki_to_md)

This document captures project-specific knowledge for developing and maintaining this repository. It focuses on build/configuration, testing, and implementation caveats unique to this codebase. For a Japanese version, see .junie/guideline_ja.md.

---

## 1. Build / Configuration

This section has been moved to a dedicated document for clarity and maintenance:
- Build / Configuration (deepwiki_to_md): [./guidelines_build.md](./guidelines_build.md)

---

## 2. Testing

This section has been moved to a dedicated document for clarity and maintenance:
- Testing (deepwiki_to_md): [./guidelines_testing.md](./guidelines_testing.md)

---

## 3. Additional Development Information

- Code style / static analysis
  - black/isort/mypy/flake8 are configured in pyproject.toml.
  - mypy is strict (e.g., disallow_untyped_defs). Public functions must have type hints.
  - Use logging, not print, except for user-facing CLI output.

- Design approach
  - Favor composition (StrategyManager with multiple ExtractionStrategy implementations).
  - Use explicit custom exceptions (ExtractorError/HTTPError/ContentError/ConfigError).
  - For HTML/JSON parsing, combine regex with structural checks to be resilient to partial failures.

- CLI output design
  - Only save files when input is a URL.
  - Split Markdown by H1 (split_markdown_by_h1) and sanitize filenames (sanitize_filename).
  - Generate a library-level index under .deepwiki/<username>/<library>.md linking to saved sections.

- Known pitfalls
  - pytest testpaths mismatch (tests vs test directory).
  - Coverage target refers to a non-existent module (src.html_formatter).
  - Chat depends on external services and requires initial config derived from XML logs.

- Recommended workflow
  - Create venv: python -m venv .venv && source .venv/bin/activate
  - Install dev deps: python -m pip install -e .[dev]
  - Lint/type-check: black . && isort . && flake8 && mypy src
  - Run tests: PYTHONPATH=src pytest -q or pytest test -q

---

## 4. Python conventions (project-applied highlights)

- Clean, PEP8-compliant code (black/flake8).
- Manage resources with with; handle exceptions explicitly.
- Annotate typing for Dict/List/etc.
- Prefer composition over inheritance; keep functions short and clear.
- Public code must include English docstrings and have tests where appropriate.
- No mutable globals; use virtual environments.
- Use enumerate()/zip(), comprehensions, and f-strings.
- Use dataclasses; naming: snake_case / PascalCase / UPPER_CASE.
- Avoid circular imports; prefer standard library.
- Log exceptions; avoid print() except for CLI user output.
- Make changes carefully; analyze impact and verify behavior.
- Investigate root causes for bugs.
- Avoid processing excessively large data (rows/bytes) when not necessary.
- Comments may be written in Japanese when helpful.

- Comments
  - When editing with comments, avoid mentioning or referring to removed items.
  - Write comments so that new contributors can understand them immediately; be concise and explicit.

---

## 5. Shallow nesting and 6‑month clarity (project rule)

- Rule of thumb
  - Keep nesting shallow by using guard clauses (early returns) and extracting small helper functions.
  - Prefer linear, readable flows over deeply nested conditionals/loops.
  - Write code so that a future maintainer can understand intent “at a glance” six months later.

- Practical checklist before merging
  - Is there any if/elif/else or try/except block nested more than two levels? Flatten with guard clauses where possible.
  - Can a long conditional branch be moved into a short helper (with a descriptive name)? Do it.
  - Are variable and function names self-explanatory without reading implementation? Rename if not.
  - Add a brief docstring or comment for non-obvious logic and data structures (1–3 lines max).
  - Avoid clever tricks; prefer explicit, boring code.

- Affected modules (typical hotspots)
  - src/chat.py: WebSocket message handling → use small handlers and guard clauses.
  - src/deepwiki_to_md.py: Strategy selection and HTTP response processing → keep branches flat.
  - src/cli.py: Keep I/O paths separate; return early for stdout vs file output.

- Process requirement (確認の慣行)
  - Before changing files, ask the user which files are affected and why (impact reasoning). When possible, ask in Japanese for confirmation.
  - Before making changes, explicitly ask whether to keep backward compatibility or replace entirely, and proceed per the user's choice.
  - Document the chosen scope and rationale in the task update/status before editing.

- Testing after refactor
  - Run PYTHONPATH=src pytest -q (or pytest test -q) and verify behavior is unchanged.
  - Prefer adding tiny smoke tests around refactored helpers if feasible.


---

## 6. Policy updates (2025-09-21)

These updates document recent design decisions so future work follows the same approach (「今後そういう設計で進める」方針の明文化).

- Path resolution policy (config files)
  - Absolute paths: use as-is.
  - Relative paths: resolve relative to the caller script (the user’s file that invoked the function). If not found, fall back to the current working directory for backward compatibility.
  - Avoid broad try/except around path resolution; prefer guard clauses and explicit checks. Log meaningful paths (original arg and resolved path) when failures occur.

- Exception handling policy
  - Avoid unnecessary try/except where simple conditionals suffice (e.g., urlparse does not raise).
  - Catch specific exceptions instead of bare except. Keep the surface of try blocks minimal and local to the risky operation.
  - Shallow nesting: use early returns (guard clauses) and small helpers to keep flows linear.
  - CLI run(): one top-level try is acceptable for user-facing robustness; other logic should avoid deep nesting.

- Dependencies and networking
  - Keep the core library zero-dependency where possible. Use standard library (e.g., urllib) for simple HTTP in reusable modules like search_repository.
  - Defer optional heavy dependencies (e.g., requests, websockets) to the functions that need them (lazy import). If missing, raise a clear RuntimeError instructing how to install.

- URL parsing rule
  - Do not wrap urlparse in try/except; check scheme and netloc directly to determine a valid URL.

- Backward compatibility note
  - When changing behaviors like path resolution, maintain a compatibility fallback (e.g., CWD) and document it here and in docstrings.
