# Deepwiki to Markdown Converter

> **The Japanese version of this document is available at [README_ja.md](./README_ja.md).**

A Python tool to scrape content from DeepWiki sites and convert it to Markdown format. It provides various scraping
strategies and utility functions for processing the scraped data.

## Features

- Scrapes content from DeepWiki sites using multiple strategies:
  - Direct Markdown Fetching (default)
  - HTML Scraping with conversion to Markdown
- Extracts navigation items from content to traverse DeepWiki sites
- Converts HTML content to Markdown format using `markdownify`
- Saves the converted files in an organized directory structure
- Includes error handling with domain validation, reachability checks, and retry mechanisms
- Offers a utility to convert Markdown files to YAML format while preserving formatting
- Provides a utility to fix links within the scraped Markdown files
- Supports interactive chat with the scraped content

## Requirements

- Python 3.6 or higher
- Required Python packages (see `requirements.txt`):
  - `requests`
  - `beautifulsoup4`
  - `markdownify`
  - `pyyaml` (Required for the Markdown to YAML conversion feature)

## Installation

### Option 1: Install from PyPI

```bash
pip install deepwiki-to-md
```

### Option 2: Install from source

Clone this repository:

```bash
git clone https://github.com/yourusername/deepwiki_to_md.git
cd deepwiki_to_md
```

Install the package in development mode, including all dependencies from requirements.txt:

```bash
pip install -e . -r requirements.txt
```

## Usage

### Basic Usage (Command Line)

If installed from PyPI, you can use the command-line tool:

```bash
deepwiki-to-md "https://deepwiki.com/library_path"
```

Or with explicit parameters:

```bash
deepwiki-to-md -o "output_directory" -n "library_name" -d 2 "https://deepwiki.com/library_path"
```

If installed from source, you can run the script directly:

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/library_path"
```

Or with explicit parameters:

```bash
python -m deepwiki_to_md.run_scraper -o "output_directory" -n "library_name" -d 2 "https://deepwiki.com/library_path"
```

### Command-line Options

```
usage: deepwiki-to-md [-h] [-o OUTPUT_DIR] [-n LIBRARY_NAME] [-d MAX_DEPTH] [-v] [-t TIMEOUT] [-r RETRY_LIMIT] [--delay DELAY] url

Scrape content from DeepWiki sites and convert it to Markdown format.

positional arguments:
  url                   URL of the DeepWiki site to scrape.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save the output files. Default: output
  -n LIBRARY_NAME, --library-name LIBRARY_NAME
                        Name of the library to create. Default: derived from the URL
  -d MAX_DEPTH, --max-depth MAX_DEPTH
                        Maximum depth to crawl. Default: 1
  -v, --verbose         Print verbose output.
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout for HTTP requests in seconds. Default: 30
  -r RETRY_LIMIT, --retry-limit RETRY_LIMIT
                        Maximum number of retries for failed requests. Default: 3
  --delay DELAY         Delay between requests in seconds. Default: 0.5
```

### Repository Creation Tool

The package also includes a tool to create repository structures from DeepWiki content:

```bash
deepwiki-create "https://deepwiki.com/library_path"
```

With options to create YAML files and fix links:

```bash
deepwiki-create --create-yaml --fix-links "https://deepwiki.com/library_path"
```

### Interactive Chat

The package includes an interactive chat tool to explore the scraped content:

```bash
deepwiki-chat "https://deepwiki.com/library_path"
```

With option to save chat history:

```bash
deepwiki-chat --save-chat "https://deepwiki.com/library_path"
```

In the chat mode, you can use the following commands:

- `help`: Show a list of commands
- `list`: List available documents
- `read <number>`: Read a document
- `search <term>`: Search for a term in the documents
- `exit` or `quit`: End the chat

## Using as a Library

You can also use the package as a library in your own Python code:

```python
from deepwiki_to_md import DeepwikiScraper
from deepwiki_to_md.models.config import Config

# Create a configuration
config = Config(
  url="https://deepwiki.com/library_path",
  library_name="my_library",
  output_dir="output",
  max_depth=2,
  verbose=True
)

# Create a scraper
scraper = DeepwikiScraper(config)

# Scrape content
results = scraper.scrape()

# Process the results
for result in results:
  print(f"Scraped {result['url']} to {result['filepath']}")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.