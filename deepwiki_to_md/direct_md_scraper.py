import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

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


        # Define a dummy function that does nothing if import fails
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

    Args:
        url: スクレイピングするdeepwikiのURL（例：https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization）

    Returns:
        requests.Response: レスポンスオブジェクト
    """
    # URLからドメインとパスを抽出
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # セッションの作成
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    })

    # URLを解析してリファラーを作成（URLの一部を使用）
    path_parts = path.strip('/').split('/')
    referer_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else path

    # クエリパラメータを保持
    query = parsed_url.query
    full_url = f"{parsed_url.scheme}://{domain}{path}"
    if query:
        full_url += f"?{query}"

    # ヘッダーの設定（動的に生成）
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

    # リクエストの実行
    try:
        response = session.get(full_url, headers=headers, timeout=10)
        logger.info(f"レスポンスステータス: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"リクエスト中にエラーが発生: {e}")
        raise


class DirectMarkdownScraper:
    def __init__(self, output_dir="DirectMarkdownDocuments"):
        """
        Initialize the DirectMarkdownScraper.

        Args:
            output_dir (str): The base directory to save the Markdown files.
        """
        self.output_dir = output_dir

    def save_markdown(self, content, library_name, page_path):
        """
        Markdownコンテンツをファイルに保存する

        Args:
            content (str): 保存するMarkdownコンテンツ
            library_name (str): ライブラリ名
            page_path (str): ページのパス

        Returns:
            str: 保存したファイルのパス
        """
        # URLパスから適切な部分を取得
        path_parts = page_path.strip('/').split('/')

        # URLが複数のパス部分を持つ場合（例：python/cpython/1-overview）
        if len(path_parts) > 2:
            # 2番目に最後の部分を使用（例：cpython）
            dir_path_part = path_parts[-2]
        else:
            # それ以外の場合は最後の部分を使用
            dir_path_part = path_parts[-1] if path_parts else 'index'

        # ファイル名用に最後の部分を保持
        last_path_part = path_parts[-1] if path_parts else 'index'

        # 出力ディレクトリを作成
        output_path = os.path.join(self.output_dir, dir_path_part, 'md')
        os.makedirs(output_path, exist_ok=True)

        # ファイル名を作成
        filename = last_path_part if page_path else 'index'
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # 無効な文字を置換

        # JavaScriptを削除する
        # Markdownの実際のコンテンツは通常、"# "で始まる見出しから始まる
        cleaned_content = content

        # より確実にJavaScriptを削除するために、複数のパターンを試す
        # 1. 最初の"# "で始まる行を探す（最も一般的なMarkdownの見出し）
        markdown_start = re.search(r'^#\s+', content, re.MULTILINE)

        if markdown_start:
            # 見出しの開始位置から後ろの部分だけを保持
            start_pos = markdown_start.start()
            cleaned_content = content[start_pos:]
            logger.info(f"JavaScriptを削除しました: {len(content) - len(cleaned_content)} バイト")
        else:
            # 2. 見出しが見つからない場合、T47ac,# のようなパターンを探す（特定のフォーマット）
            alt_pattern = re.search(r'T[0-9a-f]+,#\s+', content)
            if alt_pattern:
                start_pos = alt_pattern.start()
                # "T47ac," などのプレフィックスをスキップして、"#" から始まるようにする
                hash_pos = content.find('#', start_pos)
                if hash_pos != -1:
                    cleaned_content = content[hash_pos:]
                    logger.info(
                        f"代替パターンを使用してJavaScriptを削除しました: {len(content) - len(cleaned_content)} バイト")
                else:
                    logger.warning(f"'#'記号が見つかりませんでした。JavaScriptを削除できない可能性があります。")
            else:
                logger.warning(f"Markdownの見出しが見つかりませんでした。JavaScriptを削除できない可能性があります。")

        # ファイル末尾の独自データを削除する
        # 独自データは通常、特定のパターンで始まる行から始まる
        # 例: "- Continued improvements..." や JSON-like データ
        end_data_patterns = [
            r'^-\s+Continued improvements',  # 例: "- Continued improvements to developer experience..."
            r'^c:null$',  # 例: "c:null"
            r'^\d+:\[\["',  # 例: "10:[[\"$\",\"title\",\"0\",{\"children\":..."
        ]

        for pattern in end_data_patterns:
            match = re.search(pattern, cleaned_content, re.MULTILINE)
            if match:
                # マッチした行の前までの内容だけを保持
                end_pos = match.start()
                original_length = len(cleaned_content)
                cleaned_content = cleaned_content[:end_pos].rstrip()
                logger.info(f"ファイル末尾の独自データを削除しました: {original_length - len(cleaned_content)} バイト")

        # Markdownファイルを保存
        md_file_path = os.path.join(output_path, f"{filename}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        return md_file_path

    def scrape_page(self, url, library_name):
        """
        指定されたURLのページをスクレイピングし、Markdownとして保存する

        Args:
            url (str): スクレイピングするURL
            library_name (str): ライブラリ名

        Returns:
            str: 保存したMarkdownファイルのパス、失敗した場合はNone
        """
        try:
            # URLをログに出力
            logger.info(f"scrape_page: URL = {url}")

            # URLの各部分を解析
            parsed_url = urlparse(url)

            # 正しいURLを構築
            correct_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            # ページをスクレイピング
            response = scrape_deepwiki(correct_url)
            if response.status_code != 200:
                logger.error(f"ページの取得に失敗しました: {url} (ステータスコード: {response.status_code})")
                return None

            # URLからページパスを抽出
            page_path = parsed_url.path

            # レスポンスの内容をMarkdownとして保存
            # このスクレイピング方法では、レスポンスの内容が直接Markdownとして使用可能
            return self.save_markdown(response.text, library_name, page_path)

        except Exception as e:
            logger.error(f"ページのスクレイピングに失敗しました: {url} ({e})")
            import traceback
            logger.error(traceback.format_exc())
            return None

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

        logger.info(f"抽出されたナビゲーション項目数: {len(nav_items)}")
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
        logger.info(f"ライブラリのスクレイピングを開始: {library_name} ({library_url})")

        # URLから適切なパス部分を抽出
        parsed_url = urlparse(library_url)
        path_parts = parsed_url.path.strip('/').split('/')

        # URLが複数のパス部分を持つ場合（例：python/cpython/1-overview）
        if len(path_parts) > 2:
            # 2番目に最後の部分を使用（例：cpython）
            dir_path_part = path_parts[-2]
        else:
            # それ以外の場合は最後の部分を使用
            dir_path_part = path_parts[-1] if path_parts else library_name

        # メインページをスクレイピング
        main_page_path = self.scrape_page(library_url, library_name)
        if not main_page_path:
            logger.error(f"メインページのスクレイピングに失敗しました: {library_url}")
            return []

        # HTMLコンテンツを取得してナビゲーション項目を抽出
        try:
            # 通常のHTTPリクエストを使用してHTMLを取得
            response = requests.get(library_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            })
            if response.status_code != 200:
                logger.error(f"HTMLの取得に失敗しました: {library_url} (ステータスコード: {response.status_code})")
                return [main_page_path]  # メインページのみ返す

            # ナビゲーション項目を抽出
            nav_items = self.extract_navigation_items(response.text, library_url)

            if not nav_items:
                logger.warning(f"ナビゲーション項目が見つかりませんでした: {library_url}")
                # メインページのみの場合でもMarkdownリンクを修正
                md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
                logger.info(f"Fixing markdown links in {md_directory}")
                fix_markdown_links(md_directory)
                return [main_page_path]  # メインページのみ返す

            # 保存したファイルのパスのリスト
            md_files = [main_page_path]

            # 各ナビゲーション項目をスクレイピング
            for item in nav_items:
                title = item['title']
                url = item['url']

                logger.info(f"ナビゲーション項目をスクレイピング: {title} ({url})")

                # 小さな遅延を入れてサーバーに負荷をかけないようにする
                import time
                time.sleep(1)

                # ページをスクレイピング
                page_path = self.scrape_page(url, library_name)
                if page_path:
                    md_files.append(page_path)
                else:
                    logger.error(f"ナビゲーション項目のスクレイピングに失敗しました: {title} ({url})")

            # スクレイピング完了後、Markdownリンクを修正
            md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
            logger.info(f"Fixing markdown links in {md_directory}")
            fix_markdown_links(md_directory)

            return md_files
        except Exception as e:
            logger.error(f"ナビゲーション項目の抽出中にエラーが発生しました: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # エラーが発生した場合でもMarkdownリンクを修正
            md_directory = os.path.join(os.getcwd(), self.output_dir, dir_path_part, "md")
            logger.info(f"Fixing markdown links in {md_directory}")
            fix_markdown_links(md_directory)
            return [main_page_path]  # エラーが発生した場合はメインページのみ返す

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
            md_files = self.scrape_library(library_url, library_name)

            # 結果を記録
            results[library_name] = {
                "url": library_url,
                "md_files": md_files,
                "success": len(md_files) > 0
            }

        return results
