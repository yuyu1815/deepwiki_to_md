# Deepwiki to Markdown Converter

> **The Japanese version of this document is available at [README_ja.md](./README_ja.md).**

A Python tool to scrape content from deepwiki sites and convert it to Markdown format. It provides various scraping
strategies and utility functions for processing the scraped data.

## Features

- Scrapes content from deepwiki sites using multiple strategies:
    - Direct Markdown Fetching (default)
    - Direct HTML Scraping with conversion
    - Simple static fallback
- Extracts navigation items from specified UI elements to traverse libraries
- Converts HTML content to Markdown format using `markdownify`
- Saves the converted files in an organized directory structure
- Supports scraping multiple libraries in a single run
- Includes error handling with domain validation, reachability checks, and retry mechanisms
- Offers a utility to convert Markdown files to YAML format while preserving formatting
- Provides a utility to fix links within the scraped Markdown files
- Supports scraping responses from chat interfaces using Selenium

## Requirements

- Python 3.6 or higher
- Required Python packages (see `requirements.txt`):
    - `requests`
    - `beautifulsoup4`
    - `argparse`
    - `markdownify`
    - `selenium` (Required for the chat scraping feature)
    - `webdriver-manager` (Required for the chat scraping feature)
    - `pyyaml` (Required for the Markdown to YAML conversion feature)

## Installation

### Option 1: Install from PyPI

```bash
pip install deepwiki-to-md
```

This will install the core dependencies listed in setup.py. Note that selenium, webdriver-manager, and pyyaml are listed
in requirements.txt but not in setup.py's install_requires. If you need the chat scraping or YAML conversion features,
you may need to install these manually or install from source including requirements.txt.

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
deepwiki-to-md --library "library_name" "https://deepwiki.example.com/library_path"
```

If installed from source, you can run the script directly:

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/library_path"
```

Or with explicit parameters:

```bash
python -m deepwiki_to_md.run_scraper --library "library_name" "https://deepwiki.example.com/library_path"
```

Note: The output directory will be created in the current working directory where the command is executed, not in the
package installation directory.

### Using the Python API

You can also use the DeepwikiScraper class directly in your Python code:

```python
from deepwiki_to_md import DeepwikiScraper
# Import specific scraper classes if needed for direct use
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper  # For HTML -> MD
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper  # For Direct MD

# Create a scraper instance (DirectMarkdownScraper is used by default)
scraper = DeepwikiScraper(output_dir="MyDocuments")

# Scrape a library using the default (DirectMarkdownScraper)
scraper.scrape_library("python", "https://deepwiki.com/python/cpython")

# Create another scraper with a different output directory
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# Scrape another library (still uses DirectMarkdownScraper by default)
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# --- Using DirectDeepwikiScraper explicitly (HTML to Markdown) ---
# Create a scraper instance explicitly using DirectDeepwikiScraper
# This scraper fetches HTML and converts it to Markdown
html_scraper = DeepwikiScraper(
    output_dir="HtmlScrapedDocuments",
    use_direct_scraper=True,  # Enable DirectDeepwikiScraper
    use_alternative_scraper=False,  # Disable alternative fallback for clarity
    use_direct_md_scraper=False  # Disable DirectMarkdownScraper
)
html_scraper.scrape_library("go", "https://deepwiki.com/go")

# --- Using DirectMarkdownScraper explicitly (Direct Markdown Fetching) ---
# Create a scraper instance explicitly using DirectMarkdownScraper
# This is already the default, but can be specified for clarity or if other defaults change
md_scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
    use_direct_scraper=False,
    use_alternative_scraper=False,
    use_direct_md_scraper=True  # Enable DirectMarkdownScraper (this is the default)
)
md_scraper.scrape_library("rust", "https://deepwiki.com/rust")

# --- Using the individual direct scrapers directly ---
# These classes can be used independently for scraping specific pages or lists of pages

# Create a DirectDeepwikiScraper instance (HTML to Markdown)
direct_html_scraper = DirectDeepwikiScraper(output_dir="DirectHtmlScraped")

# Scrape a specific page directly (HTML to Markdown)
direct_html_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",  # Library name/path part for output folder
    save_html=True  # Optionally save the original HTML
)

# Create a DirectMarkdownScraper instance (Direct Markdown Fetching)
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownFetched")

# Scrape a specific page directly as Markdown
direct_md_scraper.scrape_page(
   "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode"  # Library name/path part for output folder
)
```

