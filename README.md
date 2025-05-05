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
- Offers direct scraping methods for improved reliability and direct Markdown fetching
- Converts Markdown files to YAML format while preserving formatting

## Requirements

- Python 3.6 or higher
- Required Python packages:
    - requests
    - beautifulsoup4
    - argparse
  - markdownify

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

You can also use the `DeepwikiScraper` class directly in your Python code. See `example.py` for a complete example:

```python
from deepwiki_to_md import DeepwikiScraper
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper

# Create a scraper instance (default uses DirectMarkdownScraper)
scraper = DeepwikiScraper(output_dir="MyDocuments")

# Scrape a library using the default (DirectMarkdownScraper)
scraper.scrape_library("python", "https://deepwiki.com/python")

# Create another scraper with a different output directory
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# Scrape another library
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# --- Using DirectDeepwikiScraper (HTML to Markdown) ---
# Create a scraper instance explicitly using DirectDeepwikiScraper
html_scraper = DeepwikiScraper(
    output_dir="HtmlScrapedDocuments",
    use_direct_scraper=True,  # Enable DirectDeepwikiScraper
    use_alternative_scraper=False,
    use_direct_md_scraper=False
)
html_scraper.scrape_library("go", "https://deepwiki.com/go")

# --- Using DirectMarkdownScraper (Direct Markdown Fetching) ---
# Create a scraper instance explicitly using DirectMarkdownScraper
md_scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
    use_direct_scraper=False,
    use_alternative_scraper=False,
    use_direct_md_scraper=True  # Enable DirectMarkdownScraper (this is the default)
)
md_scraper.scrape_library("rust", "https://deepwiki.com/rust")

# --- Using the individual direct scrapers --- 
# Create a DirectDeepwikiScraper instance (HTML to Markdown)
direct_html_scraper = DirectDeepwikiScraper(output_dir="DirectHtmlScraped")

# Scrape a specific page directly (HTML to Markdown)
direct_html_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",
    save_html=True  # Optionally save the original HTML
)

# Create a DirectMarkdownScraper instance (Direct Markdown Fetching)
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownFetched")

# Scrape a specific page directly as Markdown
direct_md_scraper.scrape_page(
   "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
   "python_bytecode"
)

# You can also use the run method for multiple direct scrapes (for DirectDeepwikiScraper)
# direct_html_results = direct_html_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])

# You can also use the run method for multiple direct scrapes (for DirectMarkdownScraper)
# direct_md_results = direct_md_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])
```

Run the example script:

```
python example.py
```

### Command-line Arguments

- `library_url`: URL of the library to scrape (can be provided as a positional argument).
- `--library`, `-l`: Library name and URL to scrape. Can be specified multiple times for different libraries. Format:
  `--library NAME URL` (NAME and URL are placeholders).
- `--output-dir`, `-o`: Output directory for Markdown files (default: `Documents`).
- `--use-direct-scraper`: Use `DirectDeepwikiScraper` (HTML to Markdown conversion). Overrides `--use-direct-md-scraper`
  if both are specified.
- `--no-direct-scraper`: Disable `DirectDeepwikiScraper`.
- `--use-alternative-scraper`: Use the `scrape_deepwiki` function from `direct_scraper.py` as a fallback if the primary
  method fails (default: True).
- `--no-alternative-scraper`: Disable the alternative scraper fallback.
- `--use-direct-md-scraper`: Use `DirectMarkdownScraper` (fetches Markdown directly). This is the **default behavior**
  if no scraper type is explicitly specified.
- `--no-direct-md-scraper`: Disable `DirectMarkdownScraper`.

**Scraper Priority:**

1. If `--use-direct-scraper` is specified, `DirectDeepwikiScraper` (HTML to Markdown) is used.
2. If `--use-direct-md-scraper` is specified (and `--use-direct-scraper` is not), `DirectMarkdownScraper` (Direct
   Markdown) is used.
3. If neither `--use-direct-scraper` nor `--use-direct-md-scraper` is specified, `DirectMarkdownScraper` (Direct
   Markdown) is used by **default**.
4. The `--use-alternative-scraper` flag controls a fallback mechanism within the chosen primary scraper.

### Examples

1. **Simplified usage (uses DirectMarkdownScraper by default):**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python"
   ```

2. **Scrape a single library with explicit parameters (uses DirectMarkdownScraper by default):**
   ```
   python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.example.com/python"
   ```

3. **Scrape multiple libraries (uses DirectMarkdownScraper by default):**
   ```
   python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.example.com/python" --library "javascript" "https://deepwiki.example.com/javascript"
   ```

4. **Specify a custom output directory:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --output-dir "MyDocuments"
   ```

