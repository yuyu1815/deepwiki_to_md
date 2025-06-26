"""
DeepWikiからMarkdownへのコンバーターのベーススクレイパー。
"""

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from deepwiki_to_md.models.config import Config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    すべてのスクレイパーのベースクラス。
    
    このクラスは、すべてのスクレイパーに共通のインターフェースと機能を定義します。
    サブクラスは、scrapeメソッドとextract_navigationメソッドを実装する必要があります。
    """

    def __init__(self, config: Config):
        """
        指定された設定でスクレイパーを初期化します。
        
        Args:
            config (Config): URL、ライブラリ名、出力ディレクトリを含む設定オブジェクト。
        """
        self.config = config
        self.library_dir = os.path.join(config.output_dir, config.library_name)
        os.makedirs(self.library_dir, exist_ok=True)

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        DeepWikiサイトからコンテンツをスクレイピングします。
        
        Returns:
            List[Dict[str, Any]]: スクレイピングされたコンテンツを含む辞書のリスト。
        """
        pass

    @abstractmethod
    def extract_navigation(self, content: str) -> List[Dict[str, Any]]:
        """
        コンテンツからナビゲーションを抽出します。
        
        Args:
            content (str): ナビゲーションを抽出するコンテンツ。
            
        Returns:
            List[Dict[str, Any]]: ナビゲーション項目を含む辞書のリスト。
        """
        pass

    def _clean_content(self, content: str) -> str:
        """
        不要なパターンを削除してコンテンツをクリーンアップします。
        
        Args:
            content (str): クリーンアップするコンテンツ。
            
        Returns:
            str: クリーンアップされたコンテンツ。
        """
        # "- Continued improvements"パターンを削除
        if "- Continued improvements" in content:
            content = content.split("- Continued improvements")[0].rstrip()

        # "c:null"パターンを削除
        if "c:null" in content:
            content = content.split("c:null")[0].rstrip()

        # 数字の後に ":[[" が続くパターンを削除
        match = re.search(r'\d+:"|\[\[', content)
        if match:
            content = content[:match.start()].rstrip()

        return content

    def save_content(self, filename: str, content: str) -> str:
        """
        コンテンツをファイルに保存します。
        
        Args:
            filename (str): 保存するファイルの名前。
            content (str): 保存するコンテンツ。
            
        Returns:
            str: 保存されたファイルへのパス。
        """
        # コンテンツをクリーンアップ
        content = self._clean_content(content)

        # ファイル名が有効であることを確認
        filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        if not filename.endswith(".md"):
            filename += ".md"

        # コンテンツを保存
        filepath = os.path.join(self.library_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        if self.config.verbose:
            logger.info(f"Saved content to {filepath}")

        return filepath
