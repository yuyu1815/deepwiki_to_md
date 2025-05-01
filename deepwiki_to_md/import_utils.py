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
        from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper, scrape_deepwiki
        from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper
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

            # ダミー実装を定義
            class DummyDirectDeepwikiScraper:
                def __init__(self, *args, **kwargs):
                    logger.warning("DirectDeepwikiScraper は利用できません - 直接スクレイピングは無効になります")
                    pass

                def scrape_page(self, *args, **kwargs):
                    logger.error("DirectDeepwikiScraper.scrape_page が呼び出されましたが、モジュールが利用できません")
                    return None

            def dummy_scrape_deepwiki(url, **kwargs):
                logger.error("scrape_deepwiki 関数が呼び出されましたが、利用できません")
                return None

            class DummyDirectMarkdownScraper:
                def __init__(self, *args, **kwargs):
                    logger.warning(
                        "DirectMarkdownScraper は利用できません - 直接Markdownスクレイピングは無効になります")
                    pass

                def scrape_page(self, *args, **kwargs):
                    logger.error("DirectMarkdownScraper.scrape_page が呼び出されましたが、モジュールが利用できません")
                    return None

                def scrape_library(self, *args, **kwargs):
                    logger.error("DirectMarkdownScraper.scrape_library が呼び出されましたが、モジュールが利用できません")
                    return None

            return DummyDirectDeepwikiScraper, dummy_scrape_deepwiki, DummyDirectMarkdownScraper


def import_markdown_link_fixing_modules():
    """
    Markdownリンク修正モジュールをインポートする関数
    
    Returns:
        tuple: (fix_markdown_links, fix_markdown_links_in_file)
    """
    try:
        # 絶対インポートを最初に試す
        from deepwiki_to_md.fix_markdown_links import fix_markdown_links, fix_markdown_links_in_file
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

            # ダミー実装を定義
            def dummy_fix_markdown_links(directory):
                logger.error(
                    f"fix_markdown_links が呼び出されましたが、モジュールが利用できません - {directory} のリンクは修正されません")
                return

            def dummy_fix_markdown_links_in_file(file_path):
                logger.error(
                    f"fix_markdown_links_in_file が呼び出されましたが、モジュールが利用できません - {file_path} のリンクは修正されません")
                return 0

            return dummy_fix_markdown_links, dummy_fix_markdown_links_in_file


def import_fix_markdown_links_in_file():
    """
    fix_markdown_links_in_file 関数のみをインポートする関数
    
    Returns:
        function: fix_markdown_links_in_file 関数
    """
    try:
        # 絶対インポートを最初に試す
        from deepwiki_to_md.fix_markdown_links import fix_markdown_links_in_file
        logger.debug("fix_markdown_links_in_file を絶対インポートで読み込みました")
        return fix_markdown_links_in_file
    except ImportError:
        # 絶対インポートが失敗した場合、相対インポートを試す
        try:
            from .fix_markdown_links import fix_markdown_links_in_file
            logger.debug("fix_markdown_links_in_file を相対インポートで読み込みました")
            return fix_markdown_links_in_file
        except ImportError as e:
            logger.error(f"fix_markdown_links_in_file のインポートに失敗しました: {e}")

            # ダミー実装を定義
            def dummy_fix_markdown_links_in_file(file_path):
                logger.error(
                    f"fix_markdown_links_in_file が呼び出されましたが、モジュールが利用できません - {file_path} のリンクは修正されません")
                return 0

            return dummy_fix_markdown_links_in_file
