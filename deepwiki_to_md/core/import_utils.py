import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def import_scraping_modules():
    """
    スクレイピングモジュールをインポートする関数
    
    Returns:
        tuple: (DirectDeepwikiScraper, scrape_deepwiki, DirectMarkdownScraper)
    """
    try:
        # 絶対インポートを最初に試す
        from deepwiki_to_md.core.direct_scraper import DirectDeepwikiScraper, scrape_deepwiki
        from deepwiki_to_md.core.direct_md_scraper import DirectMarkdownScraper
        logger.debug("スクレイピングモジュールを絶対インポートで読み込みました")
        return DirectDeepwikiScraper, scrape_deepwiki, DirectMarkdownScraper
    except ImportError:
        # 絶対インポートが失敗した場合、相対インポートを試す
        try:
            from .direct_scraper import DirectDeepwikiScraper, scrape_deepwiki
            from .direct_md_scraper import DirectMarkdownScraper
            logger.debug("スクレイピングモジュールを相対インポートで読み込みました")
            return DirectDeepwikiScraper, scrape_deepwiki, DirectMarkdownScraper
        except ImportError as e:
            logger.error(f"スクレイピングモジュールのインポートに失敗しました: {e}")


def import_markdown_link_fixing_modules():
    """
    Markdownリンク修正モジュールをインポートする関数
    
    Returns:
        tuple: (fix_markdown_links, fix_markdown_links_in_file)
    """
    try:
        # 絶対インポートを最初に試す
        from deepwiki_to_md.core.fix_markdown_links import fix_markdown_links, fix_markdown_links_in_file
        logger.debug("Markdownリンク修正モジュールを絶対インポートで読み込みました")
        return fix_markdown_links, fix_markdown_links_in_file
    except ImportError:
        # 絶対インポートが失敗した場合、相対インポートを試す
        try:
            from .fix_markdown_links import fix_markdown_links, fix_markdown_links_in_file
            logger.debug("Markdownリンク修正モジュールを相対インポートで読み込みました")
            return fix_markdown_links, fix_markdown_links_in_file
        except ImportError as e:
            logger.error(f"Markdownリンク修正モジュールのインポートに失敗しました: {e}")


def import_fix_markdown_links_in_file():
    """
    fix_markdown_links_in_file 関数のみをインポートする関数
    
    Returns:
        function: fix_markdown_links_in_file 関数
    """
    try:
        # 絶対インポートを最初に試す
        from deepwiki_to_md.core.fix_markdown_links import fix_markdown_links_in_file
        logger.debug("fix_markdown_links_in_file 関数を絶対インポートで読み込みました")
        return fix_markdown_links_in_file
    except ImportError:
        # 絶対インポートが失敗した場合、相対インポートを試す
        try:
            from .fix_markdown_links import fix_markdown_links_in_file
            logger.debug("fix_markdown_links_in_file 関数を相対インポートで読み込みました")
            return fix_markdown_links_in_file
        except ImportError as e:
            logger.error(f"fix_markdown_links_in_file 関数のインポートに失敗しました: {e}")
