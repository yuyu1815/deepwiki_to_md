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

# Import DirectDeepwikiScraper
try:
    from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper
except ImportError:
    # If the module import fails, try relative import
    try:
        from .direct_scraper import DirectDeepwikiScraper
    except ImportError:
        logging.error("Could not import DirectDeepwikiScraper module")
        # Define a dummy class that does nothing if import fails
        class DirectDeepwikiScraper:
            def __init__(self, *args, **kwargs):
                pass
            def scrape_page(self, *args, **kwargs):
                return None

# Import scrape_deepwiki from direct_scraper.py
try:
    from deepwiki_to_md.direct_scraper import scrape_deepwiki
except ImportError:
    # If the module import fails, try relative import
    try:
        from .direct_scraper import scrape_deepwiki
    except ImportError:
        logging.error("Could not import scrape_deepwiki function from direct_scraper.py")
        # Define a dummy function that does nothing if import fails
        def scrape_deepwiki(url):
            logging.error("scrape_deepwiki function not available")
            return None

# Import DirectMarkdownScraper
try:
    from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper
except ImportError:
    # If the module import fails, try relative import
    try:
        from .direct_md_scraper import DirectMarkdownScraper
    except ImportError:
        logging.error("Could not import DirectMarkdownScraper module")


        # Define a dummy class that does nothing if import fails
        class DirectMarkdownScraper:
            def __init__(self, *args, **kwargs):
                pass

            def scrape_page(self, *args, **kwargs):
                return None



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import fix_markdown_links function
try:
    from deepwiki_to_md.fix_markdown_links import fix_markdown_links
except ImportError:
    # If the module import fails, try relative import
    try:
        from .fix_markdown_links import fix_markdown_links
    except ImportError:
        logger.error("Could not import fix_markdown_links module")
        # Define a dummy function that does nothing if import fails
        def fix_markdown_links(directory):
            logger.error("fix_markdown_links module not available")
            return


class DeepwikiScraper:
    def __init__(self, output_dir="Documents", use_direct_scraper=False, use_alternative_scraper=False):
        """
        Initialize the DeepwikiScraper.

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
            use_direct_scraper (bool): Whether to use DirectDeepwikiScraper for scraping.
            use_alternative_scraper (bool): Whether to use scrape_deepwiki from direct_scraper.py for scraping. When True, this method is prioritized. Default is True.
            use_direct_md_scraper (bool): Whether to use DirectMarkdownScraper for direct Markdown scraping. When True, this method is prioritized over all others. Default is False.
        """
        if use_direct_scraper:
            self.use_direct_scraper = True
            self.use_alternative_scraper = False
            self.use_direct_md_scraper = False
        elif use_alternative_scraper:
            self.use_direct_scraper = False
            self.use_alternative_scraper = True
            self.use_direct_md_scraper = False
        else:
            self.use_direct_scraper = False
            self.use_alternative_scraper = False
            self.use_direct_md_scraper = True
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
            return True
        except (socket.timeout, socket.error):
            # If HTTPS fails, try HTTP (port 80)
            try:
                socket.create_connection((domain, 80), timeout=timeout)
                return True
            except (socket.timeout, socket.error):
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
                md_file_path = self.direct_scraper.scrape_page(url, library_name, save_html=True, debug=False)
                if md_file_path:
                    logger.info(f"DirectDeepwikiScraper successfully scraped {url} to {md_file_path}")
                    # If DirectDeepwikiScraper was successful, we can return the HTML content from the regular request
                    # This ensures we have the HTML content for further processing
            except Exception as e:
                logger.error(f"Error using DirectDeepwikiScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue with regular request if DirectDeepwikiScraper fails

        # Use requests to fetch the page
        retries = 0
        while retries <= max_retries:
            try:
                logger.info(f"Fetching {url} with requests")
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
                delay += random.uniform(0, 0.2)  # Add jitter
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

    def extract_content(self, html_content, url):
        """
        ページからメインコンテンツを抽出します。

        Args:
            html_content (str): ページのHTMLコンテンツ。
            url (str): コンテンツを抽出するページのURL。

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
            # ここで url 引数が利用可能になる
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
            # The path is already the last part of the URL path (e.g., "cpython")
            dir_path = os.path.join(os.path.abspath(os.getcwd()), self.output_dir, path, "md")
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

        # Fix markdown links in the file immediately after saving
        # Use a regular expression to replace links with URLs with links with empty parentheses
        link_pattern = re.compile(r'\[([^\]]+)\]\((?![\s\)])[^\)]+\)')

        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace links with URLs with links with empty parentheses
        modified_content = link_pattern.sub(r'[\1]()', content)

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        logger.debug(f"Fixed links in {file_path}")

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
                    main_content = self.extract_content(direct_html_content, library_url)
                    if main_content:
                        markdown = self.html_to_markdown(main_content)
                        self.save_markdown(library_name, library_name, markdown, url_path)

                        # Fix markdown links in the output directory
                        md_directory = os.path.join(os.getcwd(), self.output_dir, url_path, "md")
                        logger.info(f"Fixing markdown links in {md_directory}")
                        fix_markdown_links(md_directory)
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
        # Get the library's main page
        html_content = self.get_page_content(library_url)
        if not html_content:
            logger.error(f"Failed to fetch content for {library_name}")
            return

        # Extract navigation items, using the library URL as the base URL
        nav_items = self.extract_navigation_items(html_content, library_url)

        if not nav_items:
            logger.warning(f"No navigation items found for {library_name}")

            # If no navigation items and direct_scraper.py already failed, use the original method
            main_content = self.extract_content(html_content, library_url)
            if main_content:
                markdown = self.html_to_markdown(main_content)
                self.save_markdown(library_name, library_name, markdown, url_path)

                # Fix markdown links in the output directory
                md_directory = os.path.join(os.getcwd(), self.output_dir, url_path, "md")
                logger.info(f"Fixing markdown links in {md_directory}")
                fix_markdown_links(md_directory)
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
            main_content = self.extract_content(page_html, url)
            if not main_content:
                logger.warning(f"No main content found for {title}")
                continue

            # Convert to Markdown
            markdown = self.html_to_markdown(main_content)

            # Save the Markdown content
            self.save_markdown(library_name, title, markdown, url_path)

        # After all navigation items are processed, fix markdown links in the output directory
        md_directory = os.path.join(os.getcwd(), self.output_dir, url_path, "md")
        logger.info(f"Fixing markdown links in {md_directory}")
        fix_markdown_links(md_directory)

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
