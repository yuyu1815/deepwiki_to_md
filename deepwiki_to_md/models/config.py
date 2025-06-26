"""
DeepWiki to Markdownコンバーターの設定モデル。
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """
    DeepWikiスクレイパーの設定。
    
    Attributes:
        url (str): スクレイピング対象のDeepWikiサイトのURL。
        library_name (str): 作成するライブラリの名前。
        output_dir (str): 出力ファイルを保存するディレクトリ。
        max_depth (int): クロールする最大深度（デフォルト：1）。
        verbose (bool): 詳細な出力を表示するかどうか（デフォルト：False）。
        headers (Dict[str, str]): リクエストに使用するHTTPヘッダー。
        timeout (int): HTTPリクエストのタイムアウト（秒）（デフォルト：30）。
        retry_limit (int): 失敗したリクエストの最大再試行回数（デフォルト：3）。
        delay (float): リクエスト間の遅延（秒）（デフォルト：0.5）。
    """
    url: str
    library_name: str
    output_dir: str = "output"
    max_depth: int = 1
    verbose: bool = False
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    timeout: int = 30
    retry_limit: int = 3
    delay: float = 0.5

    def __post_init__(self):
        """初期化後に設定を検証・処理します。"""
        # URLが有効であることを確認
        if not self.url.startswith(("http://", "https://")):
            self.url = f"https://{self.url}"

        # URLがDeepWikiのURLであることを確認
        if "deepwiki.com" not in self.url:
            logger.warning(f"URL {self.url} is not a DeepWiki URL. This may cause issues.")

        # 出力ディレクトリが存在することを確認
        os.makedirs(self.output_dir, exist_ok=True)

        # ライブラリディレクトリが存在することを確認
        library_dir = os.path.join(self.output_dir, self.library_name)
        os.makedirs(library_dir, exist_ok=True)

        # ライブラリ名を正規化
        self.library_name = self.library_name.replace(" ", "_").lower()
