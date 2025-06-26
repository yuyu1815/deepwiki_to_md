"""
"""
DeepWikiコンテンツからリポジトリ構造を作成するためのコマンドラインツール。
"""

import os
import sys
import logging
import argparse
import yaml
from typing import Dict, Any, List, Optional
import re

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
        description="DeepWikiコンテンツからリポジトリ構造を作成します。"
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
        "--create-yaml",
        action="store_true",
        help="MarkdownコンテンツからYAMLファイルを作成します。"
    )
    
    parser.add_argument(
        "--fix-links",
        action="store_true",
        help="Markdownコンテンツ内のリンクを修正します。"
    )
    
    return parser.parse_args()

def create_yaml_from_md(md_file: str) -> Optional[str]:
    """
MarkdownファイルからYAMLファイルを作成します。

Args:
md_file(str): Markdownファイルへのパス。

Returns:
Optional[str]: 作成されたYAMLファイルへのパス。作成に失敗した場合はNone。
"""
try:
    # Markdownファイルを読み込む
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # タイトルを抽出（最初の見出し）
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(md_file).replace(".md", "")
    
    # YAMLコンテンツを作成
    yaml_content = {
        "title": title,
        "content": content
    }
    
    # YAMLファイルを書き込む
    yaml_file = md_file.replace(".md", ".yaml")
    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
        
    logger.info(f"YAMLファイルを作成しました: {yaml_file}")
    return yaml_file
except Exception as e:
    logger.error(f"{md_file}からYAMLファイルの作成中にエラーが発生しました: {e}")
    return None

def fix_markdown_links(md_file: str) -> bool:
"""
Markdownファイル内のリンクを修正します。

Args:
md_file(str): Markdownファイルへのパス。

Returns:
bool: リンクが修正された場合はTrue、それ以外の場合はFalse。
"""
try:
    # Markdownファイルを読み込む
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # リンクを修正
    # 1. deepwiki.comのリンクを相対リンクに置換
    content = re.sub(
        r'\[([^\]]+)\]\(https?:\/\/deepwiki\.com\/([^)]+)\)',
        r'[\1](\2.md)',
        content
    )
    
    # 2. 相対リンクに.md拡張子を追加
    content = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'[{m.group(1)}]({m.group(2)}.md)' if not m.group(2).endswith(('.md', '.html', '.pdf', 'http://', 'https://')) else m.group(0),
        content
    )
    
    # 更新されたコンテンツを書き込む
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    logger.info(f"{md_file}のリンクを修正しました")
    return True
except Exception as e:
    logger.error(f"{md_file}のリンク修正中にエラーが発生しました: {e}")
    return False

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
        verbose=args.verbose
    )
    
    # スクレイパーを作成
    scraper = DeepwikiScraper(config)
    
    try:
        # コンテンツをスクレイピング
        logger.info(f"{args.url}からコンテンツをスクレイピングしています")
        results = scraper.scrape()
        
        if not results:
            logger.error("コンテンツのスクレイピングに失敗しました。")
            return 1
            
        logger.info(f"{len(results)}ページのスクレイピングに成功しました。")
        
        # 結果を処理
        for result in results:
            filepath = result["filepath"]
            
            # 要求に応じてリンクを修正
            if args.fix_links:
                fix_markdown_links(filepath)
                
            # 要求に応じてYAMLファイルを作成
            if args.create_yaml:
                create_yaml_from_md(filepath)
                
        return 0
    except Exception as e:
        logger.exception(f"リポジトリ作成中にエラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
