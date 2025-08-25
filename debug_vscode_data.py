#!/usr/bin/env python3
"""
VS Code データ取得デバッグスクリプト
https://deepwiki.com/microsoft/vscode からVS Codeのドキュメントを取得し、詳細なデバッグ情報を出力します
"""

import os
import sys
import logging
import requests
from deepwiki_to_md.direct_md_scraper import scrape_deepwiki

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def debug_vscode_request():
    """VS Codeページへの直接リクエストをデバッグ"""
    url = "https://deepwiki.com/microsoft/vscode"
    
    logger.info("=== VS Code ページ直接リクエストテスト ===")
    logger.info(f"URL: {url}")
    
    try:
        # 直接HTTPリクエスト
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(url, timeout=10)
        logger.info(f"ステータスコード: {response.status_code}")
        logger.info(f"コンテンツタイプ: {response.headers.get('content-type', 'unknown')}")
        logger.info(f"コンテンツ長: {len(response.text)} バイト")
        logger.info(f"エンコーディング: {response.encoding}")
        
        # レスポンスの最初の500文字を表示
        preview = response.text[:500]
        logger.info(f"レスポンスプレビュー:\n{preview}")
        
        # HTMLであることを確認
        if response.text.strip().startswith('<'):
            logger.info("✓ HTMLコンテンツであることを確認")
        else:
            logger.warning("⚠ HTMLコンテンツではない可能性があります")
        
        return response
        
    except Exception as e:
        logger.error(f"リクエスト中にエラーが発生: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def debug_scrape_deepwiki():
    """scrape_deepwiki関数をデバッグ"""
    url = "https://deepwiki.com/microsoft/vscode"
    
    logger.info("=== scrape_deepwiki 関数テスト ===")
    
    try:
        response = scrape_deepwiki(url)
        logger.info(f"ステータスコード: {response.status_code}")
        logger.info(f"コンテンツ長: {len(response.text)} バイト")
        
        # レスポンスの最初の500文字を表示
        preview = response.text[:500]
        logger.info(f"レスポンスプレビュー:\n{preview}")
        
        # バイト数を確認
        content_bytes = response.text.encode('utf-8')
        logger.info(f"UTF-8エンコード後のバイト数: {len(content_bytes)}")
        
        return response
        
    except Exception as e:
        logger.error(f"scrape_deepwiki中にエラーが発生: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def debug_file_saving():
    """ファイル保存をデバッグ"""
    logger.info("=== ファイル保存テスト ===")
    
    # テストコンテンツ
    test_content = "# Test Content\n\nThis is a test markdown content.\n\n## Section 1\n\nTest section content."
    
    output_dir = "DebugTest"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "test.md")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        logger.info(f"テストファイルを保存: {file_path}")
        
        # ファイルを読み返して確認
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        logger.info(f"保存されたコンテンツ長: {len(saved_content)}")
        logger.info(f"コンテンツが一致: {saved_content == test_content}")
        
        return True
        
    except Exception as e:
        logger.error(f"ファイル保存中にエラーが発生: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """メイン関数"""
    
    logger.info("=== VS Code データ取得デバッグ開始 ===")
    
    # 1. 直接リクエストテスト
    direct_response = debug_vscode_request()
    
    # 2. scrape_deepwiki関数テスト
    scrape_response = debug_scrape_deepwiki()
    
    # 3. ファイル保存テスト
    file_save_ok = debug_file_saving()
    
    # 4. レスポンス比較
    if direct_response and scrape_response:
        logger.info("=== レスポンス比較 ===")
        direct_len = len(direct_response.text)
        scrape_len = len(scrape_response.text)
        
        logger.info(f"直接リクエスト長: {direct_len}")
        logger.info(f"scrape_deepwiki長: {scrape_len}")
        logger.info(f"コンテンツが一致: {direct_response.text == scrape_response.text}")
        
        if direct_response.text != scrape_response.text:
            logger.warning("コンテンツが一致しません - 詳細比較を実行")
            
            # 最初の1000文字を比較
            direct_preview = direct_response.text[:1000]
            scrape_preview = scrape_response.text[:1000]
            
            logger.info(f"直接リクエストプレビュー:\n{direct_preview}")
            logger.info(f"scrape_deepwikiプレビュー:\n{scrape_preview}")
    
    logger.info("=== デバッグ完了 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())