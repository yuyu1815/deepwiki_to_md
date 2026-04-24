import json
import re
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from deepwiki.core.config import ExtractionConfig
from deepwiki.core.errors import ContentError


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
        return "_rsc=" in (url or "") or bool(re.search(r'^[0-9]+:', html[:1000], re.MULTILINE))

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
