"""
Example script demonstrating how to use the DeepwikiScraper class directly.
"""
from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper


def main():
    # Example 1: Scraping from deepwiki.com
    libraries = [
        {
            "name": "python",
            "url": "https://deepwiki.com/python/cpython"
        }
    ]

    # Create a DeepwikiScraper instance
    scraper = DeepwikiScraper(output_dir="Documents")

    # Run the scraper for the library
    for library in libraries:
        print(f"Scraping {library['name']}...")
        scraper.scrape_library(library['name'], library['url'])

    # Example 2: Scraping from a different domain
    other_libraries = [
        {
            "name": "javascript",
            "url": "https://deepwiki.example.com/javascript"
        }
    ]

    # Create another DeepwikiScraper instance with a different output directory
    other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

    # Run the scraper for each library
    for library in other_libraries:
        print(f"Scraping {library['name']}...")
        other_scraper.scrape_library(library['name'], library['url'])

    print("Scraping completed!")


if __name__ == "__main__":
    main()
