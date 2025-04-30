"""
DeepwikiScraper クラスと DirectDeepwikiScraper クラスを直接使用する方法を示すサンプルスクリプトです。
このスクリプトは静的リクエストのみを使用します。
"""
from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper


def main():
    # 例 1: deepwiki.com からの静的スクレイピング
    libraries = [
        {
            "name": "python",
            "url": "https://deepwiki.com/python/cpython"
        }
    ]

    # DeepwikiScraper インスタンスを作成します
    print("\nInitializing scraper...")
    scraper = DeepwikiScraper(output_dir="Documents")

    # ライブラリに対してスクレイパーを実行します
    for library in libraries:
        print(f"Scraping {library['name']}...")
        scraper.scrape_library(library['name'], library['url'])

    # 例 3: DirectDeepwikiScraper を使用した直接スクレイピング
    direct_libraries = [
        {
            "name": "direct_python_example",
            "url": "https://deepwiki.com/python/cpython" # 特定のページURL
        }
    ]

    # DirectDeepwikiScraper インスタンスを作成します
    direct_scraper = DeepwikiScraper(output_dir="DirectScrapedDocuments", use_direct_scraper=True)

    # 各ライブラリ (この場合は特定のページ) に対してスクレイパーを実行します
    for library in direct_libraries:
        print(f"Scraping {library['name']} directly...")
        # scrape_library の代わりに scrape_page を使用して単一ページをスクレイピング
        # または、scrape_library を使用してライブラリ全体を試みることも可能 (実装による)
        # ここでは scrape_page を使用する例を示します
        saved_path = direct_scraper.scrape_page(library['url'], library['name'], save_html=True)
        if saved_path:
            print(f"Successfully scraped and saved to {saved_path}")
        else:
            print(f"Failed to scrape {library['url']}")

    # run メソッドを使用して複数のライブラリ/ページを一度に処理する例
    # direct_scraper_run = DirectDeepwikiScraper(output_dir="DirectScrapedRun")
    # run_results = direct_scraper_run.run(direct_libraries)
    # print("\nDirect scraping run results:")
    # print(run_results)

    print("\nスクレイピングが完了しました！")


if __name__ == "__main__":
    main()
