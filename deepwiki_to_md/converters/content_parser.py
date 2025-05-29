"""
Content Parser for DeepWiki to Markdown Converter

This module provides functionality for parsing Markdown content.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_markdown_content(markdown: str) -> List[Dict[str, Any]]:
    """
    Parse Markdown content into a structured format.

    Args:
        markdown (str): Markdown content to parse

    Returns:
        List[Dict[str, Any]]: Parsed content as a list of elements
    """
    # Split content into lines
    lines = markdown.split('\n')

    # Parse lines into elements
    elements = []
    current_element = None

    for line in lines:
        # Check for headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            elements.append({
                'type': 'heading',
                'level': level,
                'text': text
            })
            current_element = None
            continue

        # Check for list items
        list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
        if list_match:
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            text = list_match.group(3).strip()

            list_type = 'unordered' if marker in ['-', '*', '+'] else 'ordered'

            elements.append({
                'type': 'list_item',
                'list_type': list_type,
                'indent': indent,
                'text': text
            })
            current_element = None
            continue

        # Check for code blocks
        if line.startswith('```'):
            if current_element and current_element['type'] == 'code_block':
                # End of code block
                current_element = None
            else:
                # Start of code block
                language = line[3:].strip()
                current_element = {
                    'type': 'code_block',
                    'language': language,
                    'content': []
                }
                elements.append(current_element)
            continue

        # Add line to current code block
        if current_element and current_element['type'] == 'code_block':
            current_element['content'].append(line)
            continue

        # Check for blank lines
        if not line.strip():
            if current_element and current_element['type'] == 'paragraph':
                current_element = None
            continue

        # Default: paragraph text
        if current_element and current_element['type'] == 'paragraph':
            current_element['text'] += '\n' + line
        else:
            current_element = {
                'type': 'paragraph',
                'text': line
            }
            elements.append(current_element)

    # Post-process elements
    return _post_process_elements(elements)


def _post_process_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Post-process parsed elements.

    Args:
        elements (List[Dict[str, Any]]): Parsed elements

    Returns:
        List[Dict[str, Any]]: Post-processed elements
    """
    # Join code block content
    for element in elements:
        if element['type'] == 'code_block':
            element['content'] = '\n'.join(element['content'])

    # Group list items into lists
    processed_elements = []
    current_list = None

    for element in elements:
        if element['type'] == 'list_item':
            if not current_list or current_list['type'] != element['list_type']:
                # Start a new list
                current_list = {
                    'type': 'list',
                    'list_type': element['list_type'],
                    'items': []
                }
                processed_elements.append(current_list)

            # Add item to the current list
            current_list['items'].append({
                'text': element['text'],
                'indent': element['indent']
            })
        else:
            # Non-list element
            current_list = None
            processed_elements.append(element)

    return processed_elements


def extract_metadata(markdown: str) -> Dict[str, Any]:
    """
    Extract metadata from Markdown content.

    This function looks for YAML frontmatter or other metadata patterns.

    Args:
        markdown (str): Markdown content to extract metadata from

    Returns:
        Dict[str, Any]: Extracted metadata
    """
    metadata = {}

    # Check for YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', markdown, re.DOTALL)
    if frontmatter_match:
        try:
            import yaml
            frontmatter_text = frontmatter_match.group(1)

            # Parse the frontmatter manually to keep dates as strings
            for line in frontmatter_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    metadata[key] = value
        except Exception as e:
            logger.warning(f"Error parsing YAML frontmatter: {str(e)}")

    # Extract title from first heading if not already set
    if 'title' not in metadata:
        title_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()

    # Extract other metadata patterns (e.g., key: value)
    metadata_pattern = r'^([A-Za-z0-9_-]+):\s*(.+)$'
    for match in re.finditer(metadata_pattern, markdown, re.MULTILINE):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()

        # Don't overwrite existing metadata
        if key not in metadata:
            metadata[key] = value

    return metadata


def extract_sections(markdown: str) -> Dict[str, Any]:
    """
    Extract sections from Markdown content based on headings.

    Args:
        markdown (str): Markdown content to extract sections from

    Returns:
        Dict[str, Any]: Dictionary of section title to section content
    """
    # Remove YAML frontmatter if present
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', markdown, flags=re.DOTALL)

    # Find all headings
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    headings = list(re.finditer(heading_pattern, content, re.MULTILINE))

    # If no headings found, return empty sections
    if not headings:
        return {}

    # Extract sections
    sections = {}

    for i, match in enumerate(headings):
        # Get heading info
        level = len(match.group(1))
        title = match.group(2).strip()
        start_pos = match.end()

        # Determine end position (start of next heading or end of content)
        if i < len(headings) - 1:
            end_pos = headings[i + 1].start()
        else:
            end_pos = len(content)

        # Extract section content
        section_content = content[start_pos:end_pos].strip()

        # Add to sections dictionary
        sections[title] = section_content

    return sections
