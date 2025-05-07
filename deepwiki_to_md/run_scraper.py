import argparse
import sys

import requests

from .deepwiki_to_md import DeepwikiScraper
from .localization import get_message


def parse_arguments():
    """Parse command line arguments."""
    # """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(description=get_message('scraper_description'))

    parser.add_argument('--library', '-l', action='append', nargs=2, metavar=('NAME', 'URL'),
                        help=get_message('library_help'))

    parser.add_argument('--output-dir', '-o', default='Documents',
                        help=get_message('output_dir_help', default='Documents'))

    parser.add_argument('--use-direct-scraper', action='store_true',
                        help=get_message('use_direct_scraper_help'))

    # 代替スクレイパーの引数は削除されました

    parser.add_argument('--use-direct-md-scraper', action='store_true',
                        help=get_message('use_direct_md_scraper_help'))

    parser.add_argument('--no-direct-md-scraper', action='store_true',
                        help=get_message('no_direct_md_scraper_help'))

    # Selenium-related arguments removed - only static requests are supported
    # Selenium関連の引数は削除されました - 静的リクエストのみがサポートされています

    parser.add_argument('library_url', nargs='?',
                        help=get_message('library_url_help'))

    args = parser.parse_args()

    # Handle the case where a library URL is provided as a positional argument
    # ライブラリURLが位置引数として提供された場合の処理
    if args.library_url and not args.library:
        # Extract library name from URL path
        # URLパスからライブラリ名を抽出
        from urllib.parse import urlparse
        path = urlparse(args.library_url).path.strip('/')
        library_name = path.split('/')[-1] if path else 'library'
        args.library = [(library_name, args.library_url)]

    # Validate arguments
    # 引数の検証
    if not args.library and not args.library_url:
        parser.error(get_message('library_required_error'))

    return args


def main():
    """Main function to run the scraper."""
    # """スクレイパーを実行するメイン関数。"""
    args = parse_arguments()

    # Format libraries as expected by DeepwikiScraper
    # DeepwikiScraperが期待する形式にライブラリをフォーマット
    libraries = [
        {"name": name, "url": url}
        for name, url in args.library
    ]

    # Determine whether to use DirectDeepwikiScraper
    # DirectDeepwikiScraperを使用するかどうかを決定
    use_direct_scraper = args.use_direct_scraper

    # 代替スクレイパーの機能は削除されました

    # Create and run the scraper
    # スクレイパーを作成して実行
    scraper = DeepwikiScraper(
        output_dir=args.output_dir,
        use_direct_scraper=use_direct_scraper,
    )

    try:
        # Process each library
        for library in libraries:
            name = library['name']
            url = library['url']
            print(get_message('scraping_library', library_name=name))
            saved_files = scraper.scrape_library(url, name)
            if saved_files:
                print(get_message('library_scraping_completed', library_name=name, count=len(saved_files)))
            else:
                print(get_message('library_scraping_failed', library_name=name))
        
        print(get_message('scraping_completed', output_dir=args.output_dir))
        return 0
    except requests.exceptions.RequestException as e:
        print(get_message('error', error=e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
