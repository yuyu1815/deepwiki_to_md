#!/usr/bin/env python3
"""
VS Code データ取得スクリプト
https://deepwiki.com/microsoft/vscode からVS Codeのドキュメントを取得します
"""

import os
import sys
import logging
from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """VS Codeデータ取得のメイン関数"""
    
    # VS Codeライブラリの設定
    vscode_library = {
        "name": "vscode",
        "url": "https://deepwiki.com/microsoft/vscode"
    }
    
    # 出力ディレクトリ
    output_dir = "VSCodeDocuments"
    
    logger.info("=== VS Code データ取得開始 ===")
    logger.info(f"対象URL: {vscode_library['url']}")
    logger.info(f"出力ディレクトリ: {output_dir}")
    
    try:
        # スクレイパーの初期化（優先度：DirectMarkdownScraper > DirectScraper > Alternative）
        logger.info("スクレイパーを初期化中...")
        scraper = DeepwikiScraper(
            output_dir=output_dir,
            use_direct_scraper=False,
            use_alternative_scraper=False
        )
        logger.info(f"使用スクレイパー戦略: DirectMarkdownScraper={scraper.use_direct_md_scraper}, "
                   f"DirectScraper={scraper.use_direct_scraper}, "
                   f"Alternative={scraper.use_alternative_scraper}")
        
        # VS Codeライブラリのスクレイピング
        logger.info("VS Codeライブラリのスクレイピングを開始...")
        scraper.scrape_library(vscode_library["name"], vscode_library["url"])
        
        # 結果の確認
        output_path = os.path.join(output_dir, vscode_library["name"], "md")
        if os.path.exists(output_path):
            md_files = [f for f in os.listdir(output_path) if f.endswith('.md')]
            logger.info(f"成功: {len(md_files)} 個のMarkdownファイルが生成されました")
            logger.info(f"出力場所: {os.path.abspath(output_path)}")
            
            # ファイル一覧表示
            logger.info("生成されたファイル:")
            for md_file in sorted(md_files):
                file_path = os.path.join(output_path, md_file)
                file_size = os.path.getsize(file_path)
                logger.info(f"  - {md_file} ({file_size} bytes)")
        else:
            logger.warning("出力ディレクトリが見つかりません")
            
        logger.info("=== VS Code データ取得完了 ===")
        
    except Exception as e:
        logger.error(f"VS Codeデータ取得中にエラーが発生しました: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())