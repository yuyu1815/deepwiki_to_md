"""
Direct Markdown Scraper for DeepWiki to Markdown Converter

This module provides functionality for directly scraping Markdown content from DeepWiki sites.
"""

import logging
import re
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from deepwiki_to_md.scraper.base_scraper import BaseScraper
from deepwiki_to_md.models.config import Config
from deepwiki_to_md.utils.error_handler import handle_request_error

logger = logging.getLogger(__name__)


class DirectMarkdownScraper(BaseScraper):
    """
    Scraper for directly extracting Markdown content from DeepWiki sites.
    
    This scraper assumes that the DeepWiki site provides Markdown content directly,
    without the need for HTML-to-Markdown conversion.
    """

    def __init__(self, config: Config):
        """
        Initialize the DirectMarkdownScraper.
        
        Args:
            config (Config): Configuration object containing scraper settings
        """
        super().__init__(config)
        self.session = requests.Session()
        self.visited_urls = set()

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape Markdown content directly from the DeepWiki site.
        
        Returns:
            List[Dict[str, Any]]: List of scraped content items
        """
        results = []

        # Start with the main URL
        main_url = self.config.url
        if not self._validate_url(main_url):
            logger.error(f"Invalid URL: {main_url}")
            return results

        # Process the main page
        logger.info(f"Scraping content from {main_url}")
        content = self._fetch_content(main_url)

        if content:
            # Process the main content
            result = {
                "url": main_url,
                "title": self._extract_title(content),
                "content": self._clean_content(content),
                "library": self.config.library_name
            }
            results.append(result)
            self.visited_urls.add(main_url)

            # Extract and process navigation links
            nav_items = self.extract_navigation(content)
            for nav_item in nav_items:
                if nav_item["url"] not in self.visited_urls:
                    # Recursively process navigation items
                    nav_results = self._process_navigation_item(nav_item)
                    results.extend(nav_results)

        return results

    def _process_navigation_item(self, nav_item: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Process a navigation item by scraping its content.
        
        Args:
            nav_item (Dict[str, str]): Navigation item with title and url
            
        Returns:
            List[Dict[str, Any]]: List of scraped content items
        """
        results = []
        url = nav_item["url"]

        if url in self.visited_urls:
            return results

        logger.debug(f"Processing navigation item: {nav_item['title']} ({url})")

        # Fetch content for the navigation item
        content = self._fetch_content(url)
        if content:
            # Process the content
            result = {
                "url": url,
                "title": nav_item["title"] or self._extract_title(content),
                "content": self._clean_content(content),
                "library": self.config.library_name
            }
            results.append(result)
            self.visited_urls.add(url)

            # Extract and process nested navigation links
            nested_nav_items = self.extract_navigation(content)
            for nested_item in nested_nav_items:
                if nested_item["url"] not in self.visited_urls:
                    nested_results = self._process_navigation_item(nested_item)
                    results.extend(nested_results)

        return results

    def _fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch content from the specified URL.
        
        Args:
            url (str): URL to fetch content from
            
        Returns:
            Optional[str]: Fetched content or None if an error occurred
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            handle_request_error(e, url)
            return None

    def _extract_title(self, content: str) -> str:
        """
        Extract title from the content.
        
        Args:
            content (str): Content to extract title from
            
        Returns:
            str: Extracted title or default title
        """
        # Try to extract title from the first heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback to a default title
        return "Untitled Document"

    def extract_navigation(self, content: str) -> List[Dict[str, str]]:
        """
        Extract navigation links from Markdown content.
        
        Args:
            content (str): Markdown content to extract navigation from
            
        Returns:
            List[Dict[str, str]]: List of navigation items with title and url
        """
        nav_items = []

        # Extract Markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, content)

        for match in matches:
            title = match.group(1).strip()
            url = match.group(2).strip()

            # Skip empty or anchor links
            if not url or url.startswith('#'):
                continue

            # Handle relative URLs
            if not url.startswith(('http://', 'https://')):
                url = urljoin(self.config.url, url)

            nav_items.append({
                "title": title,
                "url": url
            })

        return nav_items
