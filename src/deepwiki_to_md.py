#!/usr/bin/env python3
"""
Extensible tool to extract Markdown-like text from Next.js/DeepWiki HTML or scripts.

Goals:
    Provide a simple CLI and library that extracts human-readable text using pluggable strategies.

Design:
    - Strategy pattern: multiple approaches (NextJS push, RSC stream, fallback) can be selected.
    - Config driven: adjustable via Config classes.
    - Easy to extend: add strategies without touching the core.
    - Maintainable: separation of concerns for 6-month clarity.

Maintenance notes:
    - To add a strategy: subclass ExtractionStrategy and register it in StrategyManager.
    - To tweak heuristics: edit constants in ExtractionConfig.
    - To extend output: subclass or modify OutputFormatter.
    - To adjust HTTP behavior: edit HTTPConfig.

Usage:
    # Extract from a local HTML file
    python3 deepwikimd.py sample.html --path ./output

    # Extract from a URL
    python3 deepwikimd.py https://deepwiki.com/path --path ./output
"""

import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def normalize_deepwiki_url( raw):
    """Normalize DeepWiki URLs.

    If a path-like string is given (e.g., /owner/repo or owner/repo), convert it to
    https://deepwiki.com/<owner>/<repo>. Otherwise, return the input as-is.
    """
    # Convert path-like strings (/owner/repo or owner/repo) into full URLs
    if raw.startswith("/") or ("/" in raw and " " not in raw):
        return f"https://deepwiki.com/{raw.strip('/')}"
    return raw

# ============================================================================
# CONFIGURATION CLASSES (6-month maintenance point)
# ============================================================================

class ExtractionConfig:
    """Configuration for content extraction.

    Maintenance tips:
    - Add to CONTENT_MARKERS for new content types.
    - Adjust NOISE_PATTERNS for new frameworks.
    - Revisit MIN/MAX_CHUNK_LENGTH for performance.
    """
    
    # Core extraction patterns
    STRING_PAYLOAD_PATTERN = re.compile(
        r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"]\)',
        re.DOTALL
    )
    
    # Content filtering settings
    MIN_CHUNK_LENGTH = 8
    MAX_CHUNK_LENGTH = 10000
    
    # Content markers (expand for new content types)
    CONTENT_MARKERS = (
        "# ", "## ", "### ", "#### ",  # Markdown headings
        "```",                         # Code blocks
        "Sources:",                    # References
        "<details", "<summary",        # HTML details elements
        "mermaid",                     # Diagrams
        "graph ", "flowchart ",        # Graph syntax
        "Note:", "Warning:",           # Admonitions
        "![", "](http",               # Images and links
    )
    
    # Noise patterns (expand for new frameworks)
    NOISE_PATTERNS = (
        "static/chunks",
        "/_next/static",
        "$Sreact",
        "__webpack",
        "module.exports",
        "require(",
        "import {",
    )
    
    # RSC prefixes (update for Next.js changes)
    RSC_PREFIXES = ('["%24",', '["$', '["%24%24",')
    
    # Token pattern for filtering
    TOKEN_PATTERN = re.compile(r"[0-9a-z]{1,3}:[A-Za-z0-9]+,")


class HTTPConfig:
    """HTTP configuration.

    Maintenance tips:
    - Update DEFAULT_HEADERS for newer user-agents.
    - Extend ALLOWED_DOMAINS for security.
    - Tune timeout values for performance.
    """
    
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
    }
    
    # セキュリティ: 許可ドメイン（必要に応じて拡張）/ Security: allowed domains (expand as needed)
    ALLOWED_DOMAINS = (
        "deepwiki.com",
        "*.deepwiki.com",
    )


