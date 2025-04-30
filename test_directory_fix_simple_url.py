import os
import sys

from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper


def test_simple_url_directory_structure():
    """
    Test that the directory structure is correctly created for URLs with fewer path components.
    """
    # Create a test output directory
    output_dir = "TestDirectoryStructureSimple"

    # Create a scraper with the test output directory
    # When both use_direct_scraper and use_alternative_scraper are False, use_direct_md_scraper is set to True
    scraper = DeepwikiScraper(output_dir=output_dir, use_direct_scraper=False, use_alternative_scraper=False)

    # Define a test library with a URL that has fewer path components
    test_library = {
        "name": "cpython",
        "url": "https://deepwiki.com/python/cpython"
    }

    # Run the scraper for the test library
    scraper.scrape_library(test_library["name"], test_library["url"])

    # Check if the directory structure is correct
    expected_dir = os.path.join(os.getcwd(), output_dir, "cpython", "md")
    if os.path.exists(expected_dir):
        print(f"SUCCESS: Directory '{expected_dir}' exists.")
        # List files in the directory to verify
        files = os.listdir(expected_dir)
        print(f"Files in directory: {files}")
        return True
    else:
        print(f"ERROR: Directory '{expected_dir}' does not exist.")
        return False


if __name__ == "__main__":
    print("Testing directory structure for URLs with fewer path components...")
    success = test_simple_url_directory_structure()
    if success:
        print("Test passed: Directory structure is correct for simple URLs.")
        sys.exit(0)
    else:
        print("Test failed: Directory structure is incorrect for simple URLs.")
        sys.exit(1)
