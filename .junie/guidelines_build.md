# Build / Configuration (deepwiki_to_md)

- Packaging/Build
  - PEP 517/518 compliant. Uses setuptools.build_meta declared in pyproject.toml.
  - Designed for zero external dependencies (pure Python standard library at runtime).
  - Distributions: source and wheel artifacts are generated under dist/.
  - Build steps:
    - If build is missing: python -m pip install build
    - Build: python -m build

- Development install / import options
  - To make sources importable, either:
    - Temporarily set PYTHONPATH to src (Unix): PYTHONPATH=src python -c "import deepwiki_to_md; print(deepwiki_to_md.__name__)"
    - On Windows (PowerShell): $env:PYTHONPATH="src"; python -c "import deepwiki_to_md; print(deepwiki_to_md.__name__)"
    - Or do an editable install: python -m pip install -e .[dev]
  - CLI entry point:
    - deepwiki-to-md = "cli:main" in [project.scripts]
    - You can also run locally via module: python -m cli input.html

- Runtime working directory / output behavior
  - When input is a DeepWiki URL, output is split by H1 and saved under .deepwiki/<username>/<library>/<section>.md, and an index is generated at .deepwiki/<username>/<library>.md (see src/cli.py _write_output).
  - When input is a local HTML file or stdin, Markdown is written to stdout and no files are created.
  - Filenames are sanitized via sanitize_filename; titles are derived from H1 segments.

- Chat feature (Devin API integration)
  - Example command:
    - deepwiki-to-md chat --url https://deepwiki.com/microsoft/WSL --message "Explain WSLg Wayland and RDP" --deep-research --config-file config.json
  - Config generation (src/chat.py: load_or_create_config):
    - If the specified JSON does not exist, the tool attempts to parse an XML log file named deepResearch or test in the current directory to extract minimal headers and a request body template, then writes config.json.
    - If the log file is absent or the expected API request is not found/parsable, initialization fails. Prepare the log file before the first run.
  - Transport: HTTP POST + WebSocket. This is network-dependent; in CI/tests, prefer mocking.
