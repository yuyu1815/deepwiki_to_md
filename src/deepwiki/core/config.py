import re


class ExtractionConfig:
    """Patterns and thresholds used by extraction strategies."""

    STRING_PAYLOAD_PATTERN = re.compile(
        r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"]\)', re.DOTALL
    )
    MIN_CHUNK_LENGTH = 8
    CONTENT_MARKERS = (
        "# ",
        "## ",
        "### ",
        "#### ",
        "```",
        "Sources:",
        "<details",
        "<summary",
        "mermaid",
        "graph ",
        "flowchart ",
        "Note:",
        "Warning:",
        "![",
        "](http",
    )
    NOISE_PATTERNS = (
        "static/chunks",
        "/_next/static",
        "$Sreact",
        "__webpack",
        "module.exports",
        "require(",
        "import {",
    )
    RSC_PREFIXES = ('["%24",', '["$', '["%24%24",')
    TOKEN_PATTERN = re.compile(r"[0-9a-z]{1,3}:[A-Za-z0-9]+,")


class HTTPConfig:
    """Defaults used by the HTTP client."""

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
    }
