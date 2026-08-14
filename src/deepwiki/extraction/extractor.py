from typing import Any, Dict, List, Optional, Tuple

from deepwiki.core.utils import normalize_deepwiki_url
from deepwiki.extraction.http_client import HTTPClient
from deepwiki.extraction.strategies import StrategyManager
from deepwiki.output.formatter import OutputFormatter
from deepwiki.parsing.rsc import extract_structured_pages


class ContentExtractor:
    """Coordinate fetching, extraction, and output formatting."""

    def __init__(
        self,
        strategy_manager: Optional[StrategyManager] = None,
        http_client: Optional[HTTPClient] = None,
    ) -> None:
        self.strategy_manager = strategy_manager or StrategyManager()
        self.http_client = http_client or HTTPClient()

    def extract_from_url(self, url: str) -> str:
        markdown, _ = self.extract_document_from_url(url)
        return markdown

    def extract_document_from_url(
        self, url: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """Fetch once and return Markdown plus structured pages when available."""
        normalized = normalize_deepwiki_url(url)
        html = self.http_client.fetch_url(normalized)
        return self.extract_from_html(html, normalized), extract_structured_pages(html)

    def extract_pages_from_url(self, url: str) -> Optional[List[Dict[str, Any]]]:
        _, pages = self.extract_document_from_url(url)
        return pages

    def extract_from_html(self, html: str, url: Optional[str] = None) -> str:
        raw_content = self.strategy_manager.extract_content(html, url)
        metadata = {"extraction_url": url} if url else None
        return OutputFormatter().format_content(raw_content, metadata)
