from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper

# スクレイパーを use_direct_md_scraper 有効（＝True）で作成
scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
)

# ライブラリ一覧
libraries = [
    {"name": "python", "url": "https://deepwiki.com/python/cpython"},
    # 他のライブラリも追加可能
]

# 実行
scraper.run(libraries)
