"""
DeepWiki to Markdownコンバーター用のダイレクトMarkdownスクレイパー。

このスクレイパーはDeepWikiサイトから直接Markdownコンテンツを取得します。
"""

import logging
import os
import re
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import requests

from deepwiki_to_md.models.config import Config
from deepwiki_to_md.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class DirectMarkdownScraper(BaseScraper):
    """
    DeepWikiサイトから直接Markdownコンテンツを取得するためのスクレイパー。
    
    このスクレイパーは、DeepWikiサイトがHTMLの解析や変換を必要とせずに、
    Markdownコンテンツを直接提供することを前提としています。
    """

    def __init__(self, config: Config):
        """
        指定された設定でスクレイパーを初期化します。
        
        Args:
            config (Config): URL、ライブラリ名、出力ディレクトリを含む設定オブジェクト。
        """
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(config.headers)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        DeepWikiサイトからコンテンツをスクレイピングします。
        
        Returns:
            List[Dict[str, Any]]: スクレイピングされたコンテンツを含む辞書のリスト。
        """
        results = []

        # メインコンテンツを取得
        content = self._fetch_content(self.config.url)
        if not content:
            logger.error(f"Failed to fetch content from {self.config.url}")
            return results

        # メインコンテンツを保存
        filename = self._get_filename_from_url(self.config.url)
        filepath = self.save_content(filename, content)
        results.append({
            "url": self.config.url,
            "filename": filename,
            "filepath": filepath
        })

        # ナビゲーション項目を抽出して処理
        nav_items = self.extract_navigation(content)
        for item in nav_items:
            if len(results) >= self.config.max_depth:
                logger.info(f"Reached maximum depth of {self.config.max_depth}")
                break

            url = item.get("url")
            if not url:
                continue

            # 処理済みの場合はスキップ
            if any(r["url"] == url for r in results):
                continue

            # コンテンツを取得して保存
            item_content = self._fetch_content(url)
            if not item_content:
                logger.warning(f"Failed to fetch content from {url}")
                continue

            item_filename = item.get("title", self._get_filename_from_url(url))
            item_filepath = self.save_content(item_filename, item_content)
            results.append({
                "url": url,
                "filename": item_filename,
                "filepath": item_filepath
            })

            # リクエスト間の遅延を考慮
            time.sleep(self.config.delay)

        return results

    def extract_navigation(self, content: str) -> List[Dict[str, Any]]:
        """
        コンテンツからナビゲーションを抽出します。
        
        Args:
            content (str): ナビゲーションを抽出するコンテンツ。
            
        Returns:
            List[Dict[str, Any]]: ナビゲーション項目を含む辞書のリスト。
        """
        nav_items = []

        # Markdownコンテンツからリンクを抽出
        # これはMarkdownからリンクを抽出する単純な実装です
        # より堅牢な実装ではMarkdownパーサーを使用します
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            title = match.group(1)
            url = match.group(2)

            # DeepWiki以外のリンクはスキップ
            if "deepwiki.com" not in url and not url.startswith("/"):
                continue

            # 相対URLを絶対URLに変換
            if url.startswith("/"):
                url = urljoin(self.config.url, url)

            nav_items.append({
                "title": title,
                "url": url
            })

        return nav_items

    def _fetch_content(self, url: str) -> Optional[str]:
        """
        指定されたURLからコンテンツを取得します。
        
        Args:
            url (str): コンテンツを取得するURL。
            
        Returns:
            Optional[str]: 取得したコンテンツ。リクエストが失敗した場合はNone。
        """
        retries = 0
        while retries <= self.config.retry_limit:
            try:
                if self.config.verbose:
                    logger.info(f"Fetching content from {url}")

                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()

                return response.text
            except requests.RequestException as e:
                retries += 1
                if retries > self.config.retry_limit:
                    logger.error(f"Failed to fetch content from {url}: {e}")
                    return None

                logger.warning(f"Retry {retries}/{self.config.retry_limit} for {url}: {e}")
                time.sleep(self.config.delay * (2 ** (retries - 1)))  # 指数関数的バックオフ

        return None

    def _get_filename_from_url(self, url: str) -> str:
        """
        指定されたURLからファイル名を取得します。
        
        Args:
            url (str): ファイル名を取得するURL。
            
        Returns:
            str: URLから派生したファイル名。
        """
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if not path:
            return "index"

        # パスの最後の部分をファイル名として使用
        filename = path.split("/")[-1]

        # ファイル拡張子が存在する場合は削除
        filename = os.path.splitext(filename)[0]

        return filename
