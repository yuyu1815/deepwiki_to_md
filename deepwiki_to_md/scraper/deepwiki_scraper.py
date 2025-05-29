"""
DeepWiki Scraper for DeepWiki to Markdown Converter

This module provides the main scraper for DeepWiki sites, coordinating the scraping process.
"""

import logging
import os
from typing import Dict, List, Optional, Any

from deepwiki_to_md.scraper.base_scraper import BaseScraper
from deepwiki_to_md.scraper.direct_markdown_scraper import DirectMarkdownScraper
from deepwiki_to_md.models.config import Config
from deepwiki_to_md.utils.file_io import save_markdown_file
from deepwiki_to_md.utils.link_processor import fix_markdown_links

logger = logging.getLogger(__name__)


class DeepwikiScraper(BaseScraper):
    """
    Main scraper for DeepWiki sites.
    
    This class coordinates the scraping process, delegating to specialized scrapers
    and handling the saving of scraped content.
    """

    def __init__(self, config: Config):
        """
        Initialize the DeepwikiScraper.
        
        Args:
            config (Config): Configuration object containing scraper settings
        """
        super().__init__(config)
        self.direct_scraper = DirectMarkdownScraper(config)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape content from the DeepWiki site.
        
        This method coordinates the scraping process and saves the results.
        
        Returns:
            List[Dict[str, Any]]: List of scraped content items
        """
        logger.info(f"Starting scraping process for {self.config.library_name}")

        # Use the direct markdown scraper to get content
        results = self.direct_scraper.scrape()

        # Process and save the results
        processed_results = []
        for item in results:
            # Fix markdown links
            item["content"] = fix_markdown_links(item["content"])

            # Save the content to a file
            output_path = self._get_output_path(item)
            save_markdown_file(output_path, item["content"])

            # Add the file path to the result
            item["file_path"] = output_path
            processed_results.append(item)

            logger.info(f"Saved {item['title']} to {output_path}")

        logger.info(f"Scraping completed. Processed {len(processed_results)} documents.")
        return processed_results

    def extract_navigation(self, content: str) -> List[Dict[str, str]]:
        """
        Extract navigation links from content.
        
        This method delegates to the direct markdown scraper.
        
        Args:
            content (str): Content to extract navigation from
            
        Returns:
            List[Dict[str, str]]: List of navigation items with title and url
        """
        return self.direct_scraper.extract_navigation(content)

    def _get_output_path(self, item: Dict[str, Any]) -> str:
        """
        Get the output file path for a scraped item.
        
        Args:
            item (Dict[str, Any]): Scraped content item
            
        Returns:
            str: Output file path
        """
        # Create the output directory if it doesn't exist
        library_dir = os.path.join(self.config.output_dir, self.config.library_name)
        os.makedirs(library_dir, exist_ok=True)

        # Sanitize the title for use as a filename
        filename = self._sanitize_filename(item["title"])

        # Return the full path
        return os.path.join(library_dir, f"{filename}.md")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string for use as a filename.
        
        Args:
            filename (str): String to sanitize
            
        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit the length
        if len(filename) > 255:
            filename = filename[:255]

        return filename