### Command-line Arguments

For `deepwiki-to-md` or `python -m deepwiki_to_md.run_scraper`:

- `library_url`: URL of the library to scrape (can be provided as a positional argument).
- `--library`, `-l`: Library name and URL to scrape. Can be specified multiple times for different libraries. Format:
  `--library NAME URL`.
- `--output-dir`, `-o`: Output directory for Markdown files (default: `Documents`).
- `--use-direct-scraper`: Use DirectDeepwikiScraper (HTML to Markdown conversion). Prioritized over
  `--use-direct-md-scraper` if both are specified.
- `--no-direct-scraper`: Disable DirectDeepwikiScraper.
- `--use-alternative-scraper`: Use the scrape_deepwiki function from direct_scraper.py as a fallback if the primary
  method fails (default: True).
- `--no-alternative-scraper`: Disable the alternative scraper fallback.
- `--use-direct-md-scraper`: Use DirectMarkdownScraper (fetches Markdown directly). This is the default behavior if no
  scraper type is explicitly specified.
- `--no-direct-md-scraper`: Disable DirectMarkdownScraper.

#### Scraper Priority:

1. If `--use-direct-scraper` is specified, DirectDeepwikiScraper (HTML to Markdown) is used.
2. If `--use-direct-md-scraper` is specified (and `--use-direct-scraper` is not), DirectMarkdownScraper (Direct
   Markdown) is used.
3. If neither is specified, DirectMarkdownScraper (Direct Markdown) is used by default.
4. The `--use-alternative-scraper` flag controls a fallback mechanism within the chosen primary scraper.

### Examples (Command Line)

Simplified usage (uses DirectMarkdownScraper by default):

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython"
# Or if installed via pip: deepwiki-to-md "https://deepwiki.com/python/cpython"
```

Scrape a single library with explicit parameters:

```bash
python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.com/python/cpython"
```

Scrape multiple libraries:

```bash
python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.com/python/cpython" --library "javascript" "https://deepwiki.example.com/javascript"
```

Specify a custom output directory:

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --output-dir "MyDocuments"
```

Explicitly use DirectMarkdownScraper (Direct Markdown):

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --use-direct-md-scraper
```

Explicitly use DirectDeepwikiScraper (HTML to Markdown):

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --use-direct-scraper
```

Disable the alternative scraper fallback:

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --no-alternative-scraper
```

### Usage with run_direct_scraper.py

You can also use the run_direct_scraper.py script, which is a simplified entry point specifically for the
DirectDeepwikiScraper (HTML to Markdown):

```bash
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython"
# Or with explicit parameters:
python -m deepwiki_to_md.run_direct_scraper --library "python" "https://deepwiki.com/python/cpython"
# To save HTML as well:
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython" --save-html
```

Arguments for run_direct_scraper.py:

- `library_url`: URL of the library (positional).
- `--library`, `-l`: Library name and URL (can be multiple).
- `--output-dir`, `-o`: Output directory (default: DynamicDocuments).
- `--save-html`: Save original HTML files alongside Markdown.

## Output Structure

The converted Markdown files will be saved in the following directory structure:

```
<output_dir>/
├── <library_name1>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
│   └── html/ # Only if --save-html is used with DirectDeepwikiScraper
│       ├── <page_name1>.html
│       ├── <page_name2>.html
│       └── ...
├── <library_name2>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
└── ...
```

- `<output_dir>` is the directory specified by `--output-dir` (default: `Documents` for run_scraper.py,
  `DynamicDocuments` for run_direct_scraper.py).
- `<library_name>` is the name provided for the library (or inferred from the URL path).
- Each page from the Deepwiki site is saved as a separate .md file within the md subdirectory.
- Original HTML is saved in the html subdirectory if the `--save-html` option is used with DirectDeepwikiScraper.

## How It Works

The tool offers different scraping strategies to maximize compatibility and output quality:

### 1. Direct Markdown Scraping (DirectMarkdownScraper - Default)

**Priority:** Highest (used by default if no other scraper is explicitly chosen).

**Method:** Attempts to fetch the raw Markdown content directly from the Deepwiki site's underlying data source or API.
This is done by sending requests with specialized headers that mimic internal application requests.

**Process:**

- Sends requests designed to retrieve Markdown data (using specific Accept headers or query parameters)
- Parses the response to extract the Markdown content
- Performs minimal cleaning on the extracted Markdown
- Splits the content into multiple files based on level 2 headings (##)
- Saves the cleaned and split Markdown content directly to .md files

**Advantage:** Produces the highest fidelity Markdown, preserving the original formatting and structure as intended by
the author.

### 2. Direct HTML Scraping (DirectDeepwikiScraper)

**Priority:** Medium (used if `--use-direct-scraper` is specified).

**Method:** Connects to the Deepwiki site using headers that mimic a standard browser request to fetch the fully
rendered HTML page.

**Process:**

- Fetches the full HTML of the page using the `scrape_deepwiki` function
- Uses BeautifulSoup to parse the HTML
- Identifies the main content area using a list of potential CSS selectors
- Uses the markdownify library to convert the selected HTML content to Markdown
- Saves the converted Markdown

**Advantage:** More robust than basic static scraping if direct Markdown fetching fails or is unavailable.

### 3. Alternative Scraper Fallback

**Priority:** Lowest (used as a fallback if `--use-alternative-scraper` is enabled).

**Method:** A simpler static requests mechanism with specific headers designed to fetch the page HTML reliably.

## Markdown to YAML Conversion Utility

The tool provides a utility to convert Markdown files to YAML format while preserving formatting. This is particularly
useful for processing the scraped content for LLMs.

### Using the Conversion Tool (Command Line)

```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md"
# Or if entry point is configured:
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md"
```

To specify a custom output directory:

```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
```

### Using the Python API (Markdown to YAML)

```python
from deepwiki_to_md.md_to_yaml import convert_md_file_to_yaml, markdown_to_yaml

