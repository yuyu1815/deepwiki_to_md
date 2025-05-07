import logging
from typing import Optional, List

# Import fix_markdown_links function
try:
    from deepwiki_to_md.fix_markdown_links import fix_markdown_links
except ImportError:
    # If the module import fails, try relative import
    try:
        from .fix_markdown_links import fix_markdown_links
    except ImportError:
        logging.error("Could not import fix_markdown_links module")


        # Define a dummy function that does nothing if import fails
        # インポートに失敗した場合、何もしないダミー関数を定義する
        def fix_markdown_links(directory):
            logging.error("fix_markdown_links module not available")
            return

# Import DirectDeepwikiScraper
try:
    from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper
except ImportError:
    # If the module import fails, try relative import
    try:
        from .direct_scraper import DirectDeepwikiScraper
    except ImportError:
        logging.error("Could not import DirectDeepwikiScraper module")
        # Define a dummy class that does nothing if import fails
        # インポートに失敗した場合、何もしないダミークラスを定義する
        class DirectDeepwikiScraper:
            def __init__(self, *args, **kwargs):
                pass
            def scrape_page(self, *args, **kwargs):
                raise NotImplementedError("DirectDeepwikiScraper is not available.")

# 代替スクレイパー関連のインポートは削除されました

# Import DirectMarkdownScraper
try:
    from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper
except ImportError:
    # If the module import fails, try relative import
    try:
        from .direct_md_scraper import DirectMarkdownScraper
    except ImportError:
        logging.error("Could not import DirectMarkdownScraper module")
        # Define a dummy class that does nothing if import fails
        # インポートに失敗した場合、何もしないダミークラスを定義する
        class DirectMarkdownScraper:
            def __init__(self, *args, **kwargs):
                pass
            def scrape_page(self, *args, **kwargs):
                raise NotImplementedError("DirectMarkdownScraper is not available.")

# Import HTMLToMarkdownScraper
try:
    from deepwiki_to_md.html_to_md_scraper import HTMLToMarkdownScraper
except ImportError:
    # If the module import fails, try relative import
    try:
        from .html_to_md_scraper import HTMLToMarkdownScraper
    except ImportError:
        logging.error("Could not import HTMLToMarkdownScraper module")


        # Define a dummy class that does nothing if import fails
        # インポートに失敗した場合、何もしないダミークラスを定義する
        class HTMLToMarkdownScraper:
            def __init__(self, *args, **kwargs):
                pass

            def scrape_page(self, *args, **kwargs):
                raise NotImplementedError("HTMLToMarkdownScraper is not available.")

