from typing import Optional, List, Dict, Any
import sys
import argparse
import os
import logging
import json
import asyncio
from urllib.parse import urlparse
from chat import load_config, send_chat_message

from deepwiki_to_md import (
    ContentExtractor,
    save_markdown_to_library,
)
from search_repository import search_repositories  # make search usable from CLI

MAX_REPO_NAME_LENGTH = 29  # Maximum repository name length
MAX_LANGUAGE_LENGTH = 11  # Maximum language label length
MAX_STARS_LENGTH = 7  # Maximum stars field length
MAX_ID_LENGTH = 14  # Maximum ID field length


def format_search_results_devlog(indices: List[Dict[str, Any]]) -> str:
    """Format search results in a human-readable table for --devlog.

    This helper isolates all layout/formatting so _run_search can focus on flow control.
    It preserves existing column widths and detail lines (Description/Topics/Last modified).
    """
    lines: List[str] = []

    # Header
    lines.append("=" * 80)
    lines.append(f"{'Repository':<30} | {'Language':<12} | {'Stars':>8} | {'ID':<15}")
    lines.append("=" * 80)

    # Rows
    for item in indices:
        repo_name_raw = item.get("repo_name") or "N/A"
        language_raw = item.get("language") or "N/A"
        stars_raw = item.get("stargazers_count") or "N/A"
        idx_id_raw = item.get("id") or "N/A"

        repo_name = str(repo_name_raw)[:MAX_REPO_NAME_LENGTH]
        language = str(language_raw)[:MAX_LANGUAGE_LENGTH]
        stars = str(stars_raw)[:MAX_STARS_LENGTH]
        idx_id = str(idx_id_raw)[:MAX_ID_LENGTH]

        lines.append(f"{repo_name:<30} | {language:<12} | {stars:>7} | {idx_id:<15}")

        desc = item.get("description")
        if desc:
            lines.append(f"  └─ Description: {desc}")

        topics = item.get("topics") or []
        if topics:
            topics_list = topics if isinstance(topics, (list, tuple)) else [topics]
            topics_str = ", ".join(map(str, topics_list))
            lines.append(f"  └─ Topics: {topics_str}")

        last_modified = item.get("last_modified")
        if last_modified:
            lines.append(f"  └─ Last modified: {last_modified}")

        lines.append("")  # separator blank line

    # Footer
    lines.append("=" * 80)
    lines.append(f"Total repositories: {len(indices)}")

    return "\n".join(lines)


class CLIInterface:
    """Command-line interface with extensible options.

    6-month clarity goals:
    - Use guard clauses and early returns to keep nesting shallow.
    - Split I/O responsibilities into small helpers (_read_input / _write_output).
    - Let run() handle errors at a single place and log appropriately.
    """

    def __init__(self):
        self.parser = self._setup_parser()
        self.extractor = ContentExtractor()

    def _setup_parser(self) -> argparse.ArgumentParser:
        """Set up the command-line argument parser."""
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
        """Main entry point for the CLI."""
        parsed_args = self.parser.parse_args(args)

        try:
            # Command selection: --search → --chat → extract
            if getattr(parsed_args, "search", None):
                return self._run_search(parsed_args)
            if getattr(parsed_args, "chat", None):
                return self._run_chat(parsed_args)
            # Extraction (default)
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
        """Write to files or stdout depending on the given arguments."""
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

    # Chat handling
    def _run_chat(self, parsed_args: argparse.Namespace) -> int:
        """Run chat processing (URL comes from positional input, message from --chat)."""
        # URL is required (guard clause)
        if not parsed_args.input:
            print("Error: When using --chat, provide a DeepWiki URL as the positional argument.")
            return 1
        if not parsed_args.chat:
            print("Error: Missing --chat <message>.")
            return 1

        config = load_config(parsed_args.config_file)
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

        # If --devlog is specified, display response body and reference files after the sending log (output by chat.py)
        if getattr(parsed_args, "devlog", False):
            print("--- chat message ---")
            response_body = api_result.get("response_message") or ""
            # 応答本文はそのまま出力（\n を含むプレーンテキスト）
            print(response_body)

            # If reference files exist, list them in a readable array format
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

            output = format_search_results_devlog(indices)
            print(output)
            return 0

        # 既定は JSON を返す
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0


def main(argv: Optional[List[str]] = None) -> int:
    cli = CLIInterface()
    return cli.run(argv)
