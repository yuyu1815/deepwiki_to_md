from typing import Optional, List
import sys
import argparse
import os
import logging
from urllib.parse import urlparse

from deepwiki_to_md import (
    ContentExtractor,
    split_markdown_by_h1,
    sanitize_filename,
)


class CLIInterface:
    """Command-line interface with extensible options"""

    def __init__(self):
        self.parser = self._setup_parser()
        self.extractor = ContentExtractor()

    def _setup_parser(self) -> argparse.ArgumentParser:
        """Setup command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Extract Markdown from Next.js HTML with pluggable strategies",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s sample.html --path ./output
  %(prog)s https://deepwiki.com/path --path ./output
            """
        )

        parser.add_argument(
            "input",
            nargs="?",
            help="Input HTML file path or URL (defaults to stdin)",
        )
        parser.add_argument(
            "--path",
            help="Output directory path (defaults to ./.deepwiki)",
        )

        return parser

    def run(self, args: List[str] = None) -> int:
        """Main CLI execution"""
        parsed_args = self.parser.parse_args(args)

        try:
            content = self._read_input(parsed_args)
            self._write_output(parsed_args, content)
            return 0
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return 1

    def _read_input(self, parsed_args: argparse.Namespace) -> str:
        """Read input from URL, file, or stdin with minimal branching."""
        if parsed_args.input:
            if self._is_url(parsed_args.input):
                return self.extractor.extract_from_url(parsed_args.input)
            with open(parsed_args.input, "r", encoding="utf-8") as f:
                html = f.read()
            return self.extractor.extract_from_html(html, parsed_args.input)
        html = sys.stdin.read()
        return self.extractor.extract_from_html(html)

    def _write_output(self, parsed_args: argparse.Namespace, content: str) -> None:
        """Write output to files or stdout based on arguments; minimize nesting by early returns."""
        if not (parsed_args.input and self._is_url(parsed_args.input)):
            sys.stdout.write(content)
            return
        parsed_url = urlparse(parsed_args.input)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        if len(path_parts) < 2:
            sys.stdout.write(content)
            return
        username, library_name = path_parts[0], path_parts[1]
        base_dir = parsed_args.path or ".deepwiki"
        output_dir = os.path.join(base_dir, username, library_name)
        os.makedirs(output_dir, exist_ok=True)
        sections = split_markdown_by_h1(content)
        saved_files: List[str] = []
        for section in sections:
            title = section['title']
            section_content = section['content']
            filename = sanitize_filename(title) + ".md"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(section_content)
            saved_files.append(file_path)
        library_file_path = os.path.join(base_dir, username, f"{library_name}.md")
        with open(library_file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {library_name} Documentation Index\n\n")
            f.write("This file contains links to all extracted documents.\n")
            f.write("Please refer to the files below for detailed information.\n\n")
            for file_path in saved_files:
                filename = os.path.basename(file_path)
                title = filename[:-3].replace('_', ' ')
                f.write(f"- [{title}]({library_name}/{filename})\n")
        print(f"Content split into {len(saved_files)} files:")
        for file_path in saved_files:
            print(f"  - {file_path}")
        print(f"Library file created at: {library_file_path}")

    def _is_url(self, s: str) -> bool:
        """Check if string is a URL"""
        try:
            parsed = urlparse(s)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False


def main(argv: Optional[List[str]] = None) -> int:
    cli = CLIInterface()
    return cli.run(argv)
