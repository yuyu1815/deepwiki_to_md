import argparse
import sys

import requests

try:
    from deepwiki_to_md.core.direct_scraper import DirectDeepwikiScraper
    from deepwiki_to_md.lang.localization import get_message
except ImportError:
    from .core.direct_scraper import DirectDeepwikiScraper
    from .lang.localization import get_message

def parse_arguments():
    """コマンドライン引数を解析する。"""
    # """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=get_message('direct_scraper_description'))

    parser.add_argument('--library', '-l', action='append', nargs=2, metavar=('NAME', 'URL'),
                        help=get_message('direct_library_help'))

    parser.add_argument('--output-dir', '-o', default='DynamicDocuments',
                        help=get_message('direct_output_dir_help', default='DynamicDocuments'))

    parser.add_argument('--save-html', action='store_true',
                        help=get_message('save_html_help'))

    parser.add_argument('library_url', nargs='?',
                        help=get_message('direct_library_url_help'))

    args = parser.parse_args()

    # ライブラリURLが位置引数として提供された場合の処理
    # Handle the case where a library URL is provided as a positional argument
    if args.library_url and not args.library:
        # URLパスからライブラリ名を抽出
        # Extract library name from URL path
        from urllib.parse import urlparse
        path = urlparse(args.library_url).path.strip('/')
        library_name = path.split('/')[-1] if path else 'library'
        args.library = [(library_name, args.library_url)]

    # 引数の検証
    # Validate arguments
    if not args.library and not args.library_url:
        parser.error(get_message('direct_library_required_error'))

    return args


def main():
    """スクレイパーを実行するメイン関数。"""
    # """Main function to run the scraper."""
    args = parse_arguments()

    # DirectDeepwikiScraperが期待する形式にライブラリをフォーマット
    # Format libraries as expected by DirectDeepwikiScraper
    libraries = [
        {"name": name, "url": url}
        for name, url in args.library
    ]

    # スクレイパーを作成して実行
    # Create and run the scraper
    scraper = DirectDeepwikiScraper(args.output_dir)

    try:
        results = scraper.run(libraries)

        # 結果の表示
        # Display results
        success_count = sum(1 for lib in results.values() if lib["success"])
        print(get_message('scraping_result', success_count=success_count, total=len(libraries)))
        print(get_message('files_saved', output_dir=args.output_dir))

        return 0
    except requests.exceptions.RequestException as e:
        print(get_message('error', error=e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
# DeepwikiからMarkdownを直接取得して保存する。
# Get and save Markdown directly from Deepwiki.