# ============================================================================
# ユーティリティ関数 / UTILITY FUNCTIONS
# ============================================================================
def sanitize_filename(name: str) -> str:
    """Normalize a string to be safe for use as a filename.

    Args:
        name: The input string to normalize.

    Returns:
        A string safe to use as a filename.
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove or replace invalid characters for filenames
    # This pattern allows only alphanumeric, underscores, hyphens, dots
    name = re.sub(r'[^\w\-_.]', '', name)
    
    # Ensure the filename is not empty
    if not name:
        name = "unnamed"
        
    return name


def _parse_sections_state_machine(content: str) -> List[Dict[str, str]]:
    """Parse Markdown into sections using a simple state machine.

    - Splits by H1 (ATX "# ") and Setext ("====") headers.
    - Ignores headers when inside fenced code blocks (``` or ~~~).
    - Produces an initial list of sections with raw (unfiltered) content.
    - Keeps an implicit initial section named "Introduction" and drops it if empty.

    This function preserves the legacy behavior of split_markdown_by_h1.
    """
    sections: List[Dict[str, str]] = []
    lines: List[str] = content.split('\n')

    in_code_block: bool = False
    current_section_title: str = "Introduction"
    current_section_content: List[str] = []

    def _append_section_if_needed(title: str, body_lines: List[str]) -> None:
        # Skip empty initial section (Introduction), but add others even if empty.
        body = '\n'.join(body_lines).strip()
        if title == "Introduction" and body == "":
            return
        sections.append({"title": title, "content": body})

    prev_line: str = ""
    for line in lines:
        stripped = line.strip()
        is_backtick_fence = stripped != "" and all(ch == '`' for ch in stripped) and len(stripped) >= 2
        is_tilde_fence = stripped != "" and all(ch == '~' for ch in stripped) and len(stripped) >= 3
        if is_backtick_fence or is_tilde_fence:
            in_code_block = not in_code_block
            current_section_content.append(line)
            prev_line = line
            continue

        # Detect Setext H1 (previous line is title, this line is ==== etc.)
        if (
            not in_code_block
            and stripped
            and all(ch == '=' for ch in stripped)
            and prev_line.strip()
        ):
            # Save previous section (skip if Introduction is empty)
            prev_content_lines = current_section_content[:-1]
            _append_section_if_needed(current_section_title, prev_content_lines)
            # Start new section (title is previous line)
            current_section_title = prev_line.strip()
            current_section_content = []
            prev_line = line
            continue

        # Check for ATX H1 headers (exact "# ") outside code blocks
        if not in_code_block and line.startswith("# "):
            _append_section_if_needed(current_section_title, current_section_content)
            current_section_title = line[2:].strip()  # Remove "# " prefix
            current_section_content = []
        else:
            current_section_content.append(line)
        prev_line = line

    _append_section_if_needed(current_section_title, current_section_content)
    return sections


def _filter_sections(sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Post-process section contents to remove non-content parts.

    Behavior is kept identical to the legacy implementation:
    - Remove entire <details> blocks (from <details ...> to </details>).
    - Drop <summary ...> lines.
    - Drop navigation list items like "- [title](... .md)".
    - Trim trailing/leading whitespace of each section's content.
    """
    result: List[Dict[str, str]] = []
    for section in sections:
        raw_content = section.get('content', '')
        sec_lines = raw_content.split('\n') if raw_content else []
        filtered_lines: List[str] = []
        skip_details = False

        for l in sec_lines:
            l_strip_lower = l.strip().lower()
            if l_strip_lower.startswith('<details'):
                skip_details = True
                continue
            if l_strip_lower.startswith('</details'):
                skip_details = False
                continue
            if skip_details:
                continue

            if l_strip_lower.startswith('<summary'):
                continue
            if l.strip().startswith('- [') and l.strip().endswith('.md)'):
                continue

            filtered_lines.append(l)

        result.append({
            'title': section.get('title', ''),
            'content': '\n'.join(filtered_lines).strip(),
        })
    return result


def split_markdown_by_h1(content: str) -> List[Dict[str, str]]:
    """Split Markdown by H1 headers while ignoring H1s inside code blocks.

    This is a thin wrapper that delegates to two focused helpers:
    1) _parse_sections_state_machine: builds raw sections.
    2) _filter_sections: removes non-content lines/blocks.

    Args:
        content: The Markdown string to split.

    Returns:
        A list of dicts with 'title' and 'content' keys.
    """
    sections = _parse_sections_state_machine(content)
    return _filter_sections(sections)


# ============================================================================
# ERROR HANDLING CLASSES
# ============================================================================

class ExtractorError(Exception):
    """Base class for extraction-related errors."""
    pass


class HTTPError(ExtractorError):
    """Errors related to HTTP communication."""
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message} for {url}")


class ContentError(ExtractorError):
    """Errors related to content processing."""
    pass


class ConfigError(ExtractorError):
    """Errors related to configuration."""
    pass


# ============================================================================
# EXTRACTION STRATEGY PATTERN (6-month maintenance point)
# ============================================================================

class ExtractionStrategy(ABC):
    """Abstract base class for extraction strategies.

    Maintenance guide:
    1. Subclass this class to create a new strategy.
    2. Implement can_handle() and extract_content().
    3. Register it in StrategyManager._register_default_strategies().
    4. Set an appropriate priority via get_priority().
    """

    @abstractmethod
    def can_handle(self, html: str, url: str = None) -> bool:
        """Return True if this strategy can handle the given HTML/URL."""
        pass

    @abstractmethod
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content using this strategy."""
        pass

    def get_priority(self) -> int:
        """Return the strategy priority (higher is preferred)."""
        return 50

    def get_name(self) -> str:
        """Return the strategy name for identification."""
        return self.__class__.__name__


