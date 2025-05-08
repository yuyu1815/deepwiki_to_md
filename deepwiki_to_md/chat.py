import argparse
import logging
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Import the md_to_yaml module
try:
    from deepwiki_to_md.core.md_to_yaml import markdown_to_yaml, html_to_markdown, html_to_yaml, convert_md_file_to_yaml
    from deepwiki_to_md.lang.localization import get_message
except ImportError:
    from .core.md_to_yaml import markdown_to_yaml, html_to_markdown, html_to_yaml, convert_md_file_to_yaml
    from .lang.localization import get_message

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChatScraperSelenium:
    def __init__(self, output_dir="ChatResponses", headless=False, output_format="html"):
        """
        Initialize the ChatScraperSelenium.

        Args:
            output_dir (str): The directory to save the responses.
            headless (bool): Whether to run the browser in headless mode.
            output_format (str): The format to save the responses in. Can be "html", "md", "yaml", or a comma-separated list of formats.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Parse output_format to handle multiple formats
        self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]

        # Validate output formats
        valid_formats = ["html", "md", "yaml"]
        for fmt in self.output_formats:
            if fmt not in valid_formats:
                logger.warning(f"無効な出力フォーマット: {fmt}。'html'、'md'、または 'yaml' を使用してください。")
                logger.warning(f"Invalid output format: {fmt}. Use 'html', 'md', or 'yaml'.")
                self.output_formats.remove(fmt)

        # Default to HTML if no valid formats are specified
        if not self.output_formats:
            logger.warning("有効な出力フォーマットが指定されていません。デフォルトの 'html' を使用します。")
            logger.warning("No valid output formats specified. Using default 'html'.")
            self.output_formats = ["html"]

        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def send_chat_message(self, url, message, chat_selector="textarea", submit_selector="button[type='submit']",
                          wait_time=5, debug=False, use_deep_research=False):
        """
        Send a chat message and retrieve the response.

        Args:
            url (str): The URL of the chat interface.
            message (str): The message to send.
            chat_selector (str): CSS selector for the chat input element.
            submit_selector (str): CSS selector for the submit button.
            wait_time (int): Time to wait for response in seconds.
            debug (bool): Whether to enable debug mode.
            use_deep_research (bool): Whether to enable the "深い研究" (Deep Research) toggle.

        Returns:
            str or None: The HTML of the response, or None if no response was found.
        """
        try:
            logger.info(f"URLにアクセス中: {url}")
            self.driver.get(url)

            # 現在のウィンドウハンドルを保存
            # Save the current window handle
            original_window = self.driver.current_window_handle

            # チャット入力要素を待機して取得
            chat_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, chat_selector)))

            # 入力要素を含むフォームを見つける
            # Find the form containing the input element
            form_element = None
            try:
                form_element = chat_input.find_element(By.XPATH, "./ancestor::form")
                logger.info("フォーム要素を見つけました")
            except Exception as e:
                logger.warning(f"フォーム要素が見つかりませんでした。直接セレクタを使用します: {e}")

            chat_input.clear()
            chat_input.send_keys(message)
            logger.info(f"メッセージ入力: {message}")

            # 深い研究トグルを有効にする（存在する場合）
            if use_deep_research:
                try:
                    if form_element:
                        # フォーム内で深い研究トグルを探す
                        deep_research_label = form_element.find_element(By.XPATH,
                                                                        ".//label[contains(text(), '深い研究')]")
                        if deep_research_label:
                            # ラベルの親要素からトグルを見つける
                            toggle_div = deep_research_label.find_element(By.XPATH,
                                                                          "./following-sibling::div[@id='useDeep']")
                            if toggle_div:
                                toggle_div.click()
                                logger.info("「深い研究」トグルを有効化しました")
                    else:
                        # フォームが見つからない場合は従来の方法で探す
                        deep_research_label = self.driver.find_element(By.XPATH,
                                                                       "//label[contains(text(), '深い研究')]")
                        if deep_research_label:
                            toggle_div = deep_research_label.find_element(By.XPATH,
                                                                          "./following-sibling::div[@id='useDeep']")
                            if toggle_div:
                                toggle_div.click()
                                logger.info("「深い研究」トグルを有効化しました")
                except Exception as e:
                    logger.warning(f"「深い研究」トグルが見つからないか、クリックできませんでした: {e}")

            # 送信ボタンを探してクリック
            submit_button = None
            if form_element:
                # フォーム内でボタンを探す（より信頼性が高い）
                try:
                    # まずフォーム内で指定されたセレクタを使用
                    submit_button = form_element.find_element(By.CSS_SELECTOR, submit_selector)
                    logger.info("フォーム内で指定されたセレクタでボタンを見つけました")
                except Exception:
                    # 指定されたセレクタが見つからない場合、フォーム内の任意のボタンを探す
                    try:
                        submit_button = form_element.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        logger.info("フォーム内でtype='submit'のボタンを見つけました")
                    except Exception:
                        try:
                            # 最後の手段としてフォーム内の任意のボタンを探す
                            submit_button = form_element.find_element(By.TAG_NAME, "button")
                            logger.info("フォーム内で任意のボタンを見つけました")
                        except Exception as e:
                            logger.warning(f"フォーム内でボタンが見つかりませんでした: {e}")

            # フォーム内でボタンが見つからなかった場合、従来の方法で探す
            if not submit_button:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector)))
                logger.info("従来の方法でボタンを見つけました")

            # ボタンをクリック
            submit_button.click()
            logger.info("送信ボタンをクリック")

            # 新しいタブが開いたかチェック
            # Check if a new tab has opened
            wait_new_tab = WebDriverWait(self.driver, 5)
            try:
                # 新しいウィンドウが開くのを待機
                # Wait for a new window to open
                wait_new_tab.until(lambda d: len(d.window_handles) > 1)
                logger.info("新しいタブが開きました")

                # 新しいタブに切り替え
                # Switch to the new tab
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        logger.info("新しいタブに切り替えました")
                        break
            except Exception as e:
                logger.info(f"新しいタブは開きませんでした: {e}")

            # サムズアップ/ダウンボタンが表示されるのを待機（メッセージ完了の指標）
            # Wait for thumbs up/down buttons to appear (indicator of message completion)
            thumbs_selector = "div.flex.items-center.gap-1.text-neutral-300"
            try:
                # 最大wait_time秒間待機
                # Wait for a maximum of wait_time seconds
                thumbs_wait = WebDriverWait(self.driver, wait_time)
                thumbs_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, thumbs_selector)))
                logger.info("サムズアップ/ダウンボタンが表示されました（メッセージ完了）")
            except Exception as e:
                logger.warning(f"サムズアップ/ダウンボタンが表示されませんでした: {e}")
                # 固定の待機時間を使用
                # Use fixed wait time as fallback
                logger.info(f"{wait_time}秒間待機中...")
                time.sleep(wait_time)

            # レスポンス要素を取得
            response_html = self._extract_response_html()
            if response_html:
                self._save_response(response_html, message)
                return response_html
            else:
                logger.warning("レスポンスが見つかりませんでした")
                return None

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            return None

    def _extract_response_html(self):
        # 可能性のあるセレクターのリスト
        selectors = [
            'div.prose-custom',
            'div.dark\\:\\[\\&amp\\;_pre\\:has\\(code\\)\\]\\:bg-shade',
            '.chat-response',
            '.message-content',
            '.response-content',
            '.ai-response',
            'div[role="presentation"]',
            'div.chat-message',
            'div.response',
            # 新しいタブでのレスポンス要素のセレクター
            # Selectors for response elements in the new tab
            'main article',
            'main .content',
            'article',
            '.markdown-body'
        ]

        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    logger.info(f"レスポンス要素を発見: {selector}")

                    # サムズアップ/ダウンボタンが存在するか確認
                    # Check if thumbs up/down buttons exist
                    thumbs_selector = "div.flex.items-center.gap-1.text-neutral-300"
                    try:
                        thumbs_element = self.driver.find_element(By.CSS_SELECTOR, thumbs_selector)
                        logger.info("サムズアップ/ダウンボタンを発見")

                        # サムズアップ/ダウンボタンを含むレスポンスを返す
                        # Return the response including thumbs up/down buttons
                        full_html = element.get_attribute("outerHTML")
                        thumbs_html = thumbs_element.get_attribute("outerHTML")
                        return f"{full_html}\n{thumbs_html}"
                    except:
                        # サムズアップ/ダウンボタンが見つからない場合は通常のレスポンスを返す
                        # Return the normal response if thumbs up/down buttons are not found
                        return element.get_attribute("outerHTML")
            except Exception as e:
                continue

        logger.warning("レスポンス要素が見つかりませんでした")
        return None

    def _html_to_markdown(self, html_content):
        """
        Convert HTML content to Markdown.

        Args:
            html_content (str): The HTML content to convert.

        Returns:
            str: The Markdown content.
        """
        return html_to_markdown(html_content)

    def _html_to_yaml(self, html_content):
        """
        Convert HTML content to YAML.

        Args:
            html_content (str): The HTML content to convert.

        Returns:
            str: The YAML content.
        """
        return html_to_yaml(html_content)

    def _markdown_to_yaml(self, markdown_content):
        """
        Convert Markdown content to YAML while preserving formatting.

        Args:
            markdown_content (str): The Markdown content to convert.

        Returns:
            str: The YAML content.
        """
        return markdown_to_yaml(markdown_content)

    def _save_response(self, html_content, query):
        """
        Save the response in the specified formats.

        Args:
            html_content (str): The HTML content to save.
            query (str): The query that generated the response.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        query_part = re.sub(r'[^\w\s]', '', query)[:20].strip().replace(' ', '_')
        base_filename = f"{timestamp}_{query_part}"

        saved_files = []

        # Save in each specified format
        for fmt in self.output_formats:
            if fmt == "html":
                # Save as HTML
                html_filename = f"{base_filename}.html"
                html_file_path = os.path.join(self.output_dir, html_filename)
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                saved_files.append(html_file_path)
                logger.info(f"HTMLレスポンスを保存しました: {html_file_path}")
                logger.info(f"Saved HTML response: {html_file_path}")

            elif fmt == "md":
                # Convert to Markdown and save
                markdown_content = self._html_to_markdown(html_content)
                if markdown_content:
                    md_filename = f"{base_filename}.md"
                    md_file_path = os.path.join(self.output_dir, md_filename)
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    saved_files.append(md_file_path)
                    logger.info(f"Markdownレスポンスを保存しました: {md_file_path}")
                    logger.info(f"Saved Markdown response: {md_file_path}")

            elif fmt == "yaml":
                # If we already have Markdown content, convert directly from Markdown to YAML
                # This preserves formatting better than going through HTML
                if 'md' in self.output_formats and 'markdown_content' in locals():
                    yaml_content = self._markdown_to_yaml(markdown_content)
                else:
                    # Otherwise convert from HTML to YAML
                    yaml_content = self._html_to_yaml(html_content)

                if yaml_content:
                    yaml_filename = f"{base_filename}.yaml"
                    yaml_file_path = os.path.join(self.output_dir, yaml_filename)
                    with open(yaml_file_path, 'w', encoding='utf-8') as f:
                        f.write(yaml_content)
                    saved_files.append(yaml_file_path)
                    logger.info(f"YAMLレスポンスを保存しました: {yaml_file_path}")
                    logger.info(f"Saved YAML response: {yaml_file_path}")

        return saved_files

    def close(self):
        self.driver.quit()


