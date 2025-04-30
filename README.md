# Deepwiki to Markdown Converter

> **このドキュメントの日本語版は [README_ja.md](./README_ja.md) にあります。**

A Python tool to scrape content from deepwiki sites and convert it to Markdown format.

## Features

- Scrapes content from deepwiki sites
- Extracts navigation items from the specified UI elements
- Converts HTML content to Markdown format
- Saves the converted files in an organized directory structure
- Supports scraping multiple libraries
- Supports static page scraping with requests

## Requirements

- Python 3.6 or higher
- Required Python packages:
    - requests
    - beautifulsoup4
    - argparse

## Installation

### Option 1: Install from PyPI

```
pip install deepwiki-to-md
```

### Option 2: Install from source

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/deepwiki_to_md.git
   cd deepwiki_to_md
   ```

2. Install the package in development mode:
   ```
   pip install -e .
   ```

## Usage

### Basic Usage

If installed from PyPI, you can use the command-line tool:

```
deepwiki-to-md "https://deepwiki.com/library_path"
```

Or with explicit parameters:

```
deepwiki-to-md --library "library_name" "https://deepwiki.example.com/library_path"
```

If installed from source, you can run the script directly:

```
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/library_path"
```

Or with explicit parameters:

```
python -m deepwiki_to_md.run_scraper --library "library_name" "https://deepwiki.example.com/library_path"
```

**Note**: The output directory will be created in the current working directory where the command is executed, not in
the package installation directory.

### Using the Python API

You can also use the DeepwikiScraper class directly in your Python code. See `example.py` for a complete example:

```python
from deepwiki_to_md import DeepwikiScraper
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper

# Create a scraper instance
scraper = DeepwikiScraper(output_dir="MyDocuments")

# Scrape a library
scraper.scrape_library("python", "https://deepwiki.com/python")

# Create another scraper with a different output directory
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# Scrape another library
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# Create a direct scraper instance
direct_scraper = DirectDeepwikiScraper(output_dir="DirectScraped")

# Scrape a specific page directly
direct_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",
    save_html=True
)

# You can also use the run method for multiple direct scrapes
# direct_results = direct_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])
```

Run the example script:

```
python example.py
```

### Command-line Arguments

- `library_url`: URL of the library to scrape (can be provided as a positional argument)
- `--library`, `-l`: Library name and URL to scrape. Can be specified multiple times for different libraries.
- `--output-dir`, `-o`: Output directory for Markdown files (default: Documents)
- `--use-direct-scraper`: Use DirectDeepwikiScraper for scraping (default: True)
- `--no-direct-scraper`: Disable DirectDeepwikiScraper
- `--use-alternative-scraper`: Use alternative scraper for pages without navigation items (default: True)
- `--no-alternative-scraper`: Disable alternative scraper for pages without navigation items

### Examples

1. Simplified usage:
   ```
   python run_scraper.py "https://deepwiki.com/python"
   ```

2. Scrape a single library with explicit parameters:
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python"
   ```

3. Use the direct scraper to fetch Markdown directly:
   ```
   python run_direct_scraper.py "https://deepwiki.com/python"
   ```

4. Use the direct scraper with HTML preservation:
   ```
   python run_direct_scraper.py --library "python" "https://deepwiki.example.com/python" --save-html
   ```

3. Scrape multiple libraries:
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python" --library "javascript" "https://deepwiki.example.com/javascript"
   ```

4. Specify a custom output directory:
   ```
   python run_scraper.py "https://deepwiki.com/python" --output-dir "MyDocuments"
   ```

5. Specify a custom output directory with explicit parameters:
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python" --output-dir "MyDocuments"
   ```

6. Use DirectDeepwikiScraper for scraping:
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-direct-scraper
   ```

7. Disable DirectDeepwikiScraper:
   ```
   python run_scraper.py "https://deepwiki.com/python" --no-direct-scraper
   ```

8. Disable alternative scraper for pages without navigation items:
   ```
   python run_scraper.py "https://deepwiki.com/python" --no-alternative-scraper
   ```

9. Explicitly enable alternative scraper (enabled by default):
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-alternative-scraper
   ```

## Output Structure

The converted Markdown files will be saved in the following directory structure:

```
Documents/
├── library_name1/
│   └── md/
│       ├── page1.md
│       ├── page2.md
│       └── ...
├── library_name2/
│   └── md/
│       ├── page1.md
│       ├── page2.md
│       └── ...
└── ...
```

## How It Works

### Static Page Scraping (Default)

1. The script connects to the specified deepwiki site using the requests library
2. It extracts navigation items from the ul element with class="flex-1 flex-shrink-0 space-y-1 overflow-y-auto py-1"
3. For each navigation item, it fetches the page content
4. It extracts the main content from the page
5. It converts the HTML content to Markdown format
6. It saves the Markdown content to a file in the specified directory structure

### Direct Scraping (New Feature)

The new direct scraping feature allows you to fetch Markdown content directly from DeepWiki:

1. Connects to the DeepWiki site using specialized headers
2. Extracts Markdown content from the response
3. Preserves HTML structure needed for left-side URLs (optional)
4. Saves the content as Markdown files in the specified directory structure

This method skips the HTML-to-Markdown conversion process, resulting in higher quality Markdown content.

### Error Handling

The tool includes robust error handling to deal with common issues:

1. Validates domains before attempting to scrape (rejects placeholder domains like example.com)
2. Checks if domains are reachable before attempting to connect
3. Provides clear error messages when domains are unreachable
4. Gracefully falls back to alternative scraping methods when primary methods fail
5. Implements retry mechanisms with exponential backoff for transient errors


## Customization

You can modify the `deepwiki_to_md.py` script to customize:

- The HTML selectors used to extract content
- The HTML to Markdown conversion logic
- The output file naming convention
- The delay between requests


## License

This project is licensed under the MIT License - see the LICENSE file for details.
