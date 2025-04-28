import logging
import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeepwikiScraper:
    def __init__(self, output_dir="Documents"):
        """
        Initialize the DeepwikiScraper.

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
        """
        self.output_dir = output_dir
        self.session = requests.Session()
        # Set a user agent to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page_content(self, url, max_retries=3, base_delay=1):
        """
        Get the HTML content of a page with retry mechanism and exponential backoff.

        Args:
            url (str): The URL to fetch.
            max_retries (int): Maximum number of retry attempts.
            base_delay (int): Base delay in seconds between retries.

        Returns:
            str: The HTML content of the page.
        """
        retries = 0
        while retries <= max_retries:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Error fetching {url} after {max_retries} retries: {e}")
                    return None

                # Calculate exponential backoff delay with jitter
                delay = base_delay * (2 ** (retries - 1))
                delay += random.uniform(0, 0.5)  # Add jitter
                logger.warning(f"Retry {retries}/{max_retries} for {url} after {delay:.2f}s delay. Error: {e}")
                time.sleep(delay)

        return None

    def extract_navigation_items(self, html_content, current_url):
        """
        Extract navigation items from the specified ul element.

        Args:
            html_content (str): The HTML content of the page.
            current_url (str): The URL of the current page, used as base for relative URLs.

        Returns:
            list: A list of dictionaries containing the title and URL of each navigation item.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        nav_ul = soup.select_one('ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1')

        if not nav_ul:
            logger.warning("Navigation element not found")
            return []

        nav_items = []
        for li in nav_ul.find_all('li'):
            a_tag = li.find('a')
            if a_tag and a_tag.get('href'):
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href')
                full_url = urljoin(current_url, href)
                nav_items.append({
                    'title': title,
                    'url': full_url
                })

        return nav_items

    def extract_content(self, html_content):
        """
        Extract the main content from the page.

        Args:
            html_content (str): The HTML content of the page.

        Returns:
            str: The main content of the page.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        # Try multiple possible selectors for the main content
        # Order from most specific to most general
        selectors = [
            'main article',  # Original selector
            'main .content',  # Common pattern for main content
            'main',  # Any main element
            'article',  # Any article element
            '.content',  # Common class for content
            '.article-content',  # Common class for article content
            '#content',  # Common ID for content
            '.markdown-body',  # Common class for markdown content
            '.documentation-content',  # Common class for documentation
            'div.container div.row div.col'  # Bootstrap-like layout
        ]

        main_content = None
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text(strip=True)) > 0:
                logger.info(f"Found content using selector: {selector}")
                break

        if not main_content:
            # If no specific container found, try to get the body or largest text container
            body = soup.find('body')
            if body:
                # Find the div with the most text content
                divs = body.find_all('div', recursive=False)
                if divs:
                    main_content = max(divs, key=lambda x: len(x.get_text(strip=True)))
                else:
                    main_content = body

        if not main_content or len(main_content.get_text(strip=True)) == 0:
            logger.warning("Main content element not found")
            return ""

        return main_content

    def html_to_markdown(self, html_element):
        """
        Convert HTML content to Markdown.

        Args:
            html_element: The BeautifulSoup element containing the HTML content.

        Returns:
            str: The content converted to Markdown.
        """
        if not html_element:
            return ""

        # This is a simple implementation. For more complex conversions,
        # consider using a library like html2text or markdownify
        markdown = ""

        # Process headings
        for i in range(1, 7):
            for heading in html_element.find_all(f'h{i}'):
                text = heading.get_text(strip=True)
                markdown += f"{'#' * i} {text}\n\n"
                heading.decompose()

        # Process paragraphs
        for p in html_element.find_all('p'):
            text = p.get_text(strip=True)
            markdown += f"{text}\n\n"

        # Process lists
        for ul in html_element.find_all('ul'):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                markdown += f"- {text}\n"
            markdown += "\n"

        for ol in html_element.find_all('ol'):
            for i, li in enumerate(ol.find_all('li'), 1):
                text = li.get_text(strip=True)
                markdown += f"{i}. {text}\n"
            markdown += "\n"

        # Process code blocks
        for pre in html_element.find_all('pre'):
            code = pre.get_text()
            markdown += f"```\n{code}\n```\n\n"

        # Process inline code
        for code in html_element.find_all('code'):
            if code.parent.name != 'pre':  # Skip code inside pre (already handled)
                text = code.get_text()
                markdown += f"`{text}`"

        # Process links
        for a in html_element.find_all('a'):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            markdown += f"[{text}]({href})"

        # Process images
        for img in html_element.find_all('img'):
            alt = img.get('alt', '')
            src = img.get('src', '')
            markdown += f"![{alt}]({src})"

        return markdown

    def save_markdown(self, library_name, title, markdown_content, path=None):
        """
        Save the Markdown content to a file.

        Args:
            library_name (str): The name of the library.
            title (str): The title of the page.
            markdown_content (str): The Markdown content to save.
            path (str, optional): The path to use for the directory structure. If None, only library_name is used.
        """
        # Create directory structure if it doesn't exist
        # Use current working directory instead of a fixed path
        if path:
            # Use the path from the URL for the directory structure
            # Replace forward slashes with the appropriate path separator
            path_parts = path.split('/')
            dir_path = os.path.join(os.getcwd(), self.output_dir, *path_parts, "md")
        else:
            # Fallback to the old behavior
            dir_path = os.path.join(os.getcwd(), self.output_dir, library_name, "md")
        os.makedirs(dir_path, exist_ok=True)

        # Sanitize the title to create a valid filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        filename = re.sub(r'\s+', '_', filename)

        # Save the Markdown content to a file
        file_path = os.path.join(dir_path, f"{filename}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Saved {file_path}")

    def scrape_library(self, library_name, library_url):
        """
        Scrape a library and convert its content to Markdown.

        Args:
            library_name (str): The name of the library.
            library_url (str): The URL of the library.
        """
        logger.info(f"Scraping library: {library_name}")

        # Extract the path from the URL
        parsed_url = urlparse(library_url)
        full_path = parsed_url.path.strip('/')  # Remove leading/trailing slashes

        # Extract only the last part of the path (e.g., "cpython" from "python/cpython")
        path_parts = full_path.split('/')
        if len(path_parts) > 1:
            url_path = path_parts[-1]  # Get the last part of the path
        else:
            url_path = full_path

        # Get the library's main page
        html_content = self.get_page_content(library_url)
        if not html_content:
            logger.error(f"Failed to fetch content for {library_name}")
            return

        # Extract navigation items, using the library URL as the base URL
        nav_items = self.extract_navigation_items(html_content, library_url)

        if not nav_items:
            logger.warning(f"No navigation items found for {library_name}")
            # Try to extract and save the main page content
            main_content = self.extract_content(html_content)
            if main_content:
                markdown = self.html_to_markdown(main_content)
                self.save_markdown(library_name, library_name, markdown, url_path)
            return

        # Process each navigation item
        for item in nav_items:
            title = item['title']
            url = item['url']

            logger.info(f"Processing: {title}")

            # Add a small delay to avoid overwhelming the server
            time.sleep(1)

            # Get the page content
            page_html = self.get_page_content(url)
            if not page_html:
                logger.error(f"Failed to fetch content for {title}")
                continue

            # Extract the main content
            main_content = self.extract_content(page_html)
            if not main_content:
                logger.warning(f"No main content found for {title}")
                continue

            # Convert to Markdown
            markdown = self.html_to_markdown(main_content)

            # Save the Markdown content
            self.save_markdown(library_name, title, markdown, url_path)

    def run(self, libraries):
        """
        Run the scraper for multiple libraries.

        Args:
            libraries (list): A list of dictionaries containing the name and URL of each library.
        """
        for library in libraries:
            name = library['name']
            url = library['url']
            self.scrape_library(name, url)


if __name__ == "__main__":
    # Example usage
    # Define the libraries to scrape
    libraries = [
        {
            "name": "example_library",
            "url": "https://deepwiki.example.com/example_library"
        }
        # Add more libraries as needed
    ]

    scraper = DeepwikiScraper()
    scraper.run(libraries)