class NextJSPushStrategy(ExtractionStrategy):
    """Extraction strategy for current Next.js self.__next_f.push format."""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "self.__next_f.push" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from self.__next_f.push payloads."""
        chunks: List[str] = []
        
        for match in ExtractionConfig.STRING_PAYLOAD_PATTERN.finditer(html):
            raw = match.group(1)
            try:
                # JSON 形式のエスケープをデコード / Decode JSON-style escapes
                decoded = json.loads(f'"{raw}"')
            except Exception:
                # フォールバック: 手動置換 / Fallback: manual replacement
                decoded = (
                    raw.replace('\\n', '\n')
                       .replace('\\t', '\t')
                       .replace('\\"', '"')
                       .replace('\\r', '\r')
                       .replace('\\u003c', '<')
                       .replace('\\u003e', '>')
                       .replace('\\u0026', '&')
                )
                
            if self._is_content_chunk(decoded):
                chunks.append(decoded.strip())
        
        # 連続する重複をまとめる / Coalesce consecutive duplicates
        merged: List[str] = []
        for chunk in chunks:
            if not merged or merged[-1] != chunk:
                merged.append(chunk)
                
        return "\n\n".join(merged).strip() + "\n" if merged else ""
    
    def _is_content_chunk(self, s: str) -> bool:
        """Determine if a chunk of text is meaningful rather than framework noise"""
        t = s.strip()
        
        # Too short
        if len(t) < ExtractionConfig.MIN_CHUNK_LENGTH:
            return False
            
        # Control tokens
        if ExtractionConfig.TOKEN_PATTERN.fullmatch(t):
            return False
            
        # RSC wiring
        if t.startswith(ExtractionConfig.RSC_PREFIXES):
            return False
            
        # Contains content markers
        if any(marker in t for marker in ExtractionConfig.CONTENT_MARKERS):
            return True
            
        # Numeric-prefixed wiring
        if re.match(r"^[0-9]+:", t):
            return False
            
        # Static asset references
        if any(noise in t for noise in ExtractionConfig.NOISE_PATTERNS):
            return False
            
        return False
    
    def get_priority(self) -> int:
        return 90  # Highest priority (current method)


class NextJSDataStrategy(ExtractionStrategy):
    """Strategy to extract from __NEXT_DATA__ script tags."""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "__NEXT_DATA__" in html and "type=\"application/json\"" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from the __NEXT_DATA__ script tag."""
        match = re.search(
            r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>([^<]+)</script>', 
            html, 
            re.IGNORECASE
        )
        
        if not match:
            return ""
            
        try:
            data = json.loads(match.group(1))
            return self._extract_from_next_data(data)
        except Exception:
            return ""
    
    def _extract_from_next_data(self, data: Dict[str, Any]) -> str:
        """Extract content from common Next.js data structures."""
        try:
            # Try common paths
            props = data.get("props", {})
            page_props = props.get("pageProps", {})
            
            # Look for source.source pattern
            if "source" in page_props and isinstance(page_props["source"], dict):
                source_content = page_props["source"].get("source", "")
                if source_content and isinstance(source_content, str):
                    return source_content
                    
            # Look for content field
            content = page_props.get("content", "")
            if content and isinstance(content, str):
                return content
                
            return ""
        except Exception:
            return ""
    
    def get_priority(self) -> int:
        return 80


class RSCStreamStrategy(ExtractionStrategy):
    """Strategy for React Server Components streaming format."""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "_rsc=" in (url or "") or re.search(r'^[0-9]+:', html[:1000], re.MULTILINE)
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from RSC stream format."""
        lines = html.split('\n')
        content_lines = []
        
        for line in lines:
            # RSC stream lines typically start with numbers
            if re.match(r'^[0-9]+:', line):
                # Extract JSON payload if present
                try:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        payload = parts[1].strip()
                        if payload.startswith('"') and payload.endswith('"'):
                            decoded = json.loads(payload)
                            if self._is_meaningful_content(decoded):
                                content_lines.append(decoded)
                except Exception:
                    pass
                    
        return "\n\n".join(content_lines) if content_lines else ""
    
    def _is_meaningful_content(self, content: str) -> bool:
        """Determine if content is meaningful rather than framework noise"""
        if not content or len(content) < ExtractionConfig.MIN_CHUNK_LENGTH:
            return False
        return any(marker in content for marker in ExtractionConfig.CONTENT_MARKERS)
    
    def get_priority(self) -> int:
        return 85


class FallbackHTMLStrategy(ExtractionStrategy):
    """Fallback strategy extracting from HTML title/meta tags."""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return True  # Always processable as fallback
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract basic content from HTML title and meta tags"""
        result = []
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            result.append(f"# {title_match.group(1).strip()}")
            
        # Extract meta description
        meta_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]*)', 
            html, 
            re.IGNORECASE
        )
        if meta_match:
            result.append(f"\n{meta_match.group(1).strip()}")
            
        # Extract twitter:description
        twitter_match = re.search(
            r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\'>]*)', 
            html, 
            re.IGNORECASE
        )
        if twitter_match and not meta_match:
            result.append(f"\n{twitter_match.group(1).strip()}")
            
        return "\n".join(result) if result else "# Content extraction failed"
    
    def get_priority(self) -> int:
        return 10  # Lowest priority (fallback)


