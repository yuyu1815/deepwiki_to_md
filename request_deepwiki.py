from deepwiki_to_md.deepwiki_to_md import DirectDeepwikiScraper

direct_libraries = [
    {
        "name": "direct_python_example",
        "url": "https://deepwiki.com/python/cpython"  # 特定のページURL
    }
]

# DirectDeepwikiScraper インスタンスを作成します
direct_scraper = DirectDeepwikiScraper(output_dir="DirectScrapedDocuments")

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