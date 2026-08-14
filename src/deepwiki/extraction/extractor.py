from typing import Optional

from deepwiki.core.utils import normalize_deepwiki_url
from deepwiki.extraction.http_client import HTTPClient
from deepwiki.extraction.strategies import StrategyManager
from deepwiki.output.formatter import OutputFormatter


class ContentExtractor:
    """Content extraction orchestrator."""

    def __init__(
        self,
        strategy_manager: Optional[StrategyManager] = None,
        http_client: Optional[HTTPClient] = None,
    ) -> None:
        self.strategy_manager = strategy_manager or StrategyManager()
        self.http_client = http_client or HTTPClient()

    def extract_from_url(self, url: str) -> str:
        """Extract content from URL."""
        normalized = normalize_deepwiki_url(url)
        html = self.http_client.fetch_url(normalized)
        return self.extract_from_html(html, normalized)

    def extract_from_html(self, html: str, url: Optional[str] = None) -> str:
        """Extract content from HTML string."""
        raw_content = self.strategy_manager.extract_content(html, url)
        metadata = {"extraction_url": url} if url else None
        formatter = OutputFormatter()
        return formatter.format_content(raw_content, metadata)
