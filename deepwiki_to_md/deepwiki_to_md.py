import logging
import os
import random
import re
import socket
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import utility functions for handling imports
try:
    # Try absolute import first
    from deepwiki_to_md.import_utils import import_scraping_modules, import_markdown_link_fixing_modules
except ImportError:
    # If absolute import fails, try relative import
    try:
        from .import_utils import import_scraping_modules, import_markdown_link_fixing_modules
    except ImportError as e:
        logger.error(f"Failed to import import_utils module: {e}")


        # Define minimal versions of the import functions if import_utils is not available
        def import_scraping_modules():
            logger.error("import_scraping_modules called but import_utils module is not available")
            return None, None, None


        def import_markdown_link_fixing_modules():
            logger.error("import_markdown_link_fixing_modules called but import_utils module is not available")
            return None, None

# Import scraping modules
DirectDeepwikiScraper, scrape_deepwiki, DirectMarkdownScraper = import_scraping_modules()

# Import markdown link fixing functions
fix_markdown_links, fix_markdown_links_in_file = import_markdown_link_fixing_modules()


class DeepwikiScraper:
    def __init__(self, output_dir="Documents", use_direct_scraper=False, use_alternative_scraper=False,
                 use_direct_md_scraper=True):
        """
        Initialize the DeepwikiScraper.

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
            use_direct_scraper (bool): Whether to use DirectDeepwikiScraper for scraping.
            use_alternative_scraper (bool): Whether to use scrape_deepwiki from direct_scraper.py for scraping.
            use_direct_md_scraper (bool): Whether to use DirectMarkdownScraper for direct Markdown scraping. Default is True.

        Note:
            Scraper priority (highest to lowest):
            1. DirectMarkdownScraper (if use_direct_md_scraper is True)
            2. scrape_deepwiki from direct_scraper.py (if use_alternative_scraper is True)
            3. DirectDeepwikiScraper (if use_direct_scraper is True)
            4. Standard scraping method (fallback)
        """
        # Set scraper flags based on parameters
        self.use_direct_md_scraper = use_direct_md_scraper
        self.use_alternative_scraper = use_alternative_scraper and not self.use_direct_md_scraper
        self.use_direct_scraper = use_direct_scraper and not self.use_direct_md_scraper
        self.output_dir = output_dir

        # Initialize DirectMarkdownScraper (highest priority)
        if self.use_direct_md_scraper:
            self.direct_md_scraper = DirectMarkdownScraper(output_dir)

        # Initialize DirectDeepwikiScraper
        if self.use_direct_scraper:
            self.direct_scraper = DirectDeepwikiScraper(output_dir)

        # Initialize requests session for static content
        self.session = requests.Session()
        # Set a user agent to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def is_domain_reachable(self, domain, timeout=3):
        """
        Check if a domain is reachable by attempting to establish a socket connection.

        Args:
            domain (str): The domain to check.
            timeout (int): The timeout in seconds for the connection attempt.

        Returns:
            bool: True if the domain is reachable, False otherwise.
        """
        # Try HTTPS (port 443) first
        try:
            socket.create_connection((domain, 443), timeout=timeout)
            logger.debug(f"HTTPS connection to {domain} succeeded")
            return True
        except (socket.timeout, socket.gaierror, socket.herror, socket.error) as e:
            # Log the specific error for debugging
            logger.debug(f"HTTPS connection to {domain} failed: {e}")
            # If HTTPS fails, try HTTP (port 80)
            try:
                socket.create_connection((domain, 80), timeout=timeout)
                logger.debug(f"HTTP connection to {domain} succeeded")
                return True
            except (socket.timeout, socket.gaierror, socket.herror, socket.error) as e:
                # Log the specific error for debugging
                logger.debug(f"HTTP connection to {domain} failed: {e}")
                return False

    # Selenium methods removed - only static requests are supported

    def get_page_content(self, url, max_retries=3, base_delay=1, library_name=None):
        """
        Get the HTML content of a page with retry mechanism and exponential backoff.
        If DirectDeepwikiScraper is enabled, it will be used for scraping.

        Args:
            url (str): The URL to fetch.
            max_retries (int): Maximum number of retry attempts.
            base_delay (int): Base delay in seconds between retries.
            library_name (str, optional): The name of the library for DirectDeepwikiScraper.

        Returns:
            str: The HTML content of the page.
        """
        # Log the URL being fetched
        logger.info(f"Getting page content for URL: {url}")

        # Use DirectDeepwikiScraper if enabled and library_name is provided
        if self.use_direct_scraper and library_name:
            try:
                logger.info(f"Using DirectDeepwikiScraper for {url}")
                # Use DirectDeepwikiScraper with debug mode disabled
                md_file_path = self.direct_scraper.scrape_page(url, library_name, debug=False)
                if md_file_path:
                    logger.info(f"DirectDeepwikiScraper successfully scraped {url} to {md_file_path}")
                    # If DirectDeepwikiScraper was successful, we can return the HTML content from the regular request
                    # This ensures we have the HTML content for further processing
            except Exception as e:
                logger.error(f"Error using DirectDeepwikiScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue with regular request if DirectDeepwikiScraper fails for any reason

        # Use requests to fetch the page
        retries = 0
        while retries < max_retries and max_retries >= 0:  # Ensure max_retries is non-negative
            try:
                logger.info(f"Fetching {url} with requests")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries >= max_retries:  # Changed from > to >= for clarity
                    logger.error(f"Error fetching {url} after {max_retries} retries: {e}")
                    return None

                # Calculate exponential backoff delay with jitter
                delay = base_delay * (2 ** (retries - 1))
                delay += random.uniform(0, 0.5)  # Increased jitter range for better randomization
                logger.warning(f"Retry {retries}/{max_retries} for {url} after {delay:.2f}s delay. Error: {e}")
                time.sleep(delay)

        return None

    # Selenium methods removed - only static requests are supported

    # Selenium cleanup methods removed - only static requests are supported

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

    def extract_content(self, html_content, url, library_name=None):
        """
        ページからメインコンテンツを抽出します。

        Args:
            html_content (str): ページのHTMLコンテンツ。
            url (str): コンテンツを抽出するページのURL。
            library_name (str, optional): ライブラリの名前。エラーログに含めるために使用されます。

        Returns:
            BeautifulSoup.Tag | str: ページのメインコンテンツ要素、または見つからない場合は空文字列。
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        # メインコンテンツの可能性のあるセレクターを複数試す
        # より具体的なものから一般的なものへ
        selectors = [
            'main article',  # 元のセレクター
            'main .content',  # メインコンテンツの一般的なパターン
            'main',  # main要素
            'article',  # article要素
            '.content',  # contentクラス
            '.article-content',  # article-contentクラス
            '#content',  # content ID
            '.markdown-body',  # markdownコンテンツの一般的なクラス
            '.documentation-content',  # ドキュメンテーションコンテンツの一般的なクラス
            'div.container div.row div.col'  # Bootstrapのようなレイアウト
        ]

        main_content = None
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text(strip=True)) > 0:
                logger.info(f"セレクターを使用してコンテンツを発見: {selector}")
                break

        if not main_content:
            # 特定のコンテナが見つからない場合、bodyまたは最大のテキストコンテナを取得しようとする
            body = soup.find('body')
            if body:
                # 最も多くのテキストコンテンツを持つdivを見つける
                divs = body.find_all('div', recursive=False)
                if divs:
                    main_content = max(divs, key=lambda x: len(x.get_text(strip=True)))
                else:
                    main_content = body

        if not main_content or len(main_content.get_text(strip=True)) == 0:
            # ここで url 引数と library_name 引数が利用可能になる
            if library_name:
                logger.warning(f"URLのメインコンテンツ要素が見つかりません: {url} (ライブラリ: {library_name})")
            else:
                logger.warning(f"URLのメインコンテンツ要素が見つかりません: {url}")
            return ""

        return main_content

    def html_to_markdown(self, html_element):
        """
        Convert HTML content to Markdown using markdownify.

        This method performs the following operations:
        1. Removes the navigation menu (ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1)
        2. Converts the HTML to Markdown format

        Args:
            html_element: The BeautifulSoup element containing the HTML content.

        Returns:
            str: The content converted to Markdown.
        """
        if not html_element:
            return ""

        # If html_element is already a BeautifulSoup object, use it directly
        # Otherwise, parse it with BeautifulSoup
        if isinstance(html_element, BeautifulSoup):
            soup = html_element
        elif hasattr(html_element, 'name'):  # Check if it's a BeautifulSoup Tag
            soup = BeautifulSoup(str(html_element), 'html.parser')
        else:
            soup = BeautifulSoup(str(html_element), 'html.parser')

        # Find and remove the navigation menu
        nav_ul = soup.select_one('ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1')
        if nav_ul:
            nav_ul.decompose()
            logger.info("Navigation menu removed before Markdown conversion")

        # Convert the modified HTML to string
        html_str = str(soup)

        # Use markdownify to convert HTML to Markdown
        markdown = markdownify(html_str, heading_style="ATX")

        return markdown

    def construct_dir_path(self, path=None, library_name=None):
        """
        Construct the directory path for saving files.

        Args:
            path (str, optional): The path to use for the directory structure. If None, only library_name is used.
            library_name (str, optional): The name of the library. Required if path is None.

        Returns:
            str: The constructed directory path.
        """
        if path:
            # Use the path from the URL for the directory structure
            dir_path = os.path.join(os.path.abspath(os.getcwd()), self.output_dir, path, "md")
        else:
            # Fallback to the old behavior
            if not library_name:
                raise ValueError("library_name must be provided when path is None")
            dir_path = os.path.join(os.path.abspath(os.getcwd()), self.output_dir, library_name, "md")
        return dir_path

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
        dir_path = self.construct_dir_path(path, library_name)
        os.makedirs(dir_path, exist_ok=True)

        # Sanitize the title to create a valid filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        filename = re.sub(r'\s+', '_', filename)

        # Remove the first 28 lines from the markdown content
        if markdown_content:
            lines = markdown_content.split('\n')
            if len(lines) > 28:
                markdown_content = '\n'.join(lines[28:])
                logger.info(f"Removed the first 28 lines from {filename}.md")

        # Save the Markdown content to a file
        file_path = os.path.join(dir_path, f"{filename}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Saved {file_path}")

        # Fix markdown links in the file immediately after saving
        try:
            fix_markdown_links_in_file(file_path)
            logger.debug(f"Fixed links in {file_path}")
        except Exception as e:
            logger.error(f"Error fixing links in {file_path}: {e}")

    def scrape_library(self, library_name, library_url):
        """
        Scrape a library and convert its content to Markdown.

        Args:
            library_name (str): The name of the library.
            library_url (str): The URL of the library.
        """
        logger.info(f"Scraping library: {library_name}")

        # Initialize html_content to None
        html_content = None

        # Extract the path from the URL
        parsed_url = urlparse(library_url)
        domain = parsed_url.netloc
        full_path = parsed_url.path.strip('/')  # Remove leading/trailing slashes

        # Check if the domain is a placeholder or example domain
        if "example.com" in domain or not domain:
            logger.error(f"Cannot scrape from placeholder or invalid domain: {domain}")
            logger.error(f"Please use a valid domain in the URL: {library_url}")
            return

        # Check if the domain is reachable
        if not self.is_domain_reachable(domain):
            logger.error(f"Cannot connect to domain: {domain}")
            logger.error(f"Please check your internet connection and make sure the domain is correct: {library_url}")
            return

        # Extract the appropriate part of the path
        path_parts = full_path.split('/')
        if len(path_parts) > 2:
            # For URLs like "python/cpython/1-overview", extract "cpython"
            url_path = path_parts[-2]  # Get the second-to-last part of the path
        elif len(path_parts) > 1:
            url_path = path_parts[-1]  # Get the last part of the path
        else:
            url_path = full_path

        # Prioritize using DirectMarkdownScraper (highest priority)
        if self.use_direct_md_scraper:
            logger.info(f"Prioritizing DirectMarkdownScraper for {library_url}")
            try:
                # Use DirectMarkdownScraper to get the content directly as Markdown
                md_files = self.direct_md_scraper.scrape_library(library_url, library_name)
                if md_files and len(md_files) > 0:
                    logger.info(
                        f"Successfully scraped {library_url} and {len(md_files)} pages using DirectMarkdownScraper")
                    return
                else:
                    logger.warning(f"Failed to scrape {library_url} using DirectMarkdownScraper")
            except Exception as e:
                logger.error(f"Error using DirectMarkdownScraper for {library_url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                logger.info(f"Falling back to alternative scraping methods for {library_url}")

        # Prioritize using direct_scraper.py scraper (second priority)
        if self.use_alternative_scraper:
            logger.info(f"Prioritizing scrape_deepwiki from direct_scraper.py for {library_url}")
            try:
                # Use scrape_deepwiki to get the content
                response = scrape_deepwiki(library_url, debug=False)
                if response and response.status_code == 200:
                    # Parse the response content
                    direct_html_content = response.text
                    # Extract the main content
                    main_content = self.extract_content(direct_html_content, library_url, library_name)
                    if main_content:
                        markdown = self.html_to_markdown(main_content)
                        self.save_markdown(library_name, library_name, markdown, url_path)

                        # Fix markdown links in the output directory
                        self.fix_markdown_links_in_directory(url_path)
                        return
                    else:
                        logger.warning(f"No main content found in response from scrape_deepwiki for {library_url}")
                else:
                    logger.error(f"Failed to fetch content with scrape_deepwiki for {library_url}")
            except Exception as e:
                logger.error(f"Error using scrape_deepwiki for {library_url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                logger.info(f"Falling back to standard scraping method for {library_url}")

        # If direct_scraper.py failed or is not used, fall back to the standard method
        # Get the library's main page if we don't have content yet
        if not html_content:
            html_content = self.get_page_content(library_url)
            if not html_content:
                logger.error(f"Failed to fetch content for {library_name}")
                return

        # Extract navigation items, using the library URL as the base URL
        nav_items = self.extract_navigation_items(html_content, library_url)

        if not nav_items:
            logger.warning(f"No navigation items found for {library_name}")

            # If no navigation items and direct_scraper.py already failed, use the original method
            main_content = self.extract_content(html_content, library_url, library_name)
            if main_content:
                markdown = self.html_to_markdown(main_content)
                self.save_markdown(library_name, library_name, markdown, url_path)

                # Fix markdown links in the output directory
                self.fix_markdown_links_in_directory(url_path)
            return

        # Process each navigation item
        for item in nav_items:
            title = item['title']
            url = item['url']

            logger.info(f"Processing: {title}")

            # Add a small delay to avoid overwhelming the server
            time.sleep(1)

            # Get the page content
            page_html = self.get_page_content(url, library_name=library_name)
            if not page_html:
                logger.error(f"Failed to fetch content for {title}")
                continue

            # Extract the main content
            main_content = self.extract_content(page_html, url, library_name)
            if not main_content:
                logger.warning(f"No main content found for {title}")
                continue

            # Convert to Markdown
            markdown = self.html_to_markdown(main_content)

            # Save the Markdown content
            self.save_markdown(library_name, title, markdown, url_path)

        # After all navigation items are processed, fix markdown links in the output directory
        self.fix_markdown_links_in_directory(url_path)

    def fix_markdown_links_in_directory(self, path):
        """
        Fix markdown links in the specified directory.

        Args:
            path (str): The path to use for the directory structure.
        """
        try:
            md_directory = self.construct_dir_path(path)
            logger.info(f"Fixing markdown links in {md_directory}")
            fix_markdown_links(md_directory)
        except Exception as e:
            logger.error(f"Error fixing markdown links in {md_directory}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Log the error but don't re-raise it to avoid interrupting the scraping process
            # This allows the scraping to continue even if link fixing fails

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

    # Create a scraper with default settings (using alternative scraper by default)
    scraper = DeepwikiScraper()
    scraper.run(libraries)

    # Example of disabling the alternative scraper (direct_scraper.py will not be prioritized)
    # scraper_without_alternative = DeepwikiScraper(use_alternative_scraper=False)
    # scraper_without_alternative.run(libraries)

    # Example of using the DirectMarkdownScraper (highest priority)
    # scraper_with_direct_md = DeepwikiScraper(
    #     output_dir="DirectMarkdownDocuments",
    #     use_direct_scraper=False,
    #     use_alternative_scraper=False,
    #     use_direct_md_scraper=True
    # )
    # scraper_with_direct_md.run(libraries)
