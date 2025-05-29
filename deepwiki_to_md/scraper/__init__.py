"""
Scraper Module for DeepWiki to Markdown Converter

This module provides functionality for scraping content from DeepWiki sites.
"""

from deepwiki_to_md.scraper.base_scraper import BaseScraper
from deepwiki_to_md.scraper.deepwiki_scraper import DeepwikiScraper
from deepwiki_to_md.scraper.direct_markdown_scraper import DirectMarkdownScraper

__all__ = ["BaseScraper", "DeepwikiScraper", "DirectMarkdownScraper"]
