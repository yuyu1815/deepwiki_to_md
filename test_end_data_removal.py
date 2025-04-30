import logging
import os
import re

from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_end_data_removal():
    """
    Test that custom data at the end of Markdown files is removed before saving
    """
    logger.info("Testing removal of custom data at the end of Markdown files")

    # Create output directory
    output_dir = "TestEndDataRemoval"
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

    # Check if custom data has been removed from the files
    if len(md_files) > 0:
        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for patterns that should have been removed
            end_data_patterns = [
                r'^-\s+Continued improvements',  # Example: "- Continued improvements to developer experience..."
                r'^c:null$',  # Example: "c:null"
                r'^\d+:\[\["',  # Example: "10:[[\"$\",\"title\",\"0\",{\"children\":..."
            ]

            found_patterns = []
            for pattern in end_data_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    found_patterns.append(pattern)

            if found_patterns:
                logger.error(f"Found {len(found_patterns)} patterns that should have been removed in {file_path}:")
                for pattern in found_patterns:
                    logger.error(f"  - {pattern}")
            else:
                logger.info(f"No custom data patterns found in {file_path}")
                logger.info("Custom data removal is working correctly")


if __name__ == "__main__":
    test_end_data_removal()
