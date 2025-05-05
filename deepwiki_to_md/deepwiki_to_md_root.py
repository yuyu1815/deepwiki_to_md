import logging
import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .localization import get_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeepwikiScraper:
    def __init__(self, base_url="https://deepwiki.com", output_dir="Documents"):
        """
        Initialize the DeepwikiScraper.

        Args:
            base_url (str): The base URL of the deepwiki site. Default is "https://deepwiki.com".
            output_dir (str): The base directory to save the converted Markdown files.
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        # Set a user agent to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page_content(self, url):
        """
        Get the HTML content of a page.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The HTML content of the page.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_navigation_items(self, html_content):
        """
        Extract navigation items from the specified ul element.

        Args:
            html_content (str): The HTML content of the page.

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
                full_url = urljoin(self.base_url, href)
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
        # This selector might need to be adjusted based on the actual structure of deepwiki
        main_content = soup.select_one('main article')

        if not main_content:
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

    def save_markdown(self, library_name, title, markdown_content):
        """
        Save the Markdown content to a file.

        Args:
            library_name (str): The name of the library.
            title (str): The title of the page.
            markdown_content (str): The Markdown content to save.
        """
        # Create directory structure if it doesn't exist
        dir_path = os.path.join(self.output_dir, library_name, "md")
        os.makedirs(dir_path, exist_ok=True)

        # Sanitize the title to create a valid filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        filename = re.sub(r'\s+', '_', filename)

        # Remove the first 28 lines from the markdown content
        if markdown_content:
            lines = markdown_content.split('\n')
            if len(lines) > 28:
                markdown_content = '\n'.join(lines[28:])
                logger.info(get_message('removed_first_lines', count=28, filename=filename))

        # Save the Markdown content to a file
        file_path = os.path.join(dir_path, f"{filename}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(get_message('saved_file', file_path=file_path))

    def scrape_library(self, library_name, library_url):
        """
        Scrape a library and convert its content to Markdown.

        Args:
            library_name (str): The name of the library.
            library_url (str): The URL of the library.
        """
        logger.info(get_message('scraping_library', library_name=library_name))

        # Get the library's main page
        html_content = self.get_page_content(library_url)
        if not html_content:
            logger.error(f"Failed to fetch content for {library_name}")
            return

        # Extract navigation items
        nav_items = self.extract_navigation_items(html_content)

        if not nav_items:
            logger.warning(f"No navigation items found for {library_name}")
            # Try to extract and save the main page content
            main_content = self.extract_content(html_content)
            if main_content:
                markdown = self.html_to_markdown(main_content)
                self.save_markdown(library_name, library_name, markdown)
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
            self.save_markdown(library_name, title, markdown)

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
    base_url = "https://deepwiki.example.com"  # Replace with the actual base URL

    # Define the libraries to scrape
    libraries = [
        {
            "name": "example_library",
            "url": f"{base_url}/example_library"
        }
        # Add more libraries as needed
    ]

    scraper = DeepwikiScraper(base_url)
    scraper.run(libraries)
