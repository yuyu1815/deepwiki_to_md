"""
HTML to Markdown Converter for DeepWiki to Markdown Converter

This module provides functionality for converting HTML content to Markdown format.
"""

import logging
import re
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
from markdownify import markdownify

from deepwiki_to_md.utils.error_handler import log_execution_time

logger = logging.getLogger(__name__)


class HTMLToMarkdownConverter:
    """
    Converter for transforming HTML content to Markdown.
    
    This class provides methods for converting HTML to Markdown with customizable options.
    """

    def __init__(self, **options):
        """
        Initialize the converter with options.
        
        Args:
            **options: Options to pass to the markdownify function
        """
        self.options = {
            'heading_style': 'ATX',  # Use # style headings
            'strip': ['script', 'style'],  # Remove script and style tags
            'convert': ['a', 'img', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'code', 'pre',
                        'blockquote', 'table', 'tr', 'td', 'th'],
            'escape_asterisks': True,
            'escape_underscores': True
        }

        # Update with user-provided options
        self.options.update(options)

    def convert(self, html: str) -> str:
        """
        Convert HTML to Markdown.
        
        Args:
            html (str): HTML content to convert
            
        Returns:
            str: Converted Markdown content
        """
        # Clean HTML before conversion
        cleaned_html = self._clean_html(html)

        # Convert to Markdown
        markdown = markdownify(cleaned_html, **self.options)

        # Post-process Markdown
        processed_markdown = self._post_process_markdown(markdown)

        return processed_markdown

    def _clean_html(self, html: str) -> str:
        """
        Clean HTML before conversion.
        
        Args:
            html (str): HTML content to clean
            
        Returns:
            str: Cleaned HTML content
        """
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        for tag_name in self.options.get('strip', []):
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        return str(soup)

    def _post_process_markdown(self, markdown: str) -> str:
        """
        Post-process Markdown after conversion.
        
        Args:
            markdown (str): Converted Markdown content
            
        Returns:
            str: Post-processed Markdown content
        """
        # Fix consecutive newlines (more than 2)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Fix code blocks (ensure proper spacing)
        markdown = re.sub(r'```(\w+)\n', r'```\1\n', markdown)

        # Fix list items (ensure proper spacing)
        markdown = re.sub(r'(\n[*-] .*\n)([*-] )', r'\1\n\2', markdown)

        return markdown.strip()


@log_execution_time
def convert_html_to_markdown(html: str, **options) -> str:
    """
    Convert HTML content to Markdown.
    
    Args:
        html (str): HTML content to convert
        **options: Options to pass to the converter
        
    Returns:
        str: Converted Markdown content
    """
    converter = HTMLToMarkdownConverter(**options)
    return converter.convert(html)


def extract_title_from_html(html: str) -> Optional[str]:
    """
    Extract title from HTML content.
    
    Args:
        html (str): HTML content to extract title from
        
    Returns:
        Optional[str]: Extracted title or None if not found
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Try to get title from title tag
        title_tag = soup.title
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # Try to get title from first h1
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.text:
            return h1_tag.text.strip()

        # Try to get title from first h2
        h2_tag = soup.find('h2')
        if h2_tag and h2_tag.text:
            return h2_tag.text.strip()

        return None

    except Exception as e:
        logger.error(f"Error extracting title from HTML: {str(e)}")
        return None
