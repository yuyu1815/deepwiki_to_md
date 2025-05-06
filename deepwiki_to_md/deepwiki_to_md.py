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

from .localization import get_message

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
        # インポートに失敗した場合、何もしないダミークラスを定義する
        class DirectDeepwikiScraper:
            def __init__(self, *args, **kwargs):
                pass
            def scrape_page(self, *args, **kwargs):
                raise NotImplementedError("DirectDeepwikiScraper is not available.")

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
        # インポートに失敗した場合、何もしないダミー関数を定義する
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
        # インポートに失敗した場合、何もしないダミークラスを定義する
        class DirectMarkdownScraper:
            def __init__(self, *args, **kwargs):
                pass
            def scrape_page(self, *args, **kwargs):
                raise NotImplementedError("DirectDeepwikiScraper is not available.")



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
        # インポートに失敗した場合、何もしないダミー関数を定義する
        def fix_markdown_links(directory):
            logger.error("fix_markdown_links module not available")
            return


class DeepwikiScraper:
    def __init__(self, output_dir="Documents", use_direct_scraper=False, use_alternative_scraper=False,
                 use_direct_md_scraper=False):
        """
        Initialize the DeepwikiScraper.
        DeepwikiScraperを初期化します。

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
                              変換されたMarkdownファイルを保存する基本ディレクトリ。

            use_direct_scraper (bool): Whether to use DirectDeepwikiScraper for scraping.
                                       スクレイピングにDirectDeepwikiScraperを使用するかどうか。

            use_alternative_scraper (bool): Whether to use scrape_deepwiki from direct_scraper.py for scraping.
                                            スクレイピングに direct_scraper.py の scrape_deepwiki を使用するかどうか。
                                            When True, this method is prioritized. Default is False.
                                            True の場合、この方法が優先されます。デフォルトは False。

            use_direct_md_scraper (bool): Whether to use DirectMarkdownScraper for direct Markdown scraping.
                                          Markdownの直接スクレイピングに DirectMarkdownScraper を使用するかどうか。
                                          When True, this method is prioritized over all others. Default is True.
                                          True の場合、この方法が最も優先されます。デフォルトは True。
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
        # DirectMarkdownScraperを初期化（最高優先度）
        if self.use_direct_md_scraper:
            self.direct_md_scraper = DirectMarkdownScraper(output_dir)

        # Initialize DirectDeepwikiScraper
        # DirectDeepwikiScraperを初期化
        if self.use_direct_scraper:
            self.direct_scraper = DirectDeepwikiScraper(output_dir)

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
        # 取得中のURLをログに出力
        logger.info(get_message('getting_page_content', url=url))

        # Use DirectDeepwikiScraper if enabled and library_name is provided
        # DirectDeepwikiScraperが有効でlibrary_nameが提供されている場合に使用
        if self.use_direct_scraper and library_name:
            try:
                logger.info(get_message('using_direct_scraper', url=url))
                # Use DirectDeepwikiScraper with debug mode disabled
                # デバッグモードを無効にしてDirectDeepwikiScraperを使用
                md_file_path = self.direct_scraper.scrape_page(url, library_name, save_html=True, debug=False)
                if md_file_path:
                    logger.info(get_message('direct_scraper_success', url=url, file_path=md_file_path))
                    # If DirectDeepwikiScraper was successful, we can return the HTML content from the regular request
                    # DirectDeepwikiScraperが成功した場合、通常のリクエストからHTMLコンテンツを返すことができる
                    # This ensures we have the HTML content for further processing
                    # これにより、さらなる処理のためにHTMLコンテンツを確保できる
            except Exception as e:
                logger.error(f"Error using DirectDeepwikiScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue with regular request if DirectDeepwikiScraper fails
                # DirectDeepwikiScraperが失敗した場合、通常のリクエストを続行

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

        logger.debug(f"Fixed links in {file_path}")

    def scrape_library(self, library_name, library_url):
        """
        Scrape a library and convert its content to Markdown.

        Args:
            library_name (str): The name of the library.
            library_url (str): The URL of the library.
        """
        logger.info(get_message('scraping_library', library_name=library_name))

        # Extract the path from the URL
        # URLからパスを抽出する
        parsed_url = urlparse(library_url)
        domain = parsed_url.netloc
        full_path = parsed_url.path.strip('/')  # Remove leading/trailing slashes
        # 先頭/末尾のスラッシュを削除

        # Check if the domain is a placeholder or example domain
        # ドメインがプレースホルダーまたはサンプルドメインであるかを確認する
        if "example.com" in domain or not domain:
            logger.error(f"Cannot scrape from placeholder or invalid domain: {domain}")
            logger.error(f"Please use a valid domain in the URL: {library_url}")
            return

        # Check if the domain is reachable
        # ドメインが到達可能かを確認する
        if not self.is_domain_reachable(domain):
            logger.error(f"Cannot connect to domain: {domain}")
            logger.error(f"Please check your internet connection and make sure the domain is correct: {library_url}")
            return

        # Extract the appropriate part of the path
        # パスの適切な部分を抽出する
        path_parts = full_path.split('/')
        if len(path_parts) > 2:
            # For URLs like "python/cpython/1-overview", extract "cpython"
            # 「python/cpython/1-overview」のようなURLの場合、「cpython」を抽出する
            url_path = path_parts[-2]  # Get the second-to-last part of the path
            # パスの最後から2番目の部分を取得する
        elif len(path_parts) > 1:
            url_path = path_parts[-1]  # Get the last part of the path
            # パスの最後の部分を取得する
        else:
            url_path = full_path

        # Use library_name for the folder name if it's provided, otherwise use url_path
        # library_nameが提供されている場合はフォルダ名に使用し、それ以外の場合はurl_pathを使用する
        folder_path = library_name if library_name else url_path

        # Prioritize using DirectMarkdownScraper (highest priority)
        # DirectMarkdownScraperの使用を優先する（最高優先度）
        if self.use_direct_md_scraper:
            logger.info(get_message('prioritizing_direct_md_scraper', url=library_url))
            try:
                # Use DirectMarkdownScraper to get the content directly as Markdown
                # DirectMarkdownScraperを使用してコンテンツを直接Markdownとして取得する
                md_files = self.direct_md_scraper.scrape_library(library_url, library_name)
                if md_files and len(md_files) > 0:
                    logger.info(get_message('direct_md_scraper_success', url=library_url, count=len(md_files)))
                    return
                else:
                    logger.warning(f"Failed to scrape {library_url} using DirectMarkdownScraper")
            except Exception as e:
                logger.error(f"Error using DirectMarkdownScraper for {library_url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                logger.info(get_message('falling_back_to_alternative', url=library_url))

        # Prioritize using direct_scraper.py scraper (second priority)
        # direct_scraper.pyスクレイパーの使用を優先する（第2優先度）
        if self.use_alternative_scraper:
            logger.info(get_message('prioritizing_scrape_deepwiki', url=library_url))
            try:
                # Use scrape_deepwiki to get the content
                # scrape_deepwikiを使用してコンテンツを取得する
                response = scrape_deepwiki(library_url, debug=False)
                if response and response.status_code == 200:
                    # Parse the response content
                    # レスポンスコンテンツを解析する
                    direct_html_content = response.text
                    # Extract the main content
                    # メインコンテンツを抽出する
                    main_content = self.extract_content(direct_html_content, library_url)
                    if main_content:
                        markdown = self.html_to_markdown(main_content)
                        self.save_markdown(library_name, library_name, markdown, folder_path)

                        # Fix markdown links in the output directory
                        # 出力ディレクトリ内のマークダウンリンクを修正する
                        md_directory = os.path.join(os.getcwd(), self.output_dir, folder_path, "md")
                        logger.info(get_message('fixing_markdown_links', directory=md_directory))
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
                logger.info(get_message('falling_back_to_standard', url=library_url))

        # If direct_scraper.py failed or is not used, fall back to the standard method
        # direct_scraper.pyが失敗したか使用されていない場合、標準メソッドにフォールバックする
        # Get the library's main page
        # ライブラリのメインページを取得する
        html_content = self.get_page_content(library_url)
        if not html_content:
            logger.error(f"Failed to fetch content for {library_name}")
            return

        # Extract navigation items, using the library URL as the base URL
        # ライブラリURLをベースURLとして使用してナビゲーション項目を抽出する
        nav_items = self.extract_navigation_items(html_content, library_url)

        if not nav_items:
            logger.warning(f"No navigation items found for {library_name}")

            # If no navigation items and direct_scraper.py already failed, use the original method
            # ナビゲーション項目がなく、direct_scraper.pyがすでに失敗している場合は、元のメソッドを使用する
            main_content = self.extract_content(html_content, library_url)
            if main_content:
                markdown = self.html_to_markdown(main_content)
                self.save_markdown(library_name, library_name, markdown, folder_path)

                # Fix markdown links in the output directory
                # 出力ディレクトリ内のマークダウンリンクを修正する
                md_directory = os.path.join(os.getcwd(), self.output_dir, folder_path, "md")
                logger.info(get_message('fixing_markdown_links', directory=md_directory))
                fix_markdown_links(md_directory)
            return

        # Process each navigation item
        # 各ナビゲーション項目を処理する
        for item in nav_items:
            title = item['title']
            url = item['url']

            logger.info(get_message('processing_title', title=title))

            # Add a small delay to avoid overwhelming the server
            # サーバーに過負荷をかけないように小さな遅延を追加する
            time.sleep(1)

            # Get the page content
            # ページコンテンツを取得する
            page_html = self.get_page_content(url, library_name=library_name)
            if not page_html:
                logger.error(f"Failed to fetch content for {title}")
                continue

            # Extract the main content
            # メインコンテンツを抽出する
            main_content = self.extract_content(page_html, url)
            if not main_content:
                logger.warning(f"No main content found for {title}")
                continue

            # Convert to Markdown
            # Markdownに変換する
            markdown = self.html_to_markdown(main_content)

            # Save the Markdown content
            # Markdownコンテンツを保存する
            self.save_markdown(library_name, title, markdown, folder_path)

        # After all navigation items are processed, fix markdown links in the output directory
        # すべてのナビゲーション項目が処理された後、出力ディレクトリ内のマークダウンリンクを修正する
        md_directory = os.path.join(os.getcwd(), self.output_dir, folder_path, "md")
        logger.info(get_message('fixing_markdown_links', directory=md_directory))
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
    # 代替スクレイパーを無効にする例（direct_scraper.pyは優先されません）
    # scraper_without_alternative = DeepwikiScraper(use_alternative_scraper=False)
    # scraper_without_alternative.run(libraries)

    # Example of using the DirectMarkdownScraper (highest priority)
    # DirectMarkdownScraperを使用する例（最高優先度）
    # scraper_with_direct_md = DeepwikiScraper(
    #     output_dir="DirectMarkdownDocuments",
    #     use_direct_scraper=False,
    #     use_alternative_scraper=False,
    #     use_direct_md_scraper=True
    # )
    # scraper_with_direct_md.run(libraries)