from .localization import get_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeepwikiScraper:
    def __init__(self, output_dir: str = "Documents", use_direct_scraper: bool = False,
                 use_direct_md_scraper: bool = True):
        """
        Initialize the DeepwikiScraper.
        DeepwikiScraperを初期化します。

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
                              変換されたMarkdownファイルを保存する基本ディレクトリ。

            use_direct_scraper (bool): Whether to use DirectDeepwikiScraper for scraping.
                                       スクレイピングにDirectDeepwikiScraperを使用するかどうか。

            # 代替スクレイパーのパラメータは削除されました

            use_direct_md_scraper (bool): Whether to use DirectMarkdownScraper for direct Markdown scraping.
                                          Markdownの直接スクレイピングに DirectMarkdownScraper を使用するかどうか。
                                          When True, this method is prioritized over all others. Default is True.
                                          True の場合、この方法が最も優先されます。デフォルトは True。
        """
        self.output_dir = output_dir

        # Set scraping strategy based on parameters
        if use_direct_scraper:
            self.use_direct_scraper = True
            self.use_direct_md_scraper = False
            self.use_html_to_md_scraper = False
        elif use_direct_md_scraper:
            self.use_direct_scraper = False
            self.use_direct_md_scraper = True
            self.use_html_to_md_scraper = False
        else:
            # Default to HTML to MD scraper if no other strategy is specified
            self.use_direct_scraper = False
            self.use_direct_md_scraper = False
            self.use_html_to_md_scraper = True

        # Initialize scrapers based on selected strategy
        if self.use_direct_md_scraper:
            self.direct_md_scraper = DirectMarkdownScraper(output_dir)
            logger.info("Using DirectMarkdownScraper for scraping")
            
        if self.use_direct_scraper:
            self.direct_scraper = DirectDeepwikiScraper(output_dir)
            logger.info("Using DirectDeepwikiScraper for scraping")

        if self.use_html_to_md_scraper:
            self.html_to_md_scraper = HTMLToMarkdownScraper(output_dir)
            logger.info("Using HTMLToMarkdownScraper for scraping")

    def scrape_page(self, url: str, library_name: Optional[str] = None) -> Optional[str]:
        """
        Scrape a page using the selected strategy.
        選択された戦略を使用してページをスクレイピングします。

        Args:
            url (str): The URL of the page to scrape.
                       スクレイピングするページのURL。
            library_name (str, optional): The name of the library.
                                          ライブラリの名前。

        Returns:
            Optional[str]: The path to the saved Markdown file, or None if scraping failed.
                           保存されたMarkdownファイルのパス、またはスクレイピングが失敗した場合はNone。
        """
        # Try DirectMarkdownScraper first (highest priority)
        if self.use_direct_md_scraper:
            try:
                logger.info(get_message('using_direct_md_scraper', url=url))
                return self.direct_md_scraper.scrape_page(url, library_name)
            except Exception as e:
                logger.error(f"Error using DirectMarkdownScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Fall back to next strategy

        # Try DirectDeepwikiScraper next
        if self.use_direct_scraper:
            try:
                logger.info(get_message('using_direct_scraper', url=url))
                return self.direct_scraper.scrape_page(url, library_name, save_html=True, debug=False)
            except Exception as e:
                logger.error(f"Error using DirectDeepwikiScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Fall back to next strategy

        # 代替スクレイパーのコードは削除されました

        # Finally, try HTML to Markdown scraper
        if self.use_html_to_md_scraper:
            try:
                logger.info(get_message('using_html_to_md_scraper', url=url))
                return self.html_to_md_scraper.scrape_page(url, library_name)
            except Exception as e:
                logger.error(f"Error using HTMLToMarkdownScraper for {url}: {e}")
                import traceback
                logger.error(traceback.format_exc())

        # If all strategies fail, return None
        logger.error(f"All scraping strategies failed for {url}")
        return None

    def scrape_library(self, url: str, library_name: Optional[str] = None) -> List[str]:
        """
        Scrape a library by starting from the given URL and following navigation links.
        指定されたURLから始めて、ナビゲーションリンクをたどってライブラリをスクレイピングします。

        Args:
            url (str): The URL of the library's main page.
                       ライブラリのメインページのURL。
            library_name (str, optional): The name of the library.
                                          ライブラリの名前。

        Returns:
            List[str]: A list of paths to the saved Markdown files.
                       保存されたMarkdownファイルのパスのリスト。
        """
        # Initialize list to store saved file paths
        saved_files = []

        # Scrape the main page first
        main_file = self.scrape_page(url, library_name)
        if main_file:
            saved_files.append(main_file)

        # If using HTML to MD scraper, extract navigation items and scrape them
        if self.use_html_to_md_scraper:
            # Get HTML content of the main page
            html_content = self.html_to_md_scraper.get_page_content(url)
            if html_content:
                # Extract navigation items
                nav_items = self.html_to_md_scraper.extract_navigation_items(html_content, url)
                logger.info(f"Found {len(nav_items)} navigation items")

                # Scrape each navigation item
                for item in nav_items:
                    item_url = item['url']
                    item_title = item['title']
                    logger.info(f"Scraping navigation item: {item_title} ({item_url})")
                    item_file = self.scrape_page(item_url, library_name)
                    if item_file:
                        saved_files.append(item_file)

        return saved_files
