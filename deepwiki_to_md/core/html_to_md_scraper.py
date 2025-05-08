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

# Import fix_markdown_links function
try:
    from deepwiki_to_md.core.fix_markdown_links import fix_markdown_links
except ImportError:
    from .fix_markdown_links import fix_markdown_links

# Import localization
try:
    from deepwiki_to_md.lang.localization import get_message
except ImportError:
    from .lang.localization import get_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTMLToMarkdownScraper:
    def __init__(self, output_dir="Documents"):
        """
        Initialize the HTMLToMarkdownScraper.
        HTMLToMarkdownScraperを初期化します。

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
                              変換されたMarkdownファイルを保存する基本ディレクトリ。
        """
        self.output_dir = output_dir

        # Initialize requests session for static content
        # 静的コンテンツ用のリクエストセッションを初期化
        self.session = requests.Session()
        # Set a user agent to mimic a browser
        # ブラウザを模倣するユーザーエージェントを設定
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
        # まずHTTPS（ポート443）を試す
        try:
            socket.create_connection((domain, 443), timeout=timeout)
            return True
        except (socket.timeout, socket.error):
            # If HTTPS fails, try HTTP (port 80)
            # HTTPSが失敗した場合、HTTP（ポート80）を試す
            try:
                socket.create_connection((domain, 80), timeout=timeout)
                return True
            except (socket.timeout, socket.error):
                return False

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
        # Log the URL being fetched
        # 取得中のURLをログに出力
        logger.info(get_message('getting_page_content', url=url))

        # Use requests to fetch the page
        # requestsを使用してページを取得
        retries = 0
        while retries <= max_retries:
            try:
                logger.info(get_message('fetching_with_requests', url=url))
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Error fetching {url} after {max_retries} retries: {e}")
                    return None

                # Calculate exponential backoff delay with jitter
                # ジッター付きの指数バックオフ遅延を計算
                delay = base_delay * (2 ** (retries - 1))
                delay += random.uniform(0, 0.2)  # Add jitter
                # ジッターを追加
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

    def extract_content(self, html_content, url):
        """
        Extract the main content from the page.

        Args:
            html_content (str): The HTML content of the page.
            url (str): The URL of the page to extract content from.

        Returns:
            BeautifulSoup.Tag | str: The main content element of the page, or an empty string if not found.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        # Try multiple potential selectors for the main content
        # メインコンテンツの可能性のあるセレクターを複数試す
        # From more specific to more general
        # より具体的なものから一般的なものへ
        selectors = [
            'main article',  # Original selector
            # 元のセレクター
            'main .content',  # Common pattern for main content
            # メインコンテンツの一般的なパターン
            'main',  # Main element
            # main要素
            'article',  # Article element
            # article要素
            '.content',  # Content class
            # contentクラス
            '.article-content',  # Article-content class
            # article-contentクラス
            '#content',  # Content ID
            # content ID
            '.markdown-body',  # Common class for markdown content
            # markdownコンテンツの一般的なクラス
            '.documentation-content',  # Common class for documentation content
            # ドキュメンテーションコンテンツの一般的なクラス
            'div.container div.row div.col'  # Bootstrap-like layout
            # Bootstrapのようなレイアウト
        ]

        main_content = None
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text(strip=True)) > 0:
                logger.info(get_message('content_found_with_selector', selector=selector))
                # Content found using selector
                break

        if not main_content:
            # 特定のコンテナが見つからない場合、bodyまたは最大のテキストコンテナを取得しようとする
            # If a specific container is not found, try to get the body or the largest text container
            body = soup.find('body')
            if body:
                # 最も多くのテキストコンテンツを持つdivを見つける
                # Find the div with the most text content
                divs = body.find_all('div', recursive=False)
                if divs:
                    main_content = max(divs, key=lambda x: len(x.get_text(strip=True)))
                else:
                    main_content = body

        if not main_content or len(main_content.get_text(strip=True)) == 0:
            # ここで url 引数が利用可能になる
            # The url argument becomes available here
            logger.warning(f"URLのメインコンテンツ要素が見つかりません: {url}")
            # Main content element not found for URL
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
        # ナビゲーションメニューを見つけて削除する
        nav_ul = soup.select_one('ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1')
        if nav_ul:
            nav_ul.decompose()
            logger.info(get_message('navigation_menu_removed'))

        # Convert the modified HTML to string
        # 変更されたHTMLを文字列に変換する
        html_str = str(soup)

        # Use markdownify to convert HTML to Markdown
        # markdownifyを使用してHTMLをMarkdownに変換する
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
        # ディレクトリ構造が存在しない場合は作成する
        # Use current working directory instead of a fixed path
        # 固定パスの代わりに現在の作業ディレクトリを使用する
        if path:
            # Use the path from the URL for the directory structure
            # URLのパスをディレクトリ構造に使用する
            # The path is already the last part of the URL path (e.g., "cpython")
            # パスはすでにURLパスの最後の部分（例：「cpython」）です
            dir_path = os.path.join(os.path.abspath(os.getcwd()), self.output_dir, path, "md")
        else:
            # Fallback to the old behavior
            # 古い動作にフォールバックする
            dir_path = os.path.join(os.getcwd(), self.output_dir, library_name, "md")
        os.makedirs(dir_path, exist_ok=True)

        # Sanitize the title to create a valid filename
        # タイトルをサニタイズして有効なファイル名を作成する
        filename = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        filename = re.sub(r'\s+', '_', filename)

        # Remove the first 28 lines from the markdown content
        # markdownコンテンツの最初の28行を削除する
        if markdown_content:
            lines = markdown_content.split('\n')
            if len(lines) > 28:
                markdown_content = '\n'.join(lines[28:])
                logger.info(get_message('removed_first_lines', count=28, filename=filename))

        # Save the Markdown content to a file
        # Markdownコンテンツをファイルに保存する
        file_path = os.path.join(dir_path, f"{filename}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(get_message('saved_file', file_path=file_path))

        # Fix markdown links in the file immediately after saving
        # 保存直後にファイル内のマークダウンリンクを修正する
        # Use a regular expression to replace links with URLs with links with empty parentheses
        # 正規表現を使用して、URL付きのリンクを空の括弧付きのリンクに置き換える
        link_pattern = re.compile(r'\[([^\]]+)\]\((?![s\)])[^\)]+\)')

        # Read the file content
        # ファイルの内容を読み取る
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace links with URLs with links with empty parentheses
        # URL付きのリンクを空の括弧付きのリンクに置き換える
        modified_content = link_pattern.sub(r'[\1]()', content)

        # Write the modified content back to the file
        # 変更された内容をファイルに書き戻す
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        logger.debug(get_message('fixed_links', file_path=file_path))

        return file_path

    def scrape_page(self, url, library_name=None):
        """
        Scrape a page and convert it to Markdown.

        Args:
            url (str): The URL of the page to scrape.
            library_name (str, optional): The name of the library. If None, it will be extracted from the URL.

        Returns:
            str: The path to the saved Markdown file, or None if scraping failed.
        """
        # Get the HTML content of the page
        html_content = self.get_page_content(url)
        if not html_content:
            logger.error(get_message('failed_get_html', url=url))
            return None

        # Extract the main content from the HTML
        main_content = self.extract_content(html_content, url)
        if not main_content:
            logger.error(get_message('failed_extract_content', url=url))
            return None

        # Convert the HTML content to Markdown
        markdown_content = self.html_to_markdown(main_content)
        if not markdown_content:
            logger.error(get_message('failed_convert_html', url=url))
            return None

        # Extract the title from the URL
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        path_parts = path.split('/')
        title = path_parts[-1] if path_parts else "index"

        # If library_name is not provided, extract it from the URL
        if not library_name and len(path_parts) > 1:
            library_name = path_parts[-2]

        # Save the Markdown content to a file
        file_path = self.save_markdown(library_name or "unknown", title, markdown_content, path=library_name)

        return file_path
