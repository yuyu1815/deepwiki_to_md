"""
DeepWikiからMarkdownへのコンバーター

このパッケージは、DeepWikiサイトからコンテンツをスクレイピングし、Markdown形式に変換するツールを提供します。
"""

from deepwiki_to_md.scraper.direct_markdown_scraper import DirectMarkdownScraper
from deepwiki_to_md.scraper.html_scraper import HtmlScraper


# URLに基づいて適切なスクレイパーを作成するファクトリ関数
def DeepwikiScraper(config):
    """
    URLに基づいて適切なスクレイパーを作成するファクトリ関数。
    
    Args:
        config (Config): URL、ライブラリ名、出力ディレクトリを含む設定オブジェクト。
        
    Returns:
        BaseScraper: 適切なスクレイパーのインスタンス。
    """
    # 現時点では、常にDirectMarkdownScraperを使用します
    return DirectMarkdownScraper(config)
