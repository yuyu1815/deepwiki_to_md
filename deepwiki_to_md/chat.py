"""
DeepWikiコンテンツと対話的にチャットするためのコマンドラインツール。
"""

import json
import logging
import os
import sys
import time
from typing import Dict, Any, List

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
        description="DeepWikiコンテンツとの対話的なチャット。"
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
        "-v", "--verbose",
        action="store_true",
        help="詳細な出力を表示します。"
    )

    parser.add_argument(
        "--save-chat",
        action="store_true",
        help="チャット履歴をファイルに保存します。"
    )

    return parser.parse_args()


def interactive_chat(results: List[Dict[str, Any]], save_chat: bool = False) -> None:
    """
    スクレイピングされたコンテンツとの対話的なチャットを開始します。
    
    Args:
        results (List[Dict[str, Any]]): スクレイピングされたコンテンツを含む辞書のリスト。
        save_chat (bool): チャット履歴をファイルに保存するかどうか。
    """
    print("\n=== DeepWikiチャット ===")
    print("チャットを終了するには 'exit' または 'quit' と入力してください。")
    print("コマンドのリストを表示するには 'help' と入力してください。")
    print("利用可能なドキュメントを表示するには 'list' と入力してください。")
    print("ドキュメントを読むには 'read <番号>' と入力してください。")
    print("ドキュメント内で用語を検索するには 'search <用語>' と入力してください。")
    print()

    chat_history = []

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() in ["exit", "quit"]:
                break

            chat_history.append({"user": user_input})

            if user_input.lower() == "help":
                print("\nコマンド:")
                print("  exit, quit - チャットを終了")
                print("  help - このヘルプメッセージを表示")
                print("  list - 利用可能なドキュメントを一覧表示")
                print("  read <番号> - ドキュメントを読む")
                print("  search <用語> - ドキュメント内で用語を検索")
                chat_history.append({"system": "ヘルプメッセージを表示しました。"})

            elif user_input.lower() == "list":
                print("\n利用可能なドキュメント:")
                for i, result in enumerate(results):
                    print(f"  {i + 1}. {os.path.basename(result['filepath'])}")
                chat_history.append({"system": "利用可能なドキュメントを一覧表示しました。"})

            elif user_input.lower().startswith("read "):
                try:
                    index = int(user_input.split(" ")[1]) - 1
                    if 0 <= index < len(results):
                        filepath = results[index]["filepath"]
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                        print(f"\n=== {os.path.basename(filepath)} ===")
                        print(content)
                        chat_history.append({"system": f"{os.path.basename(filepath)}のコンテンツを表示しました。"})
                    else:
                        print(f"無効なドキュメント番号です。1から{len(results)}までの数値を入力してください。")
                        chat_history.append({"system": "無効なドキュメント番号です。"})
                except (ValueError, IndexError):
                    print("無効なコマンドです。'read <番号>'と入力してください。")
                    chat_history.append({"system": "無効なコマンド形式です。"})

            elif user_input.lower().startswith("search "):
                term = user_input[7:].strip()
                if not term:
                    print("検索語を入力してください。")
                    chat_history.append({"system": "検索語が指定されていません。"})
                    continue

                print(f"\n'{term}'を検索中...")
                found = False
                for i, result in enumerate(results):
                    filepath = result["filepath"]
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    if term.lower() in content.lower():
                        print(f"  {os.path.basename(filepath)} (ドキュメント {i + 1}) で見つかりました")
                        found = True

                        # コンテキストを表示
                        lines = content.split("\n")
                        for j, line in enumerate(lines):
                            if term.lower() in line.lower():
                                start = max(0, j - 1)
                                end = min(len(lines), j + 2)
                                print(f"    コンテキスト:")
                                for k in range(start, end):
                                    if k == j:
                                        print(f"    > {lines[k]}")
                                    else:
                                        print(f"      {lines[k]}")
                                print()

                if not found:
                    print(f"  '{term}'の検索結果は見つかりませんでした。")

                chat_history.append({"system": f"'{term}'を検索しました。"})

            else:
                print("不明なコマンドです。コマンドのリストを表示するには 'help' と入力してください。")
                chat_history.append({"system": "不明なコマンドです。"})

        except KeyboardInterrupt:
            print("\nチャットを終了しています...")
            break

        except Exception as e:
            print(f"エラー: {e}")
            chat_history.append({"system": f"エラー: {e}"})

    print("\nチャットが終了しました。")

    if save_chat and chat_history:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        chat_file = f"chat_history_{timestamp}.json"
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
        print(f"チャット履歴が{chat_file}に保存されました")


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
        verbose=args.verbose
    )

    # スクレイパーを作成
    scraper = DeepwikiScraper(config)

    try:
        # コンテンツをスクレイピング
        logger.info(f"からコンテンツをスクレイピングしています {args.url}")
        results = scraper.scrape()

        if not results:
            logger.error("コンテンツのスクレイピングに失敗しました。")
            return 1

        logger.info(f"{len(results)}ページのスクレイピングに成功しました。")

        # 対話的なチャットを開始
        interactive_chat(results, args.save_chat)

        return 0
    except Exception as e:
        logger.exception(f"チャットモードでのエラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
