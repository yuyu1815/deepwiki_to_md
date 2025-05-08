import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

try:
    from deepwiki_to_md.lang.localization import get_message
except ImportError:
    from ..lang.localization import get_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_deepwiki(url, debug=False):
    """
    指定されたURLからdeepwikiコンテンツをスクレイピングする関数
    # Function to scrape deepwiki content from the specified URL

    Args:
        url: スクレイピングするdeepwikiのURL（例：https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization）
        debug: デバッグモードを有効にするかどうか
        # url: The URL of the deepwiki page to scrape (e.g., https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization)
        # debug: Whether to enable debug mode

    Returns:
        requests.Response: レスポンスオブジェクト
        # requests.Response: The response object
    """
    # URLからドメインとパスを抽出
    # Extract domain and path from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # 正しいURLをログに出力
    # Log the correct URL
    logger.info(get_message("scraping_start_with_path", url=url, path=path))

    # セッションの作成
    # Create a session
    session = requests.Session()

    # 一般的なブラウザのUser-Agentを使用
    # Use a common browser User-Agent
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    })

    # URLを解析してリファラーを作成（URLの一部を使用）
    # Parse the URL to create a referrer (using part of the URL)
    path_parts = path.strip('/').split('/')
    referer_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else path

    # クエリパラメータを保持
    # Keep query parameters
    query = parsed_url.query
    full_url = f"{parsed_url.scheme}://{domain}{path}"
    if query:
        full_url += f"?{query}"

    # 簡略化したヘッダーを使用（必要最小限）
    # Use simplified headers (minimum required)
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": f"{parsed_url.scheme}://{domain}/{referer_path}",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    logger.info(get_message("request_execution", url=full_url))

    # リクエストの実行
    # Execute the request
    try:
        response = session.get(full_url, headers=headers, timeout=10)
        logger.info(get_message("response_status", status_code=response.status_code))

        # デバッグモードの場合、レスポンスの内容を保存
        # If debug mode is enabled, save the response content
        if debug:
            debug_dir = "debug_html"
            os.makedirs(debug_dir, exist_ok=True)
            filename = path.strip('/').replace('/', '_')
            if not filename:
                filename = "index"
            debug_file = os.path.join(debug_dir, f"{filename}.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(get_message("debug_html_saved", file=debug_file))

            # レスポンスヘッダーも保存
            # Also save the response headers
            headers_file = os.path.join(debug_dir, f"{filename}_headers.txt")
            with open(headers_file, 'w', encoding='utf-8') as f:
                for key, value in response.headers.items():
                    f.write(f"{key}: {value}\n")
            logger.info(get_message("debug_headers_saved", file=headers_file))

        return response
    except Exception as e:
        logger.error(get_message("request_error", error=str(e)))
        # Error occurred during request
        raise


class DirectDeepwikiScraper:
    def __init__(self, output_dir="DynamicDocuments"):
        """
        Initialize the DirectDeepwikiScraper.

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
        """
        self.output_dir = output_dir

    def extract_content(self, html_content):
        """
        HTMLコンテンツからメインコンテンツを抽出し、Markdownに変換する

        Args:
            html_content (str): HTMLコンテンツ

        Returns:
            tuple: (markdown_content, html_content) - 変換されたMarkdownコンテンツとHTMLコンテンツ
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # HTMLの基本情報をログに出力
        # Log basic HTML information
        logger.info(get_message("html_length", bytes=len(html_content)))
        logger.info(get_message("html_title", title=soup.title.string if soup.title else 'タイトルなし'))

        # メインコンテンツの可能性のあるセレクターを複数試す
        # より具体的なものから一般的なものへ
        # Try multiple possible selectors for the main content
        # From more specific to more general
        selectors = [
            'main article',  # 元のセレクター
            # Original selector
            'main',
            # main要素
            # main element
            'main .content',
            # メインコンテンツの一般的なパターン
            # Common pattern for main content
            'article',
            # article要素
            # article element
            '.content',
            # contentクラス
            # content class
            '.article-content',
            # article-contentクラス
            # article-content class
            '#content',
            # content ID
            # content ID
            '.markdown-body',
            # markdownコンテンツの一般的なクラス
            # Common class for markdown content
            '.documentation-content',
            # ドキュメンテーションコンテンツの一般的なクラス
            # Common class for documentation content
            'div.container div.row div.col',
            # Bootstrapのようなレイアウト
            # Bootstrap-like layout
            '#__next',
            # Next.jsアプリケーションのルート要素
            # Root element of Next.js application
            'div[role="main"]',
            # メインコンテンツのrole属性
            # role attribute for main content
            '.prose',
            # Tailwind CSSのproseクラス
            # prose class in Tailwind CSS
            '.page-content'
            # ページコンテンツクラス
            # page content class
        ]

        # 各セレクターの存在をログに出力
        for selector in selectors:
            element = soup.select_one(selector)
            logger.debug(f"セレクター '{selector}' の存在: {element is not None}")
            if element:
                logger.debug(f"セレクター '{selector}' のテキスト長: {len(element.get_text(strip=True))}")

        main_content = None
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text(strip=True)) > 0:
                logger.info(get_message("content_found_with_selector_direct", selector=selector))
                break

        # セレクターでコンテンツが見つからない場合、最大のテキストコンテンツを持つ要素を探す
        # If content is not found by selector, search for the element with the largest text content
        if not main_content:
            logger.info("セレクターでコンテンツが見つからないため、最大テキストコンテンツを探索")
            # 特定のコンテナが見つからない場合、bodyまたは最大のテキストコンテナを取得しようとする
            # If a specific container is not found, try to get the body or the largest text container
            body = soup.find('body')
            if body:
                # 最も多くのテキストコンテンツを持つdivを見つける
                # Find the div with the most text content
                divs = body.find_all('div', recursive=False)
                if divs:
                    logger.info(f"body直下のdiv要素数: {len(divs)}")
                    # 各divのテキスト長をログに出力
                    # Log the text length of each div
                    for i, div in enumerate(divs[:5]):
                        # 最初の5つだけログに出力
                        # Log only the first 5
                        text_len = len(div.get_text(strip=True))
                        logger.debug(f"div[{i}] テキスト長: {text_len}")

                    main_content = max(divs, key=lambda x: len(x.get_text(strip=True)))
                    logger.info(
                        f"最大テキストコンテンツを持つdivを使用 (テキスト長: {len(main_content.get_text(strip=True))})")
                else:
                    main_content = body
                    logger.info(f"body要素を使用 (テキスト長: {len(body.get_text(strip=True))})")
            else:
                logger.warning("body要素が見つかりません")

        if not main_content or len(main_content.get_text(strip=True)) == 0:
            logger.warning("メインコンテンツが見つかりませんでした")
            return None, html_content

        # Markdownに変換
        # Convert to Markdown
        markdown_content = markdownify(str(main_content))
        logger.info(f"Markdown変換後の長さ: {len(markdown_content)} バイト")

        return markdown_content, html_content

    def save_markdown(self, markdown_content, library_name, page_path, save_html=False, html_content=None):
        """
        Markdownコンテンツをファイルに保存する

        Args:
            markdown_content (str): 保存するMarkdownコンテンツ
            library_name (str): ライブラリ名
            page_path (str): ページのパス
            save_html (bool): HTMLも保存するかどうか
            html_content (str): 保存するHTMLコンテンツ

        Returns:
            str: 保存したファイルのパス
        """
        # 出力ディレクトリを作成
        # Create the output directory
        output_path = os.path.join(self.output_dir, library_name, 'md')
        os.makedirs(output_path, exist_ok=True)

        # ファイル名を作成
        # Create the filename
        filename = page_path.strip('/').split('/')[-1] if page_path else 'index'
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # 無効な文字を置換
        # Replace invalid characters

        # 最初の28行を削除
        # Remove the first 28 lines
        if markdown_content:
            lines = markdown_content.split('\n')
            if len(lines) > 28:
                markdown_content = '\n'.join(lines[28:])
                logger.info(f"最初の28行を削除しました: {filename}.md")

        # Markdownファイルを保存
        # Save the Markdown file
        md_file_path = os.path.join(output_path, f"{filename}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # HTMLも保存する場合
        # If saving HTML as well
        if save_html and html_content:
            html_output_path = os.path.join(self.output_dir, library_name, 'html')
            os.makedirs(html_output_path, exist_ok=True)
            html_file_path = os.path.join(html_output_path, f"{filename}.html")
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return md_file_path

    def scrape_page(self, url, library_name, save_html=True, debug=False):
        """
        指定されたURLのページをスクレイピングし、Markdownに変換して保存する

        Args:
            url (str): スクレイピングするURL
            library_name (str): ライブラリ名
            save_html (bool): HTMLも保存するかどうか
            debug (bool): デバッグモードを有効にするかどうか

        Returns:
            str: 保存したMarkdownファイルのパス、失敗した場合はNone
        """
        try:
            # URLをログに出力
            # Log the URL
            logger.info(f"scrape_page: URL = {url}, type = {type(url)}")

            # URLの各部分を解析
            # Parse each part of the URL
            parsed_url = urlparse(url)
            logger.info(f"scrape_page: parsed_url = {parsed_url}")
            logger.info(
                f"scrape_page: scheme = {parsed_url.scheme}, netloc = {parsed_url.netloc}, path = {parsed_url.path}")

            # 正しいURLを構築
            # Construct the correct URL
            correct_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            logger.info(f"scrape_page: correct_url = {correct_url}")

            # ページをスクレイピング（デバッグモード有効）
            # Scrape the page (debug mode enabled)
            response = scrape_deepwiki(correct_url, debug=debug)
            if response.status_code != 200:
                logger.error(f"ページの取得に失敗しました: {url} (ステータスコード: {response.status_code})")
                return None

            # URLからページパスを抽出
            # Extract the page path from the URL
            parsed_url = urlparse(url)
            page_path = parsed_url.path

            # HTMLの長さをログに出力
            # Log the length of the HTML
            html_length = len(response.text)
            logger.info(f"取得したHTMLの長さ: {html_length} バイト")

            # HTMLの一部をログに出力（デバッグ用）
            # Log a part of the HTML (for debugging)
            if debug:
                preview_length = min(500, html_length)
                logger.debug(f"HTML プレビュー: {response.text[:preview_length]}...")

            # コンテンツを抽出してMarkdownに変換
            # Extract content and convert to Markdown
            markdown_content, html_content = self.extract_content(response.text)
            if not markdown_content:
                logger.error(f"コンテンツの抽出に失敗しました: {url}")

                # デバッグモードの場合、HTMLの構造を分析
                # If debug mode is enabled, analyze the HTML structure
                if debug:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    logger.debug(f"HTML構造: {soup.title.string if soup.title else 'タイトルなし'}")
                    logger.debug(f"メタタグ数: {len(soup.find_all('meta'))}")
                    logger.debug(f"スクリプトタグ数: {len(soup.find_all('script'))}")
                    logger.debug(f"divタグ数: {len(soup.find_all('div'))}")

                    # 主要なタグの存在を確認
                    # Check the existence of major tags
                    for tag in ['main', 'article', 'content', '.markdown-body']:
                        element = soup.select_one(tag)
                        logger.debug(f"タグ '{tag}' の存在: {element is not None}")

                return None

            # ファイルに保存
            # Save to file
            return self.save_markdown(markdown_content, library_name, page_path, save_html, html_content)

        except Exception as e:
            logger.error(f"ページのスクレイピングに失敗しました: {url} ({e})")
            import traceback
            logger.error(traceback.format_exc())
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

        logger.info(get_message('extracted_nav_items', count=len(nav_items)))
        return nav_items

    def scrape_library(self, library_url, library_name, save_html=True):
        """
        指定されたライブラリのページをスクレイピングする

        Args:
            library_url (str): ライブラリのURL
            library_name (str): ライブラリ名
            save_html (bool): HTMLも保存するかどうか

        Returns:
            list: 保存したMarkdownファイルのパスのリスト
        """
        logger.info(get_message('starting_library_scrape', name=library_name, url=library_url))

        # まずメインページをスクレイピング
        # First, scrape the main page
        main_page_path = self.scrape_page(library_url, library_name, save_html)
        if not main_page_path:
            logger.error(get_message('main_page_scrape_failed', url=library_url))
            return []

        # HTMLコンテンツを取得してナビゲーション項目を抽出
        try:
            # 通常のHTTPリクエストを使用してHTMLを取得
            # Get HTML using a normal HTTP request
            response = scrape_deepwiki(library_url)
            if response.status_code != 200:
                logger.error(get_message('html_fetch_failed', url=library_url, status_code=response.status_code))
                return [main_page_path]  # メインページのみ返す
                # Return only the main page

            # ナビゲーション項目を抽出
            # Extract navigation items
            nav_items = self.extract_navigation_items(response.text, library_url)

            if not nav_items:
                logger.warning(get_message('no_nav_items', url=library_url))
                return [main_page_path]  # メインページのみ返す
                # Return only the main page

            # 保存したファイルのパスのリスト
            # List of paths to saved files
            md_files = [main_page_path]

            # 各ナビゲーション項目をスクレイピング
            # Scrape each navigation item
            for item in nav_items:
                title = item['title']
                url = item['url']

                logger.info(get_message('scraping_nav_item', title=title, url=url))

                # 小さな遅延を入れてサーバーに負荷をかけないようにする
                # Add a small delay to avoid overloading the server
                import time
                time.sleep(1)

                # ページをスクレイピング
                # Scrape the page
                page_path = self.scrape_page(url, library_name, save_html)
                if page_path:
                    md_files.append(page_path)
                else:
                    logger.error(get_message('nav_item_scrape_failed', title=title, url=url))

            return md_files
        except Exception as e:
            logger.error(get_message('nav_extraction_error', error=e))
            import traceback
            logger.error(traceback.format_exc())
            return [main_page_path]  # エラーが発生した場合はメインページのみ返す
            # Return only the main page if an error occurs

    def run(self, libraries):
        """
        指定されたライブラリのスクレイピングを実行する

        Args:
            libraries (list): スクレイピングするライブラリのリスト
                             各要素は {"name": "ライブラリ名", "url": "URL"} の形式

        Returns:
            dict: ライブラリごとの結果
        """
        results = {}

        for library in libraries:
            library_name = library["name"]
            library_url = library["url"]

            # ライブラリをスクレイピング
            # Scrape the library
            md_files = self.scrape_library(library_url, library_name)

            # 結果を記録
            results[library_name] = {
                "url": library_url,
                "md_files": md_files,
                "success": len(md_files) > 0
            }

        return results
