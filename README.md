# Deepwiki to Markdown Converter

> **このドキュメントの日本語版は [README_ja.md](./README_ja.md) にあります。**

A Python tool to scrape content from deepwiki sites and convert it to Markdown format.

## Features

- Scrapes content from deepwiki sites
- Extracts navigation items from the specified UI elements
- Converts HTML content to Markdown format
- Saves the converted files in an organized directory structure
- Supports scraping multiple libraries

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

# Create a scraper instance
scraper = DeepwikiScraper(output_dir="MyDocuments")

# Scrape a library
scraper.scrape_library("python", "https://deepwiki.com/python")

# Or create another scraper with a different output directory
other_scraper = DeepwikiScraper(output_dir="OtherDocs")
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")
```

Run the example script:

```
python example.py
```

### Command-line Arguments

- `library_url`: URL of the library to scrape (can be provided as a positional argument)
- `--library`, `-l`: Library name and URL to scrape. Can be specified multiple times for different libraries.
- `--output-dir`, `-o`: Output directory for Markdown files (default: Documents)

### Examples

1. Simplified usage:
   ```
   python run_scraper.py "https://deepwiki.com/python"
   ```

2. Scrape a single library with explicit parameters:
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python"
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

1. The script connects to the specified deepwiki site
2. It extracts navigation items from the ul element with class="flex-1 flex-shrink-0 space-y-1 overflow-y-auto py-1"
3. For each navigation item, it fetches the page content
4. It extracts the main content from the page
5. It converts the HTML content to Markdown format
6. It saves the Markdown content to a file in the specified directory structure

## Customization

You can modify the `deepwiki_to_md.py` script to customize:

- The HTML selectors used to extract content
- The HTML to Markdown conversion logic
- The output file naming convention
- The delay between requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.
