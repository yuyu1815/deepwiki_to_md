import logging
import os

from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_direct_md_scraper():
    """
    Test the DirectMarkdownScraper with fix_markdown_links functionality
    """
    logger.info("Testing DirectMarkdownScraper with fix_markdown_links")

    # Create output directory
    output_dir = "TestDirectMarkdownScraper"
    os.makedirs(output_dir, exist_ok=True)

    # Create a DirectMarkdownScraper instance
    scraper = DirectMarkdownScraper(output_dir=output_dir)

    # Test URL
    url = "https://deepwiki.com/python/cpython"

    # Scrape the library
    md_files = scraper.scrape_library(url, "python")

    # Log the results
    logger.info(f"Scraped {len(md_files)} files:")
    for file_path in md_files:
        logger.info(f"  - {file_path}")

    # Check if the Markdown links have been fixed
    if len(md_files) > 0:
        # Open the first file and check if it contains any links with URLs
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if there are any links with URLs
        import re
        link_pattern = re.compile(r'\[([^\]]+)\]\((?![\s\)])[^\)]+\)')
        links_with_urls = link_pattern.findall(content)

        if links_with_urls:
            logger.error(f"Found {len(links_with_urls)} links with URLs in {md_files[0]}")
            logger.error("fix_markdown_links may not be working correctly")
        else:
            logger.info(f"No links with URLs found in {md_files[0]}")
            logger.info("fix_markdown_links is working correctly")


if __name__ == "__main__":
    test_direct_md_scraper()
