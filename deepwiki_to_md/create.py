import argparse
import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from deepwiki_to_md.localization import get_message

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RepositoryCreator:
    """
    リポジトリの作成依頼を行うクラス
    Class for creating repository requests
    """

    def __init__(self, headless=False):
        """
        Initialize the RepositoryCreator.

        Args:
            headless (bool): Whether to run the browser in headless mode.
        """
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def create(self, url, email):
        """
        Set email and submit repository creation request.

        Args:
            url (str): The URL of the repository creation page.
            email (str): The email to notify.

        Returns:
            bool: True if the request was submitted successfully, False otherwise.
        """
        try:
            logger.info(get_message("accessing_url", url=url))
            self.driver.get(url)

            # メールアドレス入力フィールドを待機して取得
            # Wait for and get the email input field
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )

            # メールアドレスを入力
            # Enter the email address
            email_input.clear()
            email_input.send_keys(email)
            logger.info(get_message("email_entered", email=email))

            # 送信ボタンを探してクリック
            # Find and click the submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )

            # ボタンをクリック
            # Click the button
            submit_button.click()
            logger.info(get_message("submit_button_clicked"))

            # 成功メッセージまたは次のページへの遷移を待機
            # Wait for success message or transition to next page
            try:
                success_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".success-message"))  # 実際のセレクターに置き換えてください
                )
                return True
            except TimeoutException:
                logger.error(get_message("error", error=get_message("success_message_wait_failed")))
                return False

        except Exception as e:
            logger.error(get_message("error", error=str(e)))
            return False

    def close(self):
        """
        Close the browser.
        """
        self.driver.quit()


def parse_arguments():
    """
    コマンドライン引数を解析する
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description=get_message("repo_creation_description"))

    parser.add_argument("--url", required=True,
                        help=get_message("repo_url_help"))
    parser.add_argument("--email", required=True,
                        help=get_message("repo_email_help"))
    parser.add_argument("--headless", action="store_true",
                        help=get_message("headless_mode_help"))

    return parser.parse_args()


def main():
    """
    メイン関数 - コマンドラインからの実行用エントリーポイント
    Main function - Entry point for command-line execution
    """
    # コマンドライン引数を解析
    # Parse command line arguments
    args = parse_arguments()

    # リポジトリ作成リクエスタを初期化
    # Initialize the repository creator
    creator = RepositoryCreator(headless=args.headless)

    try:
        # リポジトリ作成リクエストを送信
        # Send repository creation request
        print(get_message("accessing_url", url=args.url))
        print(get_message("email_info", email=args.email))

        success = creator.create(url=args.url, email=args.email)

        if success:
            print(get_message("repo_request_sent"))
            return 0
        else:
            print(get_message("repo_request_failed"))
            return 1

    finally:
        # ブラウザを閉じる
        # Close the browser
        creator.close()


if __name__ == "__main__":
    main()

# 使用例:
# python -m deepwiki_to_md.create --url "https://example.com/repository/create" --email "user@example.com"
# python -m deepwiki_to_md.create --url "https://example.com/repository/create" --email "user@example.com" --headless
