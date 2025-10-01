from typing import Optional, List
import sys
import argparse
import os
import logging
import json
import asyncio
from urllib.parse import urlparse
from chat import load_or_create_config, send_chat_message

from deepwiki_to_md import (
    ContentExtractor,
    save_markdown_to_library,
)
from search_repository import search_repositories  # make search usable from CLI

MAX_REPO_NAME_LENGTH = 29  # リポジトリ名の最大長
MAX_LANGUAGE_LENGTH = 11  # 言語名の最大長
MAX_STARS_LENGTH = 7  # Star数の最大長
MAX_ID_LENGTH = 14  # ID の最大長


class CLIInterface:
    """拡張可能なオプションを備えたコマンドラインインターフェイス。
    
    半年後でも一瞬で理解できるように:
    - 早期リターン（ガード節）でネストを浅く保つ
    - 入出力を小さな責務に分割（_read_input / _write_output）
    - 例外は上位 run() で一括処理し、ログを残す
    """

    def __init__(self):
        self.parser = self._setup_parser()
        self.extractor = ContentExtractor()

    def _setup_parser(self) -> argparse.ArgumentParser:
        """コマンドライン引数パーサーを設定する。"""
        parser = argparse.ArgumentParser(
            description="Extract Markdown from Next.js HTML with pluggable strategies and chat API integration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
                Examples:
                  %(prog)s sample.html --path ./output
                  %(prog)s https://deepwiki.com/path --path ./output
                  %(prog)s https://deepwiki.com/microsoft/WSL --chat "Explain WSLg Wayland and RDP"
                  %(prog)s https://deepwiki.com/anything --search "vector database"
            """
        )

        # 抽出（デフォルト動作）/ Extract (default behavior)
        parser.add_argument(
            "input",
            nargs="?",
            help="Input HTML file path or URL (defaults to stdin). For --chat, this must be a DeepWiki URL.",
        )
        parser.add_argument(
            "--path",
            help="Output directory path (defaults to ./.deepwiki)",
        )
        # 検索: --search <query>
        parser.add_argument(
            "--search",
            metavar="QUERY",
            help="Search public repository indexes with the given query",
        )
        parser.add_argument(
            "--devlog",
            action="store_true",
            help="When used with --search, print human-readable lines instead of JSON",
        )
        # チャット: --chat <message>（URL は位置引数 input で受ける）
        parser.add_argument(
            "--chat",
            metavar="MESSAGE",
            help="Send a chat message to the Devin API (requires positional DeepWiki URL)",
        )
        parser.add_argument(
            "--deep-research",
            action="store_true",
            help="Enable deep research mode for chat",
        )
        parser.add_argument(
            "--config-file",
            default="config.json",
            help="Config file path for chat (default: ./config.json). The file must already exist and contain complete settings.",
        )

        return parser

    def run(self, args: List[str] = None) -> int:
        """CLI のメイン実行。"""
        parsed_args = self.parser.parse_args(args)

        try:
            # コマンド判定（--search → --chat → 抽出）
            if getattr(parsed_args, "search", None):
                return self._run_search(parsed_args)
            if getattr(parsed_args, "chat", None):
                return self._run_chat(parsed_args)
            # 抽出（デフォルト）
            content = self._read_input(parsed_args)
            self._write_output(parsed_args, content)
            return 0
        except Exception as e:
            logging.error(f"CLI failed: {e}")
            return 1

    def _read_input(self, parsed_args: argparse.Namespace) -> str:
        """Read input from URL, file, or stdin with clear guard clauses.
        Rules:
        - If no positional input is provided: read from stdin (non-tty) or error if tty.
        - If input has an http/https scheme: treat as URL.
        - If input is an existing file: read as local HTML.
        - Otherwise: treat as DeepWiki path/URL and pass through to extractor.
        """
        inp = getattr(parsed_args, "input", None)

        # No positional input → read from stdin when piped; else error
        if not inp:
            if sys.stdin.isatty():
                self.parser.error("Input is required when not reading from stdin.")
            html = sys.stdin.read()
            return self.extractor.extract_from_html(html, "stdin")

        # URL first (avoid misclassifying URLs ending with .html as files)
        parsed = urlparse(inp)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return self.extractor.extract_from_url(inp)

        # Existing file path
        if os.path.isfile(inp):
            with open(inp, "r", encoding="utf-8") as f:
                html = f.read()
            return self.extractor.extract_from_html(html, inp)

        # Fallback: treat as DeepWiki library path or URL-like string
        return self.extractor.extract_from_url(inp)



    def _write_output(self, parsed_args: argparse.Namespace, content: str) -> None:
        """引数に応じてファイルまたは標準出力へ書き出す"""
        if not parsed_args.input:
            sys.stdout.write(content)
            return
        base_dir = parsed_args.path or ".deepwiki"
        result = save_markdown_to_library(content, parsed_args.input, base_dir)
        saved_files = result.get("saved_files", [])
        library_file_path = result.get("library_file")
        print(f"Content split into {len(saved_files)} files:")
        for file_path in saved_files:
            print(f"  - {file_path}")
        if library_file_path:
            print(f"Library file created at: {library_file_path}")

    # チャット処理
    def _run_chat(self, parsed_args: argparse.Namespace) -> int:
        """チャット処理を実行（URL は位置引数 input、メッセージは --chat）。"""
        # URL 必須チェック（ガード節）
        if not parsed_args.input:
            print("Error: --chat を使う場合は、位置引数に DeepWiki の URL を指定してください。")
            return 1
        if not parsed_args.chat:
            print("Error: --chat <message> が指定されていません。")
            return 1

        config = load_or_create_config(parsed_args.config_file)
        if not config:
            print("Failed to load configuration. Aborting.")
            return 1

        api_result = asyncio.run(send_chat_message(
            parsed_args.input,
            parsed_args.chat,
            config,
            bool(parsed_args.deep_research),
            bool(getattr(parsed_args, "devlog", False)),
        ))

        # --devlog が指定された場合は、送信ログ（chat.py 側で出力）に続けて、応答本文と参照ファイルを表示
        if getattr(parsed_args, "devlog", False):
            print("--- chat message ---")
            response_body = api_result.get("response_message") or ""
            # 応答本文はそのまま出力（\n を含むプレーンテキスト）
            print(response_body)

            # 参照ファイルがあれば、見やすい配列形式で列挙
            reference_files = api_result.get("reference_files") or []
            if reference_files:
                print()
                print(f'"reference_files": {reference_files}')
            return 0

        # 既定は JSON のみを返す
        print(json.dumps(api_result, indent=4, ensure_ascii=False))
        return 0
    # ライブラリ検索
    def _run_search(self, parsed_args: argparse.Namespace) -> int:
        """リポジトリの公開インデックスを検索する。デフォルトは JSON、--devlog で人間可読出力。"""
        term = getattr(parsed_args, "search", None) or "Gemini"
        result = search_repositories(term)
        # -devlog の場合
        if getattr(parsed_args, "devlog", False):
            indices = result.get("indices", []) if isinstance(result, dict) else []

            if not indices:
                print("No repositories found.")
                return 0

            # テーブル形式でヘッダーを表示
            print("=" * 80)
            print(f"{'Repository':<30} | {'Language':<12} | {'Stars':>8} | {'ID':<15}")
            print("=" * 80)

            # 各リポジトリの情報をテーブル形式で表示
            for item in indices:
                # Robustly coerce potentially null fields to strings before slicing
                repo_name_raw = item.get("repo_name") or "N/A"
                language_raw = item.get("language") or "N/A"
                stars_raw = item.get("stargazers_count") or "N/A"
                idx_id_raw = item.get("id") or "N/A"

                # Coerce potentially null fields to strings and slice to maximum lengths
                repo_name = str(repo_name_raw)[:MAX_REPO_NAME_LENGTH]
                language = str(language_raw)[:MAX_LANGUAGE_LENGTH]
                stars = str(stars_raw)[:MAX_STARS_LENGTH]
                idx_id = str(idx_id_raw)[:MAX_ID_LENGTH]

                print(f"{repo_name:<30} | {language:<12} | {stars:>7} | {idx_id:<15}")

                # 詳細情報をインデントして表示
                desc = item.get("description")
                if desc:
                    print(f"  └─ Description: {desc}")

                topics = item.get("topics") or []
                if topics:
                    topics_list = topics if isinstance(topics, (list, tuple)) else [topics]
                    topics_str = ", ".join(map(str, topics_list))
                    print(f"  └─ Topics: {topics_str}")

                last_modified = item.get("last_modified")
                if last_modified:
                    print(f"  └─ Last modified: {last_modified}")

                print()  # 空行で区切り

            # フッター
            print("=" * 80)
            print(f"Total repositories: {len(indices)}")
            return 0

        # 既定は JSON を返す
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0


def main(argv: Optional[List[str]] = None) -> int:
    cli = CLIInterface()
    return cli.run(argv)