5. **Explicitly use DirectMarkdownScraper (Direct Markdown):**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-md-scraper
   ```

6. **Explicitly use DirectDeepwikiScraper (HTML to Markdown):**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-scraper
   ```

7. **Disable the alternative scraper fallback:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --no-alternative-scraper
   ```

8. **Use DirectDeepwikiScraper and disable the alternative fallback:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-scraper --no-alternative-scraper
   ```

## Output Structure

The converted Markdown files will be saved in the following directory structure:

```
<output_dir>/
├── <library_name1>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
├── <library_name2>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
└── ...
```

- `<output_dir>` is the directory specified by `--output-dir` (default: `Documents`).
- `<library_name>` is the name provided for the library.
- Each page from the Deepwiki site is saved as a separate `.md` file within the `md` subdirectory.

## How It Works

The tool offers different scraping strategies:

### 1. Direct Markdown Scraping (`DirectMarkdownScraper` - Default)

- **Priority:** Highest (used by default).
- **Method:** Connects to the Deepwiki site using specialized headers optimized for fetching raw Markdown content
  directly from the server's internal API or data structures.
- **Process:**
    1. Sends requests designed to retrieve Markdown data.
    2. Parses the response (often JSON or a specific text format) to extract the Markdown content.
    3. Cleans up the extracted Markdown (removes potential artifacts like metadata or script tags).
    4. Saves the cleaned Markdown content directly to files.
- **Advantage:** Highest fidelity Markdown, preserves original formatting, avoids HTML conversion errors.

### 2. Direct HTML Scraping (`DirectDeepwikiScraper`)

- **Priority:** Medium (used if `--use-direct-scraper` is specified).
- **Method:** Connects to the Deepwiki site using headers that mimic a browser request to fetch the rendered HTML page.
- **Process:**
    1. Fetches the full HTML of the page.
    2. Uses BeautifulSoup to parse the HTML.
    3. Identifies the main content area using various CSS selectors.
    4. Uses `markdownify` library to convert the selected HTML content block to Markdown.
    5. Saves the converted Markdown.
- **Advantage:** More robust than basic static scraping if direct Markdown fetching fails or is unavailable.
- **Disadvantage:** Relies on HTML structure and conversion quality.

### 3. Alternative Scraper Fallback (`scrape_deepwiki` from `direct_scraper.py`)

- **Priority:** Lowest (used as a fallback within the primary scraper if `--use-alternative-scraper` is enabled, which
  is the default).
- **Method:** A simpler static request mechanism, potentially used if the main methods encounter issues (e.g., complex
  navigation or unexpected page structure).
- **Process:** Fetches HTML and attempts basic content extraction.

### Navigation and Hierarchy

- Both `DirectMarkdownScraper` and `DirectDeepwikiScraper` attempt to identify navigation links (like a table of
  contents or sidebar) within the fetched content (either Markdown or HTML).
- They recursively follow these links to scrape the entire library structure.

### Error Handling

The tool includes robust error handling:

- Validates domains before scraping.
- Checks domain reachability.
- Provides clear error messages.
- Implements retry mechanisms with exponential backoff for transient network errors.
- Falls back to the alternative scraper if configured and the primary method fails.

## Customization

You can modify the Python scripts (`deepwiki_to_md/deepwiki_to_md.py`, `deepwiki_to_md/direct_scraper.py`,
`deepwiki_to_md/direct_md_scraper.py`) to customize:

- HTML selectors used for content extraction (in `DirectDeepwikiScraper`).
- Markdown parsing/cleaning logic (in `DirectMarkdownScraper`).
- HTML to Markdown conversion options (`markdownify` settings).
- Output file naming conventions.
- Request headers and delays.

## Markdown to YAML Conversion

The tool also provides functionality to convert Markdown files to YAML format while preserving the formatting. This is
particularly useful for LLMs (Large Language Models) as YAML is an optimal format for them to read.

### Using the Conversion Tool

You can convert Markdown files to YAML using the command-line interface:

```
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md"
```

To specify a custom output directory:

```
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
```

### Using the Python API

You can also use the conversion function directly in your Python code:

```python
from deepwiki_to_md.md_to_yaml import convert_md_file_to_yaml

# Convert a Markdown file to YAML
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md")

# Convert a Markdown file to YAML with a custom output directory
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md", "path/to/output/directory")
```

### YAML Format

The converted YAML file includes:

- `timestamp`: The time of conversion
- `title`: Extracted from the first header in the Markdown file
- `content`: The full Markdown content with formatting preserved
- `links`: A list of links extracted from the Markdown
- `metadata`: Additional information including:
    - `headers`: A list of all headers in the Markdown
    - `paragraphs_count`: The number of paragraphs
    - `lists_count`: The number of lists
    - `tables_count`: The number of tables

This structured format makes it easier for LLMs to process and understand the content while preserving the original
Markdown formatting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
