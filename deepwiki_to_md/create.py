import argparse
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
            logger.info(f"URLにアクセス中: {url}")
            logger.info(f"Accessing URL: {url}")
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
            logger.info(f"メールアドレス入力: {email}")
            logger.info(f"Email entered: {email}")

            # 送信ボタンを探してクリック
            # Find and click the submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )

            # ボタンをクリック
            # Click the button
            submit_button.click()
            logger.info("送信ボタンをクリック")
            logger.info("Submit button clicked")

            # 成功メッセージまたは次のページへの遷移を待機
            # Wait for success message or transition to next page
            time.sleep(3)

            return True

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            logger.error(f"An error occurred: {e}")
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
    parser = argparse.ArgumentParser(description="Repository Creation Request")

    parser.add_argument("--url", required=True,
                        help="リポジトリ作成ページのURL (URL of the repository creation page)")
    parser.add_argument("--email", required=True,
                        help="通知先メールアドレス (Email to notify)")
    parser.add_argument("--headless", action="store_true",
                        help="ヘッドレスモードを有効にする (Enable headless mode)")

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
        print(f"URLにアクセス中: {args.url}")
        print(f"Accessing URL: {args.url}")
        print(f"メールアドレス: {args.email}")
        print(f"Email: {args.email}")

        success = creator.create(url=args.url, email=args.email)

        if success:
            print("リポジトリ作成リクエストを送信しました")
            print("Repository creation request sent")
            return 0
        else:
            print("リポジトリ作成リクエストの送信に失敗しました")
            print("Failed to send repository creation request")
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
