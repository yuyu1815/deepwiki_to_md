import logging
import os
import re
import time

import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def markdown_to_yaml(markdown_content):
    """
    Convert Markdown content to YAML while preserving formatting.

    Args:
        markdown_content (str): The Markdown content to convert.

    Returns:
        str: The YAML content.
    """
    try:
        if not markdown_content:
            return None

        # Extract headers, links, and structure from Markdown
        headers = []
        links = []

        # Extract links using regex
        link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
        for match in link_pattern.finditer(markdown_content):
            text, url = match.groups()
            links.append({"text": text, "url": url})

        # Extract headers
        header_pattern = re.compile(r'^(#+)\s+(.*?)$', re.MULTILINE)
        for match in header_pattern.finditer(markdown_content):
            headers.append(match.group(2))

        # Count paragraphs (non-empty lines separated by empty lines)
        paragraphs = re.split(r'\n\s*\n', markdown_content)
        paragraphs_count = len([p for p in paragraphs if p.strip()])

        # Count lists (lines starting with -, *, or number.)
        list_pattern = re.compile(r'^\s*(?:[-*]|\d+\.)\s', re.MULTILINE)
        lists_count = len(re.findall(list_pattern, markdown_content))

        # Count tables (lines containing | character)
        table_pattern = re.compile(r'^\|.*\|$', re.MULTILINE)
        tables_count = len(re.findall(table_pattern, markdown_content))

        # Create structured data
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "title": headers[0] if headers else "No Title",
            "content": markdown_content,  # Preserve the full markdown content with formatting
            "links": links,
            "images": [],  # We could extract images too if needed
            "metadata": {
                "headers": headers,
                "paragraphs_count": paragraphs_count,
                "lists_count": lists_count,
                "tables_count": tables_count
            }
        }

        # Convert to YAML
        yaml_content = yaml.dump(data, allow_unicode=True, sort_keys=False)

        return yaml_content
    except Exception as e:
        logger.error(f"MarkdownからYAMLへの変換中にエラーが発生しました: {e}")
        logger.error(f"Error converting Markdown to YAML: {e}")
        return None


def html_to_markdown(html_content):
    """
    Convert HTML content to Markdown.

    Args:
        html_content (str): The HTML content to convert.

    Returns:
        str: The Markdown content.
    """
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Convert to Markdown using markdownify
        markdown_content = markdownify(str(soup), heading_style="ATX")

        return markdown_content
    except Exception as e:
        logger.error(f"HTMLからMarkdownへの変換中にエラーが発生しました: {e}")
        logger.error(f"Error converting HTML to Markdown: {e}")
        return None


def html_to_yaml(html_content):
    """
    Convert HTML content to YAML.

    Args:
        html_content (str): The HTML content to convert.

    Returns:
        str: The YAML content.
    """
    try:
        # First convert HTML to Markdown to preserve formatting
        markdown_content = html_to_markdown(html_content)

        # Then convert Markdown to YAML
        return markdown_to_yaml(markdown_content)
    except Exception as e:
        logger.error(f"HTMLからYAMLへの変換中にエラーが発生しました: {e}")
        logger.error(f"Error converting HTML to YAML: {e}")
        return None


def convert_md_file_to_yaml(md_file_path, output_dir=None):
    """
    Convert an existing Markdown file to YAML format.

    Args:
        md_file_path (str): Path to the Markdown file
        output_dir (str, optional): Directory to save the YAML file. If None, saves in the same directory as the Markdown file.

    Returns:
        str: Path to the created YAML file
    """
    try:
        # Read the Markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert to YAML
        yaml_content = markdown_to_yaml(markdown_content)

        if not yaml_content:
            logger.error("Failed to convert Markdown to YAML")
            return None

        # Determine output path
        if output_dir is None:
            output_dir = os.path.dirname(md_file_path)

        base_name = os.path.splitext(os.path.basename(md_file_path))[0]
        yaml_file_path = os.path.join(output_dir, f"{base_name}.yaml")

        # Save the YAML file
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        logger.info(f"Converted Markdown to YAML: {yaml_file_path}")
        return yaml_file_path
    except Exception as e:
        logger.error(f"Error converting Markdown file to YAML: {e}")
        return None
