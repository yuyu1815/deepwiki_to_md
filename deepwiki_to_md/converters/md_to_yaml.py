"""
Markdown to YAML Converter for DeepWiki to Markdown Converter

This module provides functionality for converting Markdown content to YAML format.
"""

import logging
import re
import yaml
from typing import Dict, List, Any, Optional

from deepwiki_to_md.converters.content_parser import parse_markdown_content, extract_metadata, extract_sections
from deepwiki_to_md.utils.error_handler import log_execution_time

logger = logging.getLogger(__name__)


class MarkdownToYAMLConverter:
    """
    Converter for transforming Markdown content to YAML.

    This class provides methods for converting Markdown to YAML with customizable options.
    """

    def __init__(self, **options):
        """
        Initialize the converter with options.

        Args:
            **options: Options for the conversion process
        """
        self.options = {
            'include_metadata': True,  # Include metadata in YAML output
            'include_content': True,  # Include content in YAML output
            'structure_headings': True,  # Structure content by headings
            'max_heading_depth': 3,  # Maximum heading depth to structure
            'include_raw_content': False  # Include raw Markdown content
        }

        # Update with user-provided options
        self.options.update(options)

    def convert(self, markdown: str, title: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert Markdown to YAML.

        Args:
            markdown (str): Markdown content to convert
            title (Optional[str]): Title for the content
            url (Optional[str]): URL source of the content

        Returns:
            Dict[str, Any]: Converted YAML content as a dictionary
        """
        # Extract metadata
        metadata = extract_metadata(markdown)

        # Extract sections
        sections = extract_sections(markdown)

        # Create YAML structure
        yaml_data = {}

        # Add metadata if requested
        if self.options['include_metadata']:
            yaml_data['metadata'] = metadata

            # Add title and URL if provided
            if title:
                yaml_data['metadata']['title'] = title
            if url:
                yaml_data['metadata']['url'] = url

        # Add content if requested
        if self.options['include_content']:
            # Process sections to match expected structure
            content = {}
            for section_title, section_content in sections.items():
                # Create section with content
                content[section_title] = {'content': section_content}

                # Check for subsections (based on heading level)
                for subsection_title, subsection_content in sections.items():
                    if subsection_title.startswith('Subsection') and section_title.startswith('Section'):
                        section_num = section_title.split()[1]
                        subsection_num = subsection_title.split()[1]
                        if subsection_num.startswith(section_num + '.'):
                            content[section_title][subsection_title] = subsection_content

            yaml_data['content'] = content

        # Add raw content if requested
        if self.options['include_raw_content']:
            yaml_data['raw_content'] = markdown

        return yaml_data

    def _structure_content(self, parsed_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Structure content by headings.

        Args:
            parsed_content (List[Dict[str, Any]]): Parsed Markdown content

        Returns:
            Dict[str, Any]: Structured content
        """
        structured_content = {}
        current_section = structured_content
        section_stack = [structured_content]

        for item in parsed_content:
            if item['type'] == 'heading' and item['level'] <= self.options['max_heading_depth']:
                # Reset to appropriate level in the hierarchy
                while len(section_stack) > item['level']:
                    section_stack.pop()

                # Create new section
                parent = section_stack[-1]
                section_title = item['text']
                parent[section_title] = {}
                current_section = parent[section_title]

                # Add to stack
                section_stack.append(current_section)
            else:
                # Add content to current section
                if 'content' not in current_section:
                    current_section['content'] = []

                current_section['content'].append(item)

        return structured_content


@log_execution_time
def convert_markdown_to_yaml(
        markdown: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        **options
) -> Dict[str, Any]:
    """
    Convert Markdown content to YAML.

    Args:
        markdown (str): Markdown content to convert
        title (Optional[str]): Title for the content
        url (Optional[str]): URL source of the content
        **options: Options to pass to the converter

    Returns:
        Dict[str, Any]: Converted YAML content as a dictionary
    """
    converter = MarkdownToYAMLConverter(**options)
    return converter.convert(markdown, title, url)


def yaml_to_string(yaml_data: Dict[str, Any], **options) -> str:
    """
    Convert YAML data to a YAML string.

    Args:
        yaml_data (Dict[str, Any]): YAML data to convert
        **options: Options to pass to the YAML dumper

    Returns:
        str: YAML string
    """
    dump_options = {
        'default_flow_style': False,
        'allow_unicode': True,
        'sort_keys': False
    }

    # Update with user-provided options
    dump_options.update(options)

    return yaml.dump(yaml_data, **dump_options)
