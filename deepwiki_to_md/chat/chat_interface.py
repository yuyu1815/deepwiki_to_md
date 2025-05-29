"""
Chat Interface for DeepWiki to Markdown Converter

This module provides the interface for interacting with the DeepWiki chat.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from deepwiki_to_md.models.config import Config
from deepwiki_to_md.utils.error_handler import retry_on_exception, handle_request_error
from deepwiki_to_md.converters.html_to_md import convert_html_to_markdown

logger = logging.getLogger(__name__)


class ChatInterface:
    """
    Interface for interacting with the DeepWiki chat.

    This class provides methods for sending messages to the DeepWiki chat
    and receiving responses.
    """

    def __init__(self, config: Config):
        """
        Initialize the chat interface.

        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        self.conversation_id = None

        logger.debug("Initialized ChatInterface")

    def __enter__(self):
        """
        Enter context manager.

        Returns:
            ChatInterface: Self
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.disconnect()

    def connect(self) -> bool:
        """
        Connect to the DeepWiki chat.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Initialize Selenium WebDriver if needed
            if hasattr(self.config, 'use_selenium') and self.config.use_selenium:
                self._init_webdriver()

            # Create a new conversation
            self._create_conversation()

            logger.info("Connected to DeepWiki chat")
            return True

        except Exception as e:
            logger.error(f"Error connecting to DeepWiki chat: {str(e)}")
            return False

    def disconnect(self) -> None:
        """
        Disconnect from the DeepWiki chat.
        """
        try:
            # Close Selenium WebDriver if it was used
            if self.driver:
                self.driver.quit()
                self.driver = None

            logger.info("Disconnected from DeepWiki chat")

        except Exception as e:
            logger.error(f"Error disconnecting from DeepWiki chat: {str(e)}")

    def send_message(self, message: str) -> bool:
        """
        Send a message to the DeepWiki chat.

        Args:
            message (str): Message to send

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            if self.driver:
                return self._send_message_selenium(message)
            else:
                return self._send_message_api(message)

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    def get_response(self, timeout: int = 60) -> Optional[str]:
        """
        Get a response from the DeepWiki chat.

        Args:
            timeout (int): Maximum time to wait for a response in seconds

        Returns:
            Optional[str]: Response text or None if no response received
        """
        try:
            if self.driver:
                return self._get_response_selenium(timeout)
            else:
                return self._get_response_api(timeout)

        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return None

    def _init_webdriver(self) -> None:
        """
        Initialize Selenium WebDriver.
        """
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        # Set up Chrome options
        chrome_options = Options()
        if not hasattr(self.config, 'show_browser') or not self.config.show_browser:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the chat URL
        self.driver.get(self.config.url)

        # Wait for the page to load
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        logger.debug("Initialized Selenium WebDriver")

    def _create_conversation(self) -> None:
        """
        Create a new conversation.
        """
        if self.driver:
            # Selenium-based conversation creation
            # This is a placeholder - actual implementation would depend on the DeepWiki UI
            pass
        else:
            # API-based conversation creation
            url = f"{self.config.url}/api/conversation"
            data = {
                "model": getattr(self.config, 'library_name', 'default'),
                "messages": []
            }

            response = self.session.post(url=url, json=data)
            response.raise_for_status()

            result = response.json()
            self.conversation_id = result.get('conversation_id')

            if not self.conversation_id:
                raise ValueError("Failed to create conversation: No conversation ID returned")

    def _send_message_selenium(self, message: str) -> bool:
        """
        Send a message using Selenium.

        Args:
            message (str): Message to send

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            # Find the input field
            input_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "textarea[placeholder*='message'], input[placeholder*='message']"))
            )

            # Clear the input field
            input_field.clear()

            # Type the message
            input_field.send_keys(message)

            # Find and click the send button
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button.send-button"))
            )
            send_button.click()

            # Wait for the message to be sent
            time.sleep(1)

            return True

        except Exception as e:
            logger.error(f"Error sending message with Selenium: {str(e)}")
            return False

    @retry_on_exception
    def _send_message_api(self, message: str) -> bool:
        """
        Send a message using the API.

        Args:
            message (str): Message to send

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.conversation_id:
            raise ValueError("No active conversation")

        url = f"{self.config.url}/api/conversation/{self.conversation_id}/message"
        data = {
            "content": message,
            "role": "user"
        }

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            handle_request_error(e, url)
            raise

    def _get_response_selenium(self, timeout: int) -> Optional[str]:
        """
        Get a response using Selenium.

        Args:
            timeout (int): Maximum time to wait for a response in seconds

        Returns:
            Optional[str]: Response text or None if no response received
        """
        try:
            # Wait for the response to appear
            response_selector = "div.assistant-message, div.response-content"

            # Wait for the response to stop changing (indicating it's complete)
            last_response = None
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    # Wait for the response element to be present
                    response_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, response_selector))
                    )

                    # Get the current response text
                    current_response = response_element.get_attribute('innerHTML')

                    # If the response hasn't changed for 2 seconds, consider it complete
                    if current_response == last_response:
                        # Convert HTML to Markdown
                        return convert_html_to_markdown(current_response)

                    # Update last response
                    last_response = current_response

                    # Wait a bit before checking again
                    time.sleep(2)

                except TimeoutException:
                    # Response element not found yet, continue waiting
                    time.sleep(1)

            # Timeout reached
            logger.warning(f"Timeout reached while waiting for response")
            return last_response and convert_html_to_markdown(last_response)

        except Exception as e:
            logger.error(f"Error getting response with Selenium: {str(e)}")
            return None

    @retry_on_exception
    def _get_response_api(self, timeout: int) -> Optional[str]:
        """
        Get a response using the API.

        Args:
            timeout (int): Maximum time to wait for a response in seconds

        Returns:
            Optional[str]: Response text or None if no response received
        """
        if not self.conversation_id:
            raise ValueError("No active conversation")

        url = f"{self.config.url}/api/conversation/{self.conversation_id}/messages"

        start_time = time.time()
        last_message_id = None

        while time.time() - start_time < timeout:
            try:
                response = self.session.get(url)
                response.raise_for_status()

                messages = response.json().get('messages', [])

                # Find the latest assistant message
                for message in reversed(messages):
                    if message.get('role') == 'assistant':
                        message_id = message.get('id')

                        # If this is a new message or the message has been updated
                        if message_id != last_message_id:
                            last_message_id = message_id

                            # Check if the message is complete
                            if not message.get('is_incomplete', False):
                                return message.get('content', '')

                        break

                # Wait before checking again
                time.sleep(2)

            except requests.RequestException as e:
                handle_request_error(e, url)
                raise

        # Timeout reached
        logger.warning(f"Timeout reached while waiting for response")
        return None


def send_message(config: Config, message: str) -> bool:
    """
    Send a message to the DeepWiki chat.

    Args:
        config (Config): Configuration object
        message (str): Message to send

    Returns:
        bool: True if message sent successfully, False otherwise
    """
    with ChatInterface(config) as chat:
        return chat.send_message(message)


def get_response(config: Config, message: str, timeout: int = 60) -> Optional[str]:
    """
    Send a message and get a response from the DeepWiki chat.

    Args:
        config (Config): Configuration object
        message (str): Message to send
        timeout (int): Maximum time to wait for a response in seconds

    Returns:
        Optional[str]: Response text or None if no response received
    """
    with ChatInterface(config) as chat:
        if chat.send_message(message):
            return chat.get_response(timeout)
        return None
