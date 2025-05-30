"""
Base Scraper for DeepWiki to Markdown Converter

This module provides the base abstract class for all scrapers.
"""

import abc
import logging
import re
from typing import Dict, List, Any

from deepwiki_to_md.models.config import Config

logger = logging.getLogger(__name__)


class BaseScraper(abc.ABC):
    """
    Abstract base class for all scrapers.

    This class defines the interface that all scrapers must implement.
    """

    def __init__(self, config: Config):
        """
        Initialize the scraper with configuration.

        Args:
            config (Config): Configuration object containing scraper settings
        """
        self.config = config
        logger.debug(f"Initialized {self.__class__.__name__} with config: {config}")

    @abc.abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape content from the source.

        This method must be implemented by all subclasses.

        Returns:
            List[Dict[str, Any]]: List of scraped content items
        """
        pass

    @abc.abstractmethod
    def extract_navigation(self, content: str) -> List[Dict[str, str]]:
        """
        Extract navigation links from content.

        Args:
            content (str): Content to extract navigation from

        Returns:
            List[Dict[str, str]]: List of navigation items with title and url
        """
        pass

    def _validate_url(self, url: str) -> bool:
        """
        Validate if the URL is properly formatted.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if URL is valid, False otherwise
        """
        # Basic validation - can be extended in subclasses
        return url.startswith(("http://", "https://"))

    def _clean_content(self, content: str) -> str:
        """
        Clean the scraped content.

        Args:
            content (str): Content to clean

        Returns:
            str: Cleaned content
        """
        # Basic cleaning - strip whitespace
        content = content.strip()

        # Remove specific patterns from the end of the content
        # These patterns are specific to DeepWiki sites and contain metadata or system information

        # Split content into lines
        lines = content.split('\n')

        # Find the index of the first line that matches any of the patterns
        cut_index = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            # Check for lines starting with "- Continued improvements"
            if re.match(r'^-\s+Continued improvements', line):
                cut_index = i
                break
            # Check for lines that are exactly "c:null"
            if line == 'c:null':
                cut_index = i
                break
            # Check for lines starting with digits followed by ":[["
            if re.match(r'^\d+:\[\[', line):
                cut_index = i
                break

        # Keep only the lines before the cut index
        cleaned_lines = lines[:cut_index]

        # Join the lines back into a string
        return '\n'.join(cleaned_lines)
