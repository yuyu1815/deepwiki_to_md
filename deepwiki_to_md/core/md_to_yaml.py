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
        # Convert HTML to Markdown first
        markdown_content = html_to_markdown(html_content)
        if not markdown_content:
            return None

        # Then convert Markdown to YAML
        yaml_content = markdown_to_yaml(markdown_content)
        return yaml_content
    except Exception as e:
        logger.error(f"HTMLからYAMLへの変換中にエラーが発生しました: {e}")
        logger.error(f"Error converting HTML to YAML: {e}")
        return None


def convert_md_file_to_yaml(md_file_path, output_dir=None):
    """
    Convert a Markdown file to YAML and save it.

    Args:
        md_file_path (str): The path to the Markdown file.
        output_dir (str, optional): The directory to save the YAML file. If None, save in the same directory.

    Returns:
        str: The path to the saved YAML file, or None if conversion failed.
    """
    try:
        if not os.path.isfile(md_file_path):
            logger.error(f"ファイルが存在しません: {md_file_path}")
            logger.error(f"File does not exist: {md_file_path}")
            return None

        # Read Markdown file
        with open(md_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Convert to YAML
        yaml_content = markdown_to_yaml(markdown_content)
        if not yaml_content:
            logger.error(f"ファイルの変換に失敗しました: {md_file_path}")
            logger.error(f"Failed to convert file: {md_file_path}")
            return None

        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(md_file_path)
        os.makedirs(output_dir, exist_ok=True)

        # Save YAML file
        yaml_file = os.path.splitext(os.path.basename(md_file_path))[0] + ".yaml"
        yaml_path = os.path.join(output_dir, yaml_file)
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        logger.info(f"ファイルを変換しました: {md_file_path} -> {yaml_path}")
        logger.info(f"Converted file: {md_file_path} -> {yaml_path}")
        return yaml_path
    except Exception as e:
        logger.error(f"ファイルの変換中にエラーが発生しました: {md_file_path} - {e}")
        logger.error(f"Error converting file: {md_file_path} - {e}")
        return None


def process_directory(directory, output_format="yaml"):
    """
    Process all Markdown files in a directory and convert them to YAML.

    Args:
        directory (str): The directory containing Markdown files.
        output_format (str): The output format (yaml or json).

    Returns:
        int: The number of files processed.
    """
    try:
        if not os.path.isdir(directory):
            logger.error(f"ディレクトリが存在しません: {directory}")
            logger.error(f"Directory does not exist: {directory}")
            return 0

        # Create output directory if it doesn't exist
        output_dir = os.path.join(directory, output_format)
        os.makedirs(output_dir, exist_ok=True)

        # Get all Markdown files in the directory
        markdown_files = [f for f in os.listdir(directory) if f.endswith(".md")]
        if not markdown_files:
            logger.warning(f"ディレクトリにMarkdownファイルが見つかりません: {directory}")
            logger.warning(f"No Markdown files found in directory: {directory}")
            return 0

        # Process each Markdown file
        processed_count = 0
        for markdown_file in markdown_files:
            try:
                # Read Markdown file
                markdown_path = os.path.join(directory, markdown_file)
                with open(markdown_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()

                # Convert to YAML
                yaml_content = markdown_to_yaml(markdown_content)
                if not yaml_content:
                    logger.error(f"ファイルの変換に失敗しました: {markdown_file}")
                    logger.error(f"Failed to convert file: {markdown_file}")
                    continue

                # Save YAML file
                yaml_file = os.path.splitext(markdown_file)[0] + "." + output_format
                yaml_path = os.path.join(output_dir, yaml_file)
                with open(yaml_path, "w", encoding="utf-8") as f:
                    f.write(yaml_content)

                logger.info(f"ファイルを変換しました: {markdown_file} -> {yaml_file}")
                logger.info(f"Converted file: {markdown_file} -> {yaml_file}")
                processed_count += 1
            except Exception as e:
                logger.error(f"ファイルの処理中にエラーが発生しました: {markdown_file} - {e}")
                logger.error(f"Error processing file: {markdown_file} - {e}")

        return processed_count
    except Exception as e:
        logger.error(f"ディレクトリの処理中にエラーが発生しました: {directory} - {e}")
        logger.error(f"Error processing directory: {directory} - {e}")
        return 0
