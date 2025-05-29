"""
Link Processing Utilities for DeepWiki to Markdown Converter

This module provides link processing utility functions for the DeepWiki to Markdown converter.
"""

import re
import logging
import os
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


def fix_markdown_links(content: str) -> str:
    """
    Fix Markdown links in content.
    
    This function replaces URLs in Markdown links with empty brackets,
    which is a common convention for some Markdown processors.
    
    Args:
        content (str): Markdown content to process
        
    Returns:
        str: Processed Markdown content
    """
    # Regular expression to match Markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    def replace_link(match):
        title = match.group(1)
        url = match.group(2)

        # Skip anchor links
        if url.startswith('#'):
            return match.group(0)

        # Replace URL with empty brackets
        return f"[{title}]()"

    # Replace links
    processed_content = re.sub(link_pattern, replace_link, content)

    return processed_content


def extract_links(content: str) -> List[Dict[str, str]]:
    """
    Extract links from Markdown content.
    
    Args:
        content (str): Markdown content to extract links from
        
    Returns:
        List[Dict[str, str]]: List of links with title and url
    """
    links = []

    # Regular expression to match Markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(link_pattern, content)

    for match in matches:
        title = match.group(1).strip()
        url = match.group(2).strip()

        # Skip empty or anchor links
        if not url or url.startswith('#'):
            continue

        links.append({
            "title": title,
            "url": url
        })

    return links


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normalize a URL.
    
    Args:
        url (str): URL to normalize
        base_url (Optional[str]): Base URL for resolving relative URLs
        
    Returns:
        str: Normalized URL
    """
    # Handle relative URLs
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)

    # Parse the URL
    parsed_url = urlparse(url)

    # Normalize the URL
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    # Add query parameters if present
    if parsed_url.query:
        normalized_url += f"?{parsed_url.query}"

    # Add fragment if present
    if parsed_url.fragment:
        normalized_url += f"#{parsed_url.fragment}"

    return normalized_url


def get_relative_path(target_path: str, base_path: str) -> str:
    """
    Get the relative path from base_path to target_path.
    
    Args:
        target_path (str): Target path
        base_path (str): Base path
        
    Returns:
        str: Relative path
    """
    # Convert to absolute paths
    target_abs = os.path.abspath(target_path)
    base_abs = os.path.abspath(base_path)

    # Get the relative path
    rel_path = os.path.relpath(target_abs, os.path.dirname(base_abs))

    # Convert to forward slashes for Markdown
    rel_path = rel_path.replace('\\', '/')

    return rel_path


def update_internal_links(content: str, file_mapping: Dict[str, str], current_file: str) -> str:
    """
    Update internal links in Markdown content.
    
    Args:
        content (str): Markdown content to update
        file_mapping (Dict[str, str]): Mapping from URLs to local file paths
        current_file (str): Path to the current file
        
    Returns:
        str: Updated Markdown content
    """
    # Regular expression to match Markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    def replace_link(match):
        title = match.group(1)
        url = match.group(2)

        # Skip anchor links
        if url.startswith('#'):
            return match.group(0)

        # Check if the URL is in the mapping
        if url in file_mapping:
            target_file = file_mapping[url]
            rel_path = get_relative_path(target_file, current_file)
            return f"[{title}]({rel_path})"

        # Keep external links as is
        return match.group(0)

    # Replace links
    updated_content = re.sub(link_pattern, replace_link, content)

    return updated_content
