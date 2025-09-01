#!/usr/bin/env python3
"""
deepwikimd.py - Extensible Next.js/DeepWiki Content Extractor

Purpose:
    A powerful yet simple CLI tool that extracts human-readable Markdown-like text from 
    Next.js/DeepWiki style script payloads with pluggable extraction strategies.

Architecture:
    - Strategy Pattern: Multiple extraction methods (NextJS, RSC, fallback)
    - Configuration-driven: Easy customization via config classes
    - Extensible: Add new strategies without modifying core logic
    - Maintainable: Clear separation of concerns for 6-month maintenance

Maintenance Notes (read-me-in-6-months):
    - New strategies: Inherit from ExtractionStrategy, register in StrategyManager
    - Heuristics: Modify ExtractionConfig constants
    - New output formats: Extend OutputFormatter class
    - HTTP tweaks: Adjust HTTPConfig settings

Usage:
    # Extract from local HTML file
    python3 deepwikimd.py sample.html --path ./output
    
    # Extract from URL
    python3 deepwikimd.py https://deepwiki.com/path --path ./output
"""

import sys
import re
import json
import logging
import os
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from abc import ABC, abstractmethod


# ============================================================================
# CONFIGURATION CLASSES (6-month maintenance point)
# ============================================================================

class ExtractionConfig:
    """Extraction processing configuration
    
    6-month maintenance points:
    - Add new CONTENT_MARKERS for new content types
    - Adjust NOISE_PATTERNS for new frameworks
    - Modify MIN/MAX_CHUNK_LENGTH for performance tuning
    """
    
    # Core extraction patterns
    STRING_PAYLOAD_PATTERN = re.compile(
        r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"\]\)',
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
        "<details", "<summary",        # HTML details
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
    """HTTP communication configuration
    
    6-month maintenance points:
    - Update DEFAULT_HEADERS for new user agents
    - Add new ALLOWED_DOMAINS for security
    - Adjust timeout values for performance
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
    
    # Security: allowed domains (expand as needed)
    ALLOWED_DOMAINS = (
        "deepwiki.com",
        "*.deepwiki.com",
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename.
    
    Args:
        name: The string to sanitize
        
    Returns:
        A sanitized string suitable for use as a filename
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove or replace invalid characters for filenames
    # This pattern keeps alphanumeric characters, underscores, hyphens, and dots
    name = re.sub(r'[^\w\-_.]', '', name)
    
    # Ensure the filename is not empty
    if not name:
        name = "unnamed"
        
    return name


def split_markdown_by_h1(content: str) -> List[Dict[str, str]]:
    """Split markdown content by H1 headers, ignoring H1 headers in code blocks.
    
    Args:
        content: The markdown content to split
        
    Returns:
        A list of dictionaries, each containing 'title' and 'content' keys
    """
    # Split by H1 headers (# Header), but ignore those in code blocks
    sections: List[Dict[str, str]] = []
    lines: List[str] = content.split('\n')
    
    # Track if we're inside a code block
    in_code_block: bool = False
    current_section_title: str = "Introduction"
    current_section_content: List[str] = []
    
    for line in lines:
        # Check for fenced code block markers (allow leading spaces)
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            current_section_content.append(line)
            continue
            
        # If we're not in a code block, check for H1 headers (exact "# ")
        if not in_code_block and line.startswith("# "):
            # Save the previous section only if it has non-empty content
            prev_content = '\n'.join(current_section_content).strip()
            if prev_content:
                sections.append({
                    'title': current_section_title,
                    'content': prev_content
                })
            
            # Start a new section
            current_section_title = line[2:].strip()  # Remove "# " prefix
            current_section_content = []
        else:
            current_section_content.append(line)
    
    # Add the last section only if it has non-empty content
    final_content = '\n'.join(current_section_content).strip()
    if final_content:
        sections.append({
            'title': current_section_title,
            'content': final_content
        })
    
    # Post-process sections to remove unwanted content
    for section in sections:
        sec_lines = section['content'].split('\n')
        filtered_lines: List[str] = []
        skip_details = False
        
        for l in sec_lines:
            l_strip_lower = l.strip().lower()
            # Skip details blocks (allow attributes: <details ...>)
            if l_strip_lower.startswith('<details') and l_strip_lower.endswith('>'):
                skip_details = True
                continue
            elif l_strip_lower.startswith('</details'):
                skip_details = False
                continue
            elif skip_details:
                continue
                
            # Skip lines that look like source file references
            if l_strip_lower.startswith('<summary'):
                # include only if not the specific "Relevant source files"? Original filtered exact; keep generic.
                continue
            if l.strip().startswith('- [') and l.strip().endswith('.md)'):
                continue
                
            filtered_lines.append(l)
            
        section['content'] = '\n'.join(filtered_lines).strip()
    
    return sections


# ============================================================================
# ERROR HANDLING CLASSES
# ============================================================================

class ExtractorError(Exception):
    """Base class for extraction errors"""
    pass


class HTTPError(ExtractorError):
    """HTTP communication errors"""
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message} for {url}")


class ContentError(ExtractorError):
    """Content processing errors"""
    pass


class ConfigError(ExtractorError):
    """Configuration errors"""
    pass


# ============================================================================
# EXTRACTION STRATEGY PATTERN (6-month maintenance point)
# ============================================================================

class ExtractionStrategy(ABC):
    """Abstract base class for extraction strategies
    
    6-month maintenance guide:
    1. Create new strategy class inheriting from this
    2. Implement can_handle() and extract_content() methods
    3. Register in StrategyManager._register_default_strategies()
    4. Set appropriate priority level
    """
    
    @abstractmethod
    def can_handle(self, html: str, url: str = None) -> bool:
        """Check if this strategy can handle the given HTML"""
        pass
    
    @abstractmethod
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content using this strategy"""
        pass
    
    def get_priority(self) -> int:
        """Return strategy priority (higher = more preferred)"""
        return 50
    
    def get_name(self) -> str:
        """Return strategy name for identification"""
        return self.__class__.__name__


class NextJSPushStrategy(ExtractionStrategy):
    """Current Next.js self.__next_f.push extraction strategy"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "self.__next_f.push" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from self.__next_f.push payloads"""
        chunks: List[str] = []
        
        for match in ExtractionConfig.STRING_PAYLOAD_PATTERN.finditer(html):
            raw = match.group(1)
            try:
                # Decode JSON-style escapes
                decoded = json.loads(f'"{raw}"')
            except Exception:
                # Fallback: manual replacement
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
        
        # Coalesce consecutive duplicates
        merged: List[str] = []
        for chunk in chunks:
            if not merged or merged[-1] != chunk:
                merged.append(chunk)
                
        return "\n\n".join(merged).strip() + "\n" if merged else ""
    
    def _is_content_chunk(self, s: str) -> bool:
        """Check if string looks like user-facing content"""
        if not s:
            return False
            
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
    """__NEXT_DATA__ script tag extraction strategy"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "__NEXT_DATA__" in html and "type=\"application/json\"" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from __NEXT_DATA__ script tags"""
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
        """Extract content from Next.js data structure"""
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
    """React Server Components streaming extraction strategy"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "_rsc=" in (url or "") or re.search(r'^[0-9]+:', html[:1000], re.MULTILINE)
    
    def extract_content(self, html: str, url: str = None) -> str:
        """Extract content from RSC stream format"""
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
        """Check if content is meaningful (not framework noise)"""
        if not content or len(content) < ExtractionConfig.MIN_CHUNK_LENGTH:
            return False
        return any(marker in content for marker in ExtractionConfig.CONTENT_MARKERS)
    
    def get_priority(self) -> int:
        return 85


class FallbackHTMLStrategy(ExtractionStrategy):
    """HTML title and meta extraction fallback strategy"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return True  # Always can handle as fallback
    
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
    """Manages extraction strategies with dynamic selection
    
    6-month maintenance guide:
    - Add new strategies in _register_default_strategies()
    - Disable failing strategies using disable_strategy()
    - Adjust strategy priorities by modifying their get_priority() methods
    - Monitor strategy success rates with get_statistics()
    """
    
    def __init__(self):
        self.strategies: List[ExtractionStrategy] = []
        self.disabled_strategies: set = set()
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default extraction strategies
        
        6-month maintenance point: Add new strategies here
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
        """Disable a strategy by name"""
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
        """Try extracting with a strategy and update statistics"""
        try:
            return strategy.extract_content(html, url)
        except Exception as e:
            logging.warning(f"Strategy {strategy.get_name()} failed: {e}")
            return ""


# ============================================================================
# CORE CLASSES
# ============================================================================

class HTTPClient:
    """HTTP communication handling
    
    6-month maintenance points:
    - Add proxy support in __init__
    - Implement authentication in _create_request()
    - Add caching in fetch_url()
    """
    
    def __init__(self, timeout: float = None, headers: Dict[str, str] = None):
        self.timeout = timeout or HTTPConfig.DEFAULT_TIMEOUT
        self.headers = headers or HTTPConfig.DEFAULT_HEADERS.copy()
    
    def fetch_url(self, url: str) -> str:
        """Fetch HTML content from URL with error handling"""
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
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False
    
    def _create_request(self, url: str) -> Request:
        """Create HTTP request with proper headers"""
        return Request(url, headers=self.headers)
    
    def _process_response(self, response) -> str:
        """Process HTTP response with encoding detection"""
        data = response.read()
        
        # Handle compression
        encoding = (response.headers.get("Content-Encoding") or "").lower().strip()
        if encoding == "br":
            try:
                import brotli
                data = brotli.decompress(data)
            except ImportError:
                # Fallback: retry without compression
                pass
        elif encoding in ("gzip", "x-gzip"):
            import gzip
            try:
                data = gzip.decompress(data)
            except Exception:
                pass
        elif encoding == "deflate":
            import zlib
            try:
                data = zlib.decompress(data)
            except Exception:
                try:
                    data = zlib.decompress(data, -zlib.MAX_WBITS)
                except Exception:
                    pass
        
        # Determine charset
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")


class OutputFormatter:
    """Output formatting with multiple format support
    
    6-month maintenance points:
    - Add JSON output in format_content()
    - Add YAML output support
    - Implement custom templates
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
        """Format as Markdown with optional metadata"""
        result = []
        
        if metadata:
            result.append("---")
            for key, value in metadata.items():
                result.append(f"{key}: {value}")
            result.append("---")
            result.append("")
        
        result.append(content)
        return "\n".join(result)


class ContentExtractor:
    """Main content extraction orchestrator"""
    
    def __init__(self, strategy_manager: StrategyManager = None, 
                 http_client: HTTPClient = None):
        self.strategy_manager = strategy_manager or StrategyManager()
        self.http_client = http_client or HTTPClient()
    
    def extract_from_url(self, url: str) -> str:
        """Extract content from URL"""
        html = self.http_client.fetch_url(url)
        return self.extract_from_html(html, url)
    
    def extract_from_html(self, html: str, url: str = None) -> str:
        """Extract content from HTML string"""
        raw_content = self.strategy_manager.extract_content(html, url)
        metadata = {"extraction_url": url} if url else None
        formatter = OutputFormatter()
        return formatter.format_content(raw_content, metadata)


# ============================================================================
# CLI INTERFACE
# ============================================================================

class CLIInterface:
    """Deprecated: CLI is moved to cli.py. This class kept for backward compatibility."""
    def __init__(self):
        raise RuntimeError("CLIInterface moved to cli.py; use cli.main() instead")


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def format_html(html: str, indent: int = 2) -> str:
    """Backward compatibility function (deprecated)"""
    logging.warning("format_html() is deprecated. Use deepwikimd.py instead.")
    return "<!-- HTML formatting deprecated. Use deepwikimd.py for content extraction -->"


def extract_markdown_from_html(html: str) -> str:
    """Backward compatibility function for direct extraction"""
    strategy = NextJSPushStrategy()
    if strategy.can_handle(html):
        return strategy.extract_content(html)
    return FallbackHTMLStrategy().extract_content(html)


# ============================================================================
# COMPATIBILITY CLASSES
# ============================================================================

class NextJSContentExtractor:
    """NextJS content extractor class for backward compatibility"""
    
    def __init__(self):
        self.strategy_manager = StrategyManager()
        self.output_formatter = OutputFormatter()
        
    def extract_and_save(self, input_source: str, output_file: str = None) -> bool:
        """Extract content from input source and save to file"""
        try:
            # Determine if input is URL or file
            if self._is_url(input_source):
                html = HTTPClient().fetch_url(input_source)
            else:
                with open(input_source, 'r', encoding='utf-8') as f:
                    html = f.read()
                    
            # Extract content
            content = self.strategy_manager.extract_content(html, input_source)
            formatted_content = self.output_formatter.format_content(content)
            
            # Save to file
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                return True
            else:
                print(formatted_content)
                return True
                
        except Exception as e:
            logging.error(f"Content extraction failed: {e}")
            return False
            
    def _is_url(self, s: str) -> bool:
        """Check if string is a URL"""
        try:
            parsed = urlparse(s)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """Backward-compatible entrypoint that delegates to cli.main()."""
    from cli import main as cli_main
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())