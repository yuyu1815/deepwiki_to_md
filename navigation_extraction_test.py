import logging
import os

from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_direct_md_scraper_navigation():
    """
    Test the navigation extraction functionality in DirectMarkdownScraper
    """
    logger.info("Testing DirectMarkdownScraper navigation extraction")

    # Create output directory
    output_dir = "NavigationExtractionTest"
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

    # Save the navigation links to a file for inspection
    nav_links_file = os.path.join(output_dir, "navigation_links.md")
    with open(nav_links_file, "w", encoding="utf-8") as f:
        f.write(f"# Navigation Links for {url}\n\n")

        # Get the navigation items
        import requests
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        })

        if response.status_code == 200:
            nav_items = scraper.extract_navigation_items(response.text, url)

            if nav_items:
                f.write(f"Found {len(nav_items)} navigation items:\n\n")
                for i, item in enumerate(nav_items, 1):
                    f.write(f"{i}. [{item['title']}]({item['url']})\n")
            else:
                f.write("No navigation items found.\n")
        else:
            f.write(f"Failed to fetch the page: {response.status_code}\n")

    logger.info(f"Navigation links saved to {nav_links_file}")


def test_direct_deepwiki_scraper_navigation():
    """
    Test the navigation extraction functionality in DirectDeepwikiScraper
    """
    logger.info("Testing DirectDeepwikiScraper navigation extraction")

    # Create output directory
    output_dir = "NavigationExtractionTest"
    os.makedirs(output_dir, exist_ok=True)

    # Create a DirectDeepwikiScraper instance
    scraper = DirectDeepwikiScraper(output_dir=output_dir)

    # Test URL
    url = "https://deepwiki.com/python/cpython"

    # Scrape the library
    md_files = scraper.scrape_library(url, "python", save_html=True)

    # Log the results
    logger.info(f"Scraped {len(md_files)} files:")
    for file_path in md_files:
        logger.info(f"  - {file_path}")


def test_deepwiki_scraper_with_direct_md():
    """
    Test the DeepwikiScraper with DirectMarkdownScraper enabled
    """
    logger.info("Testing DeepwikiScraper with DirectMarkdownScraper")

    # Create a DeepwikiScraper instance with DirectMarkdownScraper enabled
    scraper = DeepwikiScraper(
        output_dir="NavigationExtractionTest",
        use_direct_scraper=False,
        use_alternative_scraper=False,
        use_direct_md_scraper=True
    )

    # Test URL
    libraries = [
        {"name": "python", "url": "https://deepwiki.com/python/cpython"}
    ]

    # Run the scraper
    scraper.run(libraries)


if __name__ == "__main__":
    # Choose which test to run
    test_direct_md_scraper_navigation()
    # test_direct_deepwiki_scraper_navigation()
    # test_deepwiki_scraper_with_direct_md()