def convert_md_to_yaml(md_file_path, output_dir=None):
    """
    Convert an existing Markdown file to YAML format.

    Args:
        md_file_path (str): Path to the Markdown file
        output_dir (str, optional): Directory to save the YAML file. If None, saves in the same directory as the Markdown file.

    Returns:
        str: Path to the created YAML file
    """
    # Use the imported function from md_to_yaml module
    return convert_md_file_to_yaml(md_file_path, output_dir)


def parse_arguments():
    """
    コマンドライン引数を解析する
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description=get_message("chat_scraper_description", default="DeepWiki Chat Scraper"))

    # Add a subparser for the convert mode
    subparsers = parser.add_subparsers(dest="mode", help=get_message("operation_mode_help", default="Operation mode"))

    # Convert mode parser
    convert_parser = subparsers.add_parser("convert", help=get_message("convert_mode_help", default="Convert mode"))
    convert_parser.add_argument("--md", required=True,
                                help=get_message("md_file_path_help", default="Path to Markdown file to convert"))
    convert_parser.add_argument("--output",
                                help=get_message("output_dir_help", default="Output directory"))

    # Add chat mode arguments to the main parser for backward compatibility
    parser.add_argument("--url", help=get_message("chat_url_help", default="URL of the chat interface"))
    parser.add_argument("--message", help=get_message("chat_message_help", default="Message to send"))
    parser.add_argument("--selector", default="textarea",
                        help=get_message("chat_selector_help",
                                         default="CSS selector for the chat input element [default: textarea]"))
    parser.add_argument("--button", default="button",
                        help=get_message("chat_button_help",
                                         default="CSS selector for the submit button [default: button]"))
    parser.add_argument("--wait", type=int, default=30,
                        help=get_message("chat_wait_help",
                                         default="Time to wait for response in seconds [default: 30]"))
    parser.add_argument("--debug", action="store_true",
                        help=get_message("debug_mode_help", default="Enable debug mode"))
    parser.add_argument("--output", default="ChatResponses",
                        help=get_message("chat_output_dir_help", default="Output directory [default: ChatResponses]"))
    parser.add_argument("--deep", action="store_true",
                        help=get_message("deep_research_help", default="Enable Deep Research mode"))
    parser.add_argument("--headless", action="store_true",
                        help=get_message("headless_mode_help", default="Enable headless mode"))
    parser.add_argument("--format", default="html",
                        help=get_message("output_format_help",
                                         default="Output format (html, md, yaml, or a comma-separated list) [default: html]"))

    args = parser.parse_args()

    # Set default mode to chat if not specified or if chat-related arguments are provided
    if args.mode is None:
        if args.url or args.message:
            args.mode = "chat"
        else:
            args.mode = "chat"  # Default to chat mode

    # Validate required arguments for chat mode
    if args.mode == "chat" and (args.url is None or args.message is None):
        parser.error(
            get_message("chat_mode_required_args_error", default="Chat mode requires --url and --message arguments"))

    return args


def main():
    # コマンドライン引数を解析
    # Parse command line arguments
    args = parse_arguments()

    # モードに応じて処理を分岐
    # Branch processing according to mode
    if args.mode == "convert":
        # Markdown to YAML conversion mode
        print(
            get_message("converting_markdown_file", default="Converting Markdown file: {file_path}", file_path=args.md))

        yaml_file = convert_md_to_yaml(args.md, args.output)

        if yaml_file:
            print(get_message("yaml_file_created", default="Created YAML file: {file_path}", file_path=yaml_file))
        else:
            print(get_message("conversion_failed", default="Conversion failed"))
    else:  # "chat" mode (default)
        # スクレイパーを初期化
        # Initialize the scraper
        scraper = ChatScraperSelenium(
            output_dir=args.output,
            headless=args.headless,
            output_format=args.format
        )

        try:
            # メッセージを送信
            # Send the message
            print(get_message("accessing_url", default="Accessing URL: {url}", url=args.url))
            print(get_message("message_info", default="Message: {message}", message=args.message))
            if args.deep:
                print(get_message("deep_research_enabled", default="Deep Research mode is enabled"))
            print(get_message("output_format_info", default="Output format: {format}", format=args.format))

            response = scraper.send_chat_message(
                url=args.url,
                message=args.message,
                chat_selector=args.selector,
                submit_selector=args.button,
                wait_time=args.wait,
                debug=args.debug,
                use_deep_research=args.deep
            )

            if response:
                print(get_message("response_retrieved", default="Response retrieved"))
            else:
                print(get_message("response_retrieval_failed", default="Failed to retrieve response"))

        finally:
            # ブラウザを閉じる
            # Close the browser
            scraper.close()
if __name__ == "__main__":
    main()

# 使用例:
# チャットモード (Chat mode):
# python -m deepwiki_to_md.test_chat --url "https://deepwiki.com/yuyu1815/deepwiki_to_md" --message "こんにちは" --wait 10 --debug
# python -m deepwiki_to_md.test_chat --url "https://deepwiki.com/yuyu1815/deepwiki_to_md" --message "詳細な説明をお願いします" --wait 15 --deep --debug
# python -m deepwiki_to_md.test_chat --url "https://deepwiki.com/yuyu1815/deepwiki_to_md" --message "こんにちは" --format "md" --wait 10 --debug
# python -m deepwiki_to_md.test_chat --url "https://deepwiki.com/yuyu1815/deepwiki_to_md" --message "詳細な説明をお願いします" --format "yaml" --wait 15 --debug
# python -m deepwiki_to_md.test_chat --url "https://deepwiki.com/yuyu1815/deepwiki_to_md" --message "詳細な説明をお願いします" --format "html,md,yaml" --wait 15 --deep --debug
#
# 変換モード (Convert mode):
# python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md"
# python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
#
# 注意: ボタンセレクタの指定について
# --button オプションでボタンのCSSセレクタを指定できますが、より確実にクリックするために
# スクリプトはまずフォーム内のボタンを探し、見つからない場合のみ指定されたセレクタを使用します。
# 
# Note: About button selector specification
# You can specify the CSS selector for the button with the --button option, but for more reliable clicking,
# the script first looks for buttons within the form, and only uses the specified selector if none are found.
