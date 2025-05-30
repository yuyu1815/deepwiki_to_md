"""
Markdown Link Fixing Module for DeepWiki to Markdown Converter

This module provides functionality for fixing Markdown links in files.
"""

import logging
import os
from typing import List

from deepwiki_to_md.utils.link_processor import fix_markdown_links as fix_links_in_content

logger = logging.getLogger(__name__)


def fix_markdown_links(directory: str) -> None:
    """
    Fix Markdown links in all Markdown files in the specified directory.
    
    This function processes all Markdown files in the specified directory,
    replacing URLs in Markdown links with empty brackets.
    
    Args:
        directory (str): Path to the directory containing Markdown files
    """
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return

    if not os.path.isdir(directory):
        logger.error(f"Not a directory: {directory}")
        return

    logger.info(f"Processing Markdown files in {directory}")

    # Find all Markdown files in the directory
    md_files = _find_markdown_files(directory)

    if not md_files:
        logger.warning(f"No Markdown files found in {directory}")
        return

    logger.info(f"Found {len(md_files)} Markdown files")

    # Process each file
    for md_file in md_files:
        _process_file(md_file)

    logger.info(f"Finished processing {len(md_files)} Markdown files")


def _find_markdown_files(directory: str) -> List[str]:
    """
    Find all Markdown files in the specified directory.
    
    Args:
        directory (str): Path to the directory to search
        
    Returns:
        List[str]: List of paths to Markdown files
    """
    md_files = []

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.md', '.markdown')):
            md_files.append(os.path.join(directory, filename))

    return md_files


def _process_file(file_path: str) -> None:
    """
    Process a single Markdown file.
    
    Args:
        file_path (str): Path to the Markdown file to process
    """
    logger.info(f"Processing file: {file_path}")

    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process the content
        processed_content = fix_links_in_content(content)

        # Write the processed content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        logger.info(f"Successfully processed {file_path}")

    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
