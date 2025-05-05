import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from .localization import get_message

# Import fix_markdown_links function
try:
    from deepwiki_to_md.fix_markdown_links import fix_markdown_links
except ImportError:
    # If the module import fails, try relative import
    try:
        from .fix_markdown_links import fix_markdown_links
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.error("Could not import fix_markdown_links module")


        def fix_markdown_links(directory):
            logger = logging.getLogger(__name__)
            logger.error("fix_markdown_links module not available")
            return

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_deepwiki(url):
    """
    指定されたURLからdeepwikiコンテンツをスクレイピングする関数
    # Function to scrape deepwiki content from the specified URL

    Args:
        url: スクレイピングするdeepwikiのURL（例：https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization）
        # url: The URL of the deepwiki page to scrape (e.g., https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization)

    Returns:
        requests.Response: レスポンスオブジェクト
        # requests.Response: The response object
    """
    # URLからドメインとパスを抽出
    # Extract domain and path from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # セッションの作成
    # Create a session
    session = requests.Session()
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

    # ヘッダーの設定（動的に生成）
    # Set headers (dynamically generated)
    headers = {
        "authority": domain,
        "method": "GET",
        "path": f"/?_rsc=13l95",
        "scheme": parsed_url.scheme,
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "next-router-prefetch": "1",
        "pragma": "no-cache",
        "priority": "i",
        "referer": f"{parsed_url.scheme}://{domain}/{referer_path}",
        "rsc": "1",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    logger.info(f"リクエスト実行: {full_url}")
    # Execute request

    # リクエストの実行
    # Execute the request
    try:
        response = session.get(full_url, headers=headers, timeout=10)
        logger.info(f"レスポンスステータス: {response.status_code}")
        # Response status
        return response
    except Exception as e:
        logger.error(f"リクエスト中にエラーが発生: {e}")
        # Error occurred during request
        raise


class DirectMarkdownScraper:
    def __init__(self, output_dir="DirectMarkdownDocuments"):
        """
        Initialize the DirectMarkdownScraper.

        Args:
            output_dir (str): The base directory to save the Markdown files.
        """
        self.output_dir = output_dir
        # Dictionary to store the content hash of saved files to avoid duplicates
        # 保存されたファイルのコンテンツハッシュを保存して重複を避けるための辞書
        self.saved_content_hash = None

    def save_markdown(self, content, library_name, page_path):
        """
        Markdownコンテンツをファイルに保存する
        見出し(##)ごとに別々のファイルに分割して保存する
        Save Markdown content to a file
        Split and save into separate files for each heading (##)
        Args:
            content (str): 保存するMarkdownコンテンツ
            library_name (str): ライブラリ名
            page_path (str): ページのパス
            # library_name (str): Library name
            # content (str): Markdown content to save
            # page_path (str): Page path

        Returns:
            list: 保存したファイルのパスのリスト
            # list: List of saved file paths
        """
        # ライブラリ名が指定されている場合はそれを使用し、そうでない場合はURLパスから取得
        # Use the specified library name if provided, otherwise get it from the URL path
        if library_name:
            dir_path_part = library_name
        else:
            # URLパスから適切な部分を取得
            # Get the appropriate part from the URL path
            path_parts = page_path.strip('/').split('/')

            # URLが複数のパス部分を持つ場合（例：python/cpython/1-overview）
            # If the URL has multiple path parts (e.g., python/cpython/1-overview)
            if len(path_parts) > 2:
                # 2番目に最後の部分を使用（例：cpython）
                # Use the second to last part (e.g., cpython)
                dir_path_part = path_parts[-2]
            else:
                # それ以外の場合は最後の部分を使用
                # Otherwise, use the last part
                dir_path_part = path_parts[-1] if path_parts else 'index'

        # ファイル名用に最後の部分を保持
        # Keep the last part for the filename
        last_path_part = path_parts[-1] if path_parts else 'index'

        # ライブラリディレクトリを作成
        # Create the library directory
        library_dir = os.path.join(self.output_dir, dir_path_part)
        os.makedirs(library_dir, exist_ok=True)

        # 分割ファイル用のmdディレクトリを作成
        # Create the md directory for split files
        output_path = os.path.join(library_dir, 'md')
        os.makedirs(output_path, exist_ok=True)

        # ファイル名を作成
        # Create the filename
        filename = last_path_part if page_path else 'index'
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # 無効な文字を置換 Replace invalid characters

        # JavaScriptを削除する機能は削除されました
        # Feature to remove JavaScript has been removed
        cleaned_content = content

        # ファイル末尾の独自データを削除する
        # Remove proprietary data at the end of the file
        # 独自データは通常、特定のパターンで始まる行から始まる
        # Proprietary data usually starts from lines beginning with a specific pattern
        # 例: "- Continued improvements..." や JSON-like データ
        # Example: "- Continued improvements..." or JSON-like data
        end_data_patterns = [
            r'^-\s+Continued improvements',  # 例: "- Continued improvements to developer experience..." Example
            r'^c:null$',  # 例: "c:null" Example
            r'^\d+:\[\["',  # 例: "10:[[\"$\",\"title\",\"0\",{\"children\":..." Example
        ]

        for pattern in end_data_patterns:
            match = re.search(pattern, cleaned_content, re.MULTILINE)
            if match:
                # マッチした行の前までの内容だけを保持
                # Keep only the content before the matched line
                end_pos = match.start()
                original_length = len(cleaned_content)
                cleaned_content = cleaned_content[:end_pos].rstrip()
                logger.info(f"ファイル末尾の独自データを削除しました: {original_length - len(cleaned_content)} バイト")
                # Removed proprietary data from the end of the file: {original_length - len(cleaned_content)} bytes

        # 最初の28行を削除
        # Delete the first 28 lines
        if cleaned_content:
            lines = cleaned_content.split('\n')
            if len(lines) > 28:
                cleaned_content = '\n'.join(lines[28:])
                logger.info(f"最初の28行を削除しました: {filename}.md")
                # Deleted the first 28 lines: {filename}.md

        # コンテンツのハッシュを計算
        # Calculate the content hash
        import hashlib
        content_hash = hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()

        # 既に同じ内容のファイルが保存されているか確認
        # Check if a file with the same content has already been saved
        if self.saved_content_hash is not None and self.saved_content_hash == content_hash:
            logger.info(
                f"同じ内容のファイルが既に保存されているため保存をスキップしますが処理は続行します: {filename}.md")
            # Skipping saving as a file with the same content has already been saved, but continuing processing: {filename}.md
            # 空のファイルリストを返す代わりに、ダミーのファイルパスを返して処理を続行
            # Instead of returning an empty list, return a dummy file path to continue processing
            dummy_path = os.path.join(output_path, f"{filename}.md")
            return [dummy_path]

        # ハッシュを更新
        # Update the hash
        self.saved_content_hash = content_hash

        # 見出し(##)でコンテンツを分割
        # Split content by headings (##)
        sections = re.split(r'(^##\s+.*)', cleaned_content, flags=re.MULTILINE)
        saved_files = []

        # 最初のセクション（見出しがない場合）
        # First section (if no heading)
        first_section = sections[0].strip()
        if first_section:
            # 最初のセクションのファイル名
            # Filename for the first section
            first_section_filename = f"{filename}_intro.md"
            first_section_path = os.path.join(output_path, first_section_filename)
            with open(first_section_path, 'w', encoding='utf-8') as f:
                f.write(first_section)
            logger.info(f"保存しました: {first_section_path}")
            # Saved: {first_section_path}
            saved_files.append(first_section_path)

        # 見出しごとのセクションを処理
        # Process sections for each heading
        for i in range(1, len(sections), 2):
            heading = sections[i].strip()
            section_content = sections[i + 1].strip()

            # 見出しからファイル名を生成
            # Generate filename from heading
            # Remove '## ' prefix and sanitize
            # '## ' プレフィックスを削除してサニタイズ
            section_title = heading[3:].strip()
            section_filename = re.sub(r'[<>:"/\\|?*]', '_', section_title)
            section_filename = re.sub(r'\s+', '_', section_filename)
            section_filename = f"{filename}_{section_filename}.md"

            section_path = os.path.join(output_path, section_filename)
            with open(section_path, 'w', encoding='utf-8') as f:
                f.write(f"{heading}\n\n{section_content}")
            logger.info(f"保存しました: {section_path}")
            # Saved: {section_path}
            saved_files.append(section_path)

        return saved_files

    def _split_by_headings(self, content):
        """
        Markdownコンテンツを見出し(##)ごとに分割する

        Args:
            content (str): 分割するMarkdownコンテンツ

        Returns:
            list: (見出し, コンテンツ)のタプルのリスト
        """
        if not content:
            return []

        # 見出し(##)を検索するための正規表現
        heading_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)

        # 見出しの位置を取得
        headings = list(heading_pattern.finditer(content))

        if not headings:
            # 見出しがない場合は空のリストを返す
            # Return an empty list if there are no headings
            return []

        sections = []

        # 最初の見出しの前のコンテンツを取得
        # Get the content before the first heading
        if headings[0].start() > 0:
            intro_content = content[:headings[0].start()].strip()
            if intro_content:
                sections.append((None, intro_content))

        # 各見出しごとにセクションを作成
        # Create sections for each heading
        for i, match in enumerate(headings):
            heading_text = match.group(1)
            start_pos = match.start()

            # 次の見出しがある場合はその位置まで、ない場合は最後まで
            # Up to the position of the next heading if it exists, otherwise to the end
            if i < len(headings) - 1:
                end_pos = headings[i + 1].start()
            else:
                end_pos = len(content)

            # セクションのコンテンツを取得
            # Get the content of the section
            section_content = content[start_pos:end_pos].strip()
            sections.append((heading_text, section_content))

        return sections

    def scrape_page(self, url, library_name):
        """
        指定されたURLのページをスクレイピングし、Markdownとして保存する

        Args:
            url (str): スクレイピングするURL
            library_name (str): ライブラリ名

        Returns:
            list: 保存したMarkdownファイルのパスのリスト、失敗した場合は空のリスト
        """
        try:
            # URLをログに出力
            # Log the URL
            logger.info(f"scrape_page: URL = {url}")

            # URLの各部分を解析
            # Parse each part of the URL
            parsed_url = urlparse(url)

            # 正しいURLを構築
            # Construct the correct URL
            correct_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            # ページをスクレイピング
            # Scrape the page
            response = scrape_deepwiki(correct_url)
            if response.status_code != 200:
                logger.error(f"ページの取得に失敗しました: {url} (ステータスコード: {response.status_code})")
                # Failed to get the page
                return []

            # URLからページパスを抽出
            # Extract the page path from the URL
            page_path = parsed_url.path

            # レスポンスの内容をMarkdownとして保存
            # Save the response content as Markdown
            # このスクレイピング方法では、レスポンスの内容が直接Markdownとして使用可能
            # In this scraping method, the response content can be used directly as Markdown
            return self.save_markdown(response.text, library_name, page_path)

        except Exception as e:
            logger.error(f"ページのスクレイピングに失敗しました: {url} ({e})")
            # Failed to scrape the page
            import traceback
            logger.error(traceback.format_exc())
            return []

    def extract_navigation_items(self, response_text, current_url):
        """
        Extract navigation items from the specified ul element.

        Args:
            response_text (str): The response text from the page.
            current_url (str): The URL of the current page, used as base for relative URLs.

        Returns:
            list: A list of dictionaries containing the title and URL of each navigation item.
        """
        if not response_text:
            return []

        soup = BeautifulSoup(response_text, 'html.parser')
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

    def scrape_library(self, library_url, library_name):
        """
        指定されたライブラリのページをスクレイピングする

        Args:
            library_url (str): ライブラリのURL
            library_name (str): ライブラリ名

        Returns:
            list: 保存したMarkdownファイルのパスのリスト
        """
        logger.info(get_message('starting_library_scrape', name=library_name, url=library_url))
        # Start scraping the library

        # ライブラリ名が指定されている場合はそれを使用し、そうでない場合はURLパスから取得
        # Use the specified library name if provided, otherwise get it from the URL path
        if library_name:
            dir_path_part = library_name
        else:
            # URLから適切なパス部分を抽出
            # Extract the appropriate path part from the URL
            parsed_url = urlparse(library_url)
            path_parts = parsed_url.path.strip('/').split('/')

            # URLが複数のパス部分を持つ場合（例：python/cpython/1-overview）
            # If the URL has multiple path parts (e.g., python/cpython/1-overview)
            if len(path_parts) > 2:
                # 2番目に最後の部分を使用（例：cpython）
                # Use the second to last part (e.g., cpython)
                dir_path_part = path_parts[-2]
            else:
                # それ以外の場合は最後の部分を使用
                # Otherwise, use the last part
                dir_path_part = path_parts[-1] if path_parts else 'index'

        # メインページをスクレイピング
        # Scrape the main page
        main_page_paths = self.scrape_page(library_url, library_name)
        if not main_page_paths:
            logger.error(get_message('main_page_scrape_failed', url=library_url))
            # Failed to scrape the main page
            return []

        # HTMLコンテンツを取得してナビゲーション項目を抽出
        # Get HTML content and extract navigation items
        try:
            # 通常のHTTPリクエストを使用してHTMLを取得
            # Get HTML using a normal HTTP request
            response = requests.get(library_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            })
            if response.status_code != 200:
                logger.error(get_message('html_fetch_failed', url=library_url, status_code=response.status_code))
                # Failed to get HTML
                return main_page_paths  # メインページのみ返す

            # ナビゲーション項目を抽出
            # Extract navigation items
            nav_items = self.extract_navigation_items(response.text, library_url)

            if not nav_items:
                logger.warning(get_message('no_nav_items', url=library_url))
                # Navigation items not found
                # メインページのみの場合でもMarkdownリンクを修正
                # Fix markdown links even if only the main page exists
                md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
                logger.info(get_message('starting_fix', directory=md_directory))
                fix_markdown_links(md_directory)
                return main_page_paths  # メインページのみ返す

            # 保存したファイルのパスのリスト
            # List of paths to saved files
            md_files = list(main_page_paths)  # リストをコピー

            # 各ナビゲーション項目をスクレイピング
            # Scrape each navigation item
            for item in nav_items:
                title = item['title']
                url = item['url']

                logger.info(get_message('scraping_nav_item', title=title, url=url))
                # Scraping navigation item

                # 小さな遅延を入れてサーバーに負荷をかけないようにする
                import time
                time.sleep(1)

                # ページをスクレイピング
                # Scrape the page
                page_paths = self.scrape_page(url, library_name)
                if page_paths:
                    md_files.extend(page_paths)
                else:
                    logger.error(get_message('nav_item_scrape_failed', title=title, url=url))

            # スクレイピング完了後、Markdownリンクを修正
            md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
            logger.info(get_message('starting_fix', directory=md_directory))
            fix_markdown_links(md_directory)

            return md_files
        except Exception as e:
            logger.error(get_message('nav_extraction_error', error=e))
            import traceback
            logger.error(traceback.format_exc())
            # エラーが発生した場合でもMarkdownリンクを修正
            md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
            logger.info(get_message('starting_fix', directory=md_directory))
            fix_markdown_links(md_directory)
            return main_page_paths  # エラーが発生した場合はメインページのみ返す

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


def main():
    # スクレイピング対象のURLリスト
    # List of URLs to scrape
    urls_to_scrape = [
        "https://deepwiki.com/python/cpython/1-overview",
        "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
        # 他のURLもここに追加 Add other URLs here
    ]

    # 出力ディレクトリ
    # Output directory
    output_directory = "DirectMarkdownDocuments"

    # スクレイパーのインスタンスを作成
    # Create scraper instance
    scraper = DirectMarkdownScraper(output_dir=output_directory)

    # 各URLをスクレイピングして保存
    # Scrape and save each URL
    all_saved_files = []
    for url in urls_to_scrape:
        logger.info(f"スクレイピング開始: {url}")
        # Start scraping: {url}
        # URLからライブラリ名を推測（例：'cpython'）
        # Infer library name from URL (e.g., 'cpython')
        path_parts = urlparse(url).path.strip('/').split('/')
        lib_name = path_parts[1] if len(path_parts) > 1 else None

        saved = scraper.scrape_and_save(url, library_name=lib_name)
        all_saved_files.extend(saved)

    logger.info(f"処理完了。合計 {len(all_saved_files)} ファイルを保存しました。")
    # Processing complete. Saved a total of {len(all_saved_files)} files.


if __name__ == "__main__":
    main()