# ============================================================================
# STRATEGY MANAGER (6-month maintenance focal point)
# ============================================================================

class StrategyManager:
    """Dynamic extraction strategy selection and management class.
    
    Maintenance notes (for yourself in 6 months):
    - Adding default strategies: Append to _register_default_strategies()  
    - Disabling failing strategies: Use disable_strategy()
    - Adjusting priorities: Modify get_priority() in each strategy
    - Monitoring results: Add statistics collection as needed
    """
    
    def __init__(self):
        self.strategies: List[ExtractionStrategy] = []
        self.disabled_strategies: set = set()
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default extraction strategies
        
        Maintenance note (for yourself in 6 months): Add new strategies here
        """
        self.add_strategy(NextJSPushStrategy())
        self.add_strategy(NextJSDataStrategy())
        self.add_strategy(RSCStreamStrategy())
        self.add_strategy(FallbackHTMLStrategy())
    
    def add_strategy(self, strategy: ExtractionStrategy):
        """Add a new extraction strategy"""
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: s.get_priority(), reverse=True)
    
    def disable_strategy(self, strategy_name: str):
        """Disable strategy by name"""
        self.disabled_strategies.add(strategy_name)
    
    def enable_strategy(self, strategy_name: str):
        """Re-enable a disabled strategy"""
        self.disabled_strategies.discard(strategy_name)
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content using the best available strategy"""
        strategies = self.strategies
        
        # Try strategies in priority order
        for strategy in strategies:
            name = strategy.get_name()
            
            if name in self.disabled_strategies:
                continue
                
            if strategy.can_handle(html, url):
                result = self._try_extract(strategy, html, url)
                if result.strip():  # Non-empty result
                    return result
                    
        return "# No suitable extraction strategy found"
    
    def _try_extract(self, strategy: ExtractionStrategy, html: str, url: str = None) -> str:
        """Try extraction with specific strategy, update statistics/logs as needed"""
        try:
            return strategy.extract_content(html, url)
        except Exception as e:
            logging.warning(f"Strategy {strategy.get_name()} failed: {e}")
            return ""


# ============================================================================
# CORE CLASSES
# ============================================================================

