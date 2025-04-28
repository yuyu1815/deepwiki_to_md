import argparse
import sys

import requests

from .direct_scraper import DirectDeepwikiScraper


def parse_arguments():
    """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(description='DeepwikiからMarkdownを直接取得して保存する。')

    parser.add_argument('--library', '-l', action='append', nargs=2, metavar=('NAME', 'URL'),
                        help='ライブラリ名とスクレイピングするURL。複数回指定可能。')

    parser.add_argument('--output-dir', '-o', default='DynamicDocuments',
                        help='Markdownファイルの出力ディレクトリ (デフォルト: DynamicDocuments)')

    parser.add_argument('--save-html', action='store_true',
                        help='HTMLも保存する（デフォルト: False）')

    parser.add_argument('library_url', nargs='?',
                        help='スクレイピングするライブラリのURL（--libraryの代わりに使用可能）')

    args = parser.parse_args()

    # ライブラリURLが位置引数として提供された場合の処理
    if args.library_url and not args.library:
        # URLパスからライブラリ名を抽出
        from urllib.parse import urlparse
        path = urlparse(args.library_url).path.strip('/')
        library_name = path.split('/')[-1] if path else 'library'
        args.library = [(library_name, args.library_url)]

    # 引数の検証
    if not args.library and not args.library_url:
        parser.error("ライブラリURLまたは--libraryオプションでライブラリを少なくとも1つ指定してください")

    return args


def main():
    """スクレイパーを実行するメイン関数。"""
    args = parse_arguments()

    # DirectDeepwikiScraperが期待する形式にライブラリをフォーマット
    libraries = [
        {"name": name, "url": url}
        for name, url in args.library
    ]

    # スクレイパーを作成して実行
    scraper = DirectDeepwikiScraper(args.output_dir)

    try:
        results = scraper.run(libraries)
        
        # 結果の表示
        success_count = sum(1 for lib in results.values() if lib["success"])
        print(f"スクレイピングが完了しました。{len(libraries)}個中{success_count}個のライブラリが成功しました。")
        print(f"Markdownファイルは{args.output_dir}に保存されました。")
        
        return 0
    except requests.exceptions.RequestException as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())