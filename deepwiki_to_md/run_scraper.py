"""
DeepWikiからMarkdownへのコンバーターのコマンドラインツール。
"""

import logging
import sys

import argparse

from deepwiki_to_md import DeepwikiScraper
from deepwiki_to_md.models.config import Config

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数を解析します。
    
    Returns:
        argparse.Namespace: 解析された引数。
    """
    parser = argparse.ArgumentParser(
        description="DeepWikiサイトからコンテンツをスクレイピングし、Markdown形式に変換します。"
    )

    parser.add_argument(
        "url",
        help="スクレイピングするDeepWikiサイトのURL。"
    )

    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="出力ファイルを保存するディレクトリ。デフォルト：output"
    )

    parser.add_argument(
        "-n", "--library-name",
        help="作成するライブラリの名前。デフォルト：URLから派生"
    )

    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        default=1,
        help="クロールする最大深度。デフォルト：1"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細な出力を表示します。"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="HTTPリクエストのタイムアウト（秒）。デフォルト：30"
    )

    parser.add_argument(
        "-r", "--retry-limit",
        type=int,
        default=3,
        help="失敗したリクエストの最大再試行回数。デフォルト：3"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="リクエスト間の遅延（秒）。デフォルト：0.5"
    )

    return parser.parse_args()


def main() -> int:
    """
    コマンドラインツールのメイン関数。
    
    Returns:
        int: 終了コード。
    """
    args = parse_args()

    # ライブラリ名が指定されていない場合はURLから派生させる
    if not args.library_name:
        from urllib.parse import urlparse
        parsed = urlparse(args.url)
        path = parsed.path.strip("/")
        if path:
            args.library_name = path.split("/")[-1]
        else:
            args.library_name = parsed.netloc.split(".")[0]

    # 設定を作成
    config = Config(
        url=args.url,
        library_name=args.library_name,
        output_dir=args.output_dir,
        max_depth=args.max_depth,
        verbose=args.verbose,
        timeout=args.timeout,
        retry_limit=args.retry_limit,
        delay=args.delay
    )

    # スクレイパーを作成
    scraper = DeepwikiScraper(config)
    
    try:
        # コンテンツをスクレイピング
        logger.info(f"{args.url}からコンテンツをスクレイピングしています")
        results = scraper.scrape()

        # 結果を出力
        if results:
            logger.info(f"{len(results)}ページのスクレイピングに成功しました。")
            for result in results:
                logger.info(f"  - {result['url']} -> {result['filepath']}")
        else:
            logger.error("コンテンツのスクレイピングに失敗しました。")
            return 1
            
        return 0
    except Exception as e:
        logger.exception(f"コンテンツのスクレイピング中にエラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())