# Convert a Markdown file to YAML
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md")

# Convert a Markdown file to YAML with a custom output directory
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md", "path/to/output/directory")

# Or convert a Markdown string directly to a YAML string
markdown_string = "# My Document\n\nThis is the content."
yaml_string = markdown_to_yaml(markdown_string)
print(yaml_string)
```

### YAML Format

The converted YAML file includes a structured representation of the document while embedding the original Markdown
content:

```yaml
timestamp: 'YYYY-MM-DD HH:MM:SS'  # Timestamp of the conversion
title: Extracted Document Title    # Title extracted from the first H1/H2 header
content: |
  # Original Title
  ## Section 1

  Content of section 1.

  * List item 1
  * List item 2

  print("code")

  [Link Text](url)

  ## Section 2

  Content of section 2.
  ...                              # Full original Markdown content is preserved
links:
  - text: Link Text
    url: url                       # List of links extracted from the Markdown
images: [ ]                         # List of images extracted (currently empty)
metadata:
  headers: # List of all header texts
    - Original Title
    - Section 1
    - Section 2
    ...
  paragraphs_count: 5              # Count of paragraphs
  lists_count: 1                   # Count of lists
  tables_count: 0                  # Count of tables
```

## Markdown Link Fixing Utility

The tool automatically runs a link-fixing utility on the generated .md files. This utility finds Markdown links in the
format `[Text](URL)` and replaces them with `[Text]()`.

### Using the Link Fixing Tool (Command Line)

```bash
python -m deepwiki_to_md.fix_markdown_links "path/to/your/markdown/directory"
```

### Using the Python API (Link Fixing)

```python
from deepwiki_to_md.fix_markdown_links import fix_markdown_links

# Fix links in all markdown files within a directory
fix_markdown_links("path/to/your/markdown/directory")
```

## Chat Scraping Feature (Requires Selenium)

The tool includes a feature to interact with chat interfaces using Selenium and save the responses.

### Using the Chat Scraper (Command Line)

```bash
python -m deepwiki_to_md.chat --url "https://deepwiki.com/some_chat_page" --message "Your message here" --wait 10 --debug --format "html,md,yaml" --output "MyChatResponses" --deep
```

Arguments for chat.py:

- `--url`: URL of the chat interface.
- `--message`: Message to send.
- `--selector`: CSS selector for the chat input (default: textarea).
- `--button`: CSS selector for the submit button (default: button).
- `--wait`: Time to wait for response in seconds (default: 30).
- `--debug`: Enable debug mode.
- `--output`: Output directory (default: ChatResponses).
- `--deep`: Enable "Deep Research" mode (specific to some interfaces).
- `--headless`: Run browser in headless mode.
- `--format`: Output format(s): html, md, yaml, or comma-separated list (default: html).

Note: The chat scraper uses Selenium, which requires a compatible browser installed.

## License

This project is licensed under the MIT License - see the LICENSE file for details.