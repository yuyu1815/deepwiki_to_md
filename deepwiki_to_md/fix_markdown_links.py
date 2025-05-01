import logging
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_markdown_links_in_file(file_path):
    """
    Fix links in a single markdown file.
    Preserves relative links while replacing external links with empty parentheses.

    Args:
        file_path (str): The path to the markdown file to process

    Returns:
        int: Number of links modified
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return 0

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expression to match markdown links with URLs
    # This pattern matches [text](url) where url is not empty
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    # Count original links
    original_links = len(link_pattern.findall(content))

    # Function to process each link match
    def process_link(match):
        text = match.group(1)
        url = match.group(2).strip()

        # Check if it's a relative link (doesn't start with http:// or https://)
        if not url.startswith(('http://', 'https://')):
            # Preserve relative links
            return f'[{text}]({url})'
        else:
            # Replace external links with empty parentheses
            return f'[{text}]()'

    # Replace links using the process_link function
    modified_content = link_pattern.sub(process_link, content)

    # Count modified links (links that were changed)
    modified_links = sum(1 for original, processed in
                         zip(link_pattern.findall(content),
                             link_pattern.findall(modified_content))
                         if original != processed)

    # Write modified content back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    logger.debug(f"Modified {modified_links} links in {file_path}")
    return modified_links

def fix_markdown_links(directory):
    """
    Find all markdown files in the specified directory and fix links.
    Preserves relative links while replacing external links with empty parentheses.

    Args:
        directory (str): The directory containing markdown files to process
    """
    # Check if directory exists
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        return

    # Find all markdown files in the directory
    md_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    logger.info(f"Found {len(md_files)} markdown files to process")

    # Process each file using the fix_markdown_links_in_file function
    total_modified = 0
    for file_path in md_files:
        logger.info(f"Processing {file_path}")
        modified = fix_markdown_links_in_file(file_path)
        total_modified += modified

    logger.info(f"Modified a total of {total_modified} links in {len(md_files)} files")

if __name__ == "__main__":
    # Path to the directory containing markdown files
    md_directory = os.path.join(os.getcwd(), "Documents", "cpython", "md")

    logger.info(f"Starting to fix markdown links in {md_directory}")
    fix_markdown_links(md_directory)
    logger.info("Finished fixing markdown links")