class HTTPClient:
    """HTTP communication handling class
    
    Maintenance notes (for yourself in 6 months):
    - Add proxy support to __init__
    - Implement authentication in _create_request()
    - Add caching layer to fetch_url()
    """
    
    def __init__(self, timeout: float = None, headers: Dict[str, str] = None):
        self.timeout = timeout or HTTPConfig.DEFAULT_TIMEOUT
        self.headers = headers or HTTPConfig.DEFAULT_HEADERS.copy()
    
    def fetch_url(self, url: str) -> str:
        """Fetch HTML from URL (with error handling)"""
        if not self._is_valid_url(url):
            raise HTTPError(url, 0, "Invalid URL format")
            
        request = self._create_request(url)
        
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return self._process_response(response)
        except Exception as e:
            raise HTTPError(url, 0, str(e))
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and security"""
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    
    def _create_request(self, url: str) -> Request:
        """Create HTTP request with appropriate headers"""
        return Request(url, headers=self.headers)
    
    def _process_response(self, response) -> str:
        """Process HTTP response and decode considering encoding.
        
        Keep nesting shallow by separating decompression into small functions,
        ensuring readability with early returns (guard clauses).
        """
        data = response.read()

        def _decompress(data_bytes: bytes, enc: str) -> bytes:
            enc = (enc or "").lower().strip()
            if not enc:
                return data_bytes


            # gzip / x-gzip
            if enc in ("gzip", "x-gzip"):
                try:
                    import gzip
                    return gzip.decompress(data_bytes)
                except Exception:
                    return data_bytes

            # deflate (zlib/raw)
            if enc == "deflate":
                try:
                    import zlib
                    return zlib.decompress(data_bytes)
                except Exception:
                    try:
                        import zlib as _z
                        return _z.decompress(data_bytes, -_z.MAX_WBITS)
                    except Exception:
                        return data_bytes

            return data_bytes

        # Handle compression
        data = _decompress(data, response.headers.get("Content-Encoding"))

        # Determine charset
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")


class OutputFormatter:
    """Output formatter supporting multiple formats
    
    Maintenance note (for yourself in 6 months):
    - Add JSON output to format_content()
    - Consider YAML output support
    - Support for custom templates
    """
    
    def __init__(self, format_type: str = "markdown"):
        self.format_type = format_type
    
    def format_content(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Format content based on specified type"""
        if self.format_type == "markdown":
            return self._format_markdown(content, metadata)
        else:
            return content
    
    def _format_markdown(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Format as Markdown (metadata is optional)"""
        result = []
        
        if metadata:
            result.append("---")
            for key, value in metadata.items():
                result.append(f"{key}: {value}")
            result.append("---")
            result.append("")
        
        result.append(content)
        return "\n".join(result)


def save_markdown_to_library(md: str, source_url: str, base_dir: str = ".deepwiki") -> Dict[str, Any]:
    """Split Markdown by H1 and save as files under .deepwiki/<username>/<library>/.
    
    - Also creates/overwrites a library index file: .deepwiki/<username>/<library>.md
    - Returns a dict with paths and metadata.
    - Raises ConfigError if source_url does not include /<username>/<library>.
    
    Parameters:
        md: The markdown content extracted from a DeepWiki/Next.js page.
        source_url: The original URL used for extraction (used to derive save path).
        base_dir: Base directory for saving outputs (default: ".deepwiki").
    
    Note:
        The source_url is normalized via normalize_deepwiki_url() so that
        path-like inputs such as "owner/repo" or "/owner/repo" also work.
        DeepWiki full URLs and non-DeepWiki full URLs are preserved as-is per policy.
    """
    if not source_url:
        raise ConfigError("source_url is required to determine save location")
    # Normalize according to shared policy (no-op for full deepwiki URLs and non-deepwiki URLs)
    normalized_url = normalize_deepwiki_url(source_url)
    try:
        parsed_url = urlparse(normalized_url)
    except Exception as e:
        raise ConfigError(f"Invalid source_url: {e}")
    path_parts = [p for p in (parsed_url.path or "").split('/') if p]
    if len(path_parts) < 2:
        raise ConfigError("source_url must include '/<username>/<library>' path components")
    username, library_name = path_parts[0], path_parts[1]

    output_dir = os.path.join(base_dir, username, library_name)
    os.makedirs(output_dir, exist_ok=True)

    sections = split_markdown_by_h1(md)
    saved_files: List[str] = []
    for section in sections:
        title = section["title"]
        section_content = section["content"]
        filename = sanitize_filename(title) + ".md"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(section_content)
        saved_files.append(file_path)

    library_file_path = os.path.join(base_dir, username, f"{library_name}.md")
    with open(library_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {library_name} Documentation Index\n\n")
        f.write("This file contains links to all extracted documents.\n")
        f.write("Please refer to the files below for detailed information.\n\n")
        for file_path in saved_files:
            filename = os.path.basename(file_path)
            title = filename[:-3].replace('_', ' ')
            f.write(f"- [{title}]({library_name}/{filename})\n")

    logging.info("Saved %d sections under %s", len(saved_files), output_dir)
    return {
        "username": username,
        "library_name": library_name,
        "output_dir": output_dir,
        "saved_files": saved_files,
        "library_file": library_file_path,
    }


class ContentExtractor:
    """Content extraction orchestrator."""
    
    def __init__(self, strategy_manager: StrategyManager = None, 
                 http_client: HTTPClient = None):
        self.strategy_manager = strategy_manager or StrategyManager()
        self.http_client = http_client or HTTPClient()
    
    def extract_from_url(self, url: str) -> str:
        """Extract content from URL."""
        normalized = normalize_deepwiki_url(url)
        html = self.http_client.fetch_url(normalized)
        return self.extract_from_html(html, normalized)
    
    def extract_from_html(self, html: str, url: str = None) -> str:
        """Extract content from HTML string."""
        raw_content = self.strategy_manager.extract_content(html, url)
        metadata = {"extraction_url": url} if url else None
        formatter = OutputFormatter()
        return formatter.format_content(raw_content, metadata)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """Backward-compatible entrypoint that delegates to cli.main()."""
    from cli import main as cli_main
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())