import os

from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper

# Create a scraper
scraper = DeepwikiScraper(
    output_dir="TestDirectoryStructure",
    use_direct_scraper=False,
    use_alternative_scraper=False
)

# Test URL
libraries = [
    {"name": "python", "url": "https://deepwiki.com/python/cpython"}
]

# Run the scraper
scraper.run(libraries)

# Check if the files are saved in the correct directory structure
expected_dir = os.path.join(os.getcwd(), "TestDirectoryStructure", "cpython", "md")
if os.path.exists(expected_dir):
    print(f"Success: Files are saved in the correct directory structure: {expected_dir}")
    # List the files in the directory
    files = os.listdir(expected_dir)
    print(f"Found {len(files)} files in the directory")
    for file in files[:5]:  # Show only the first 5 files
        print(f"  - {file}")
else:
    print(f"Error: Directory not found: {expected_dir}")
    # Check if the old directory structure exists
    old_dir = os.path.join(os.getcwd(), "TestDirectoryStructure", "python", "md")
    if os.path.exists(old_dir):
        print(f"Error: Files are still being saved in the old directory structure: {old_dir}")
    else:
        print("Error: Neither the new nor the old directory structure exists")
