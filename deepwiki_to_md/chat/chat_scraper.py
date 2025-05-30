"""
Chat Scraper Module for DeepWiki to Markdown Converter

This module provides functionality for scraping chat content using Selenium.
"""

import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from deepwiki_to_md.converters.html_to_md import convert_html_to_markdown

logger = logging.getLogger(__name__)


class ChatScraperSelenium:
    """
    A class for scraping chat content using Selenium.
    
    This class provides functionality to interact with chat interfaces,
    send messages, and extract responses in various formats.
    """

    def __init__(self, output_dir: str = "chat_output", headless: bool = True,
                 output_format: str = "html"):
        """
        Initialize the ChatScraperSelenium.
        
        Args:
            output_dir: Directory to save output files
            headless: Whether to run the browser in headless mode
            output_format: Output format(s) separated by commas (html,md,yaml)
        """
        self.output_dir = output_dir
        self.headless = headless
        self.output_formats = [fmt.strip().lower() for fmt in output_format.split(',')]
        self.driver = None

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize the webdriver
        self._init_webdriver()

    def _init_webdriver(self):
        """Initialize the Selenium WebDriver."""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            self.driver = webdriver.Chrome(options=options)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def send_chat_message(self, url: str, message: str,
                          chat_selector: str = "textarea",
                          submit_selector: str = "button",
                          response_selector: str = ".prose-custom",
                          wait_time: int = 30,
                          debug: bool = False) -> str:
        """
        Send a message to the chat interface and get the response.
        
        Args:
            url: URL of the chat interface
            message: Message to send
            chat_selector: CSS selector for the chat input element
            submit_selector: CSS selector for the submit button
            response_selector: CSS selector for the response element
            wait_time: Maximum time to wait for a response (seconds)
            debug: Whether to print debug information
            
        Returns:
            The HTML content of the response
        """
        try:
            # Navigate to the URL
            logger.info(f"Navigating to {url}")
            self.driver.get(url)

            # Wait for the chat input to be available
            logger.info("Waiting for chat input element")
            chat_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, chat_selector))
            )

            # Enter the message
            logger.info(f"Entering message: {message}")
            chat_input.send_keys(message)

            # Find and click the submit button
            logger.info("Clicking submit button")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
            submit_button.click()

            # Wait for the response
            logger.info(f"Waiting for response (max {wait_time} seconds)")
            response_element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, response_selector))
            )

            # Extract the response HTML
            response_html = self._extract_response_html(response_element)

            # Save the response in the requested formats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"{timestamp}_{message.replace(' ', '_')[:30]}"

            for fmt in self.output_formats:
                if fmt == 'html':
                    self._save_html(response_html, filename_base)
                elif fmt == 'md':
                    markdown = self._html_to_markdown(response_html)
                    self._save_markdown(markdown, filename_base)
                elif fmt == 'yaml':
                    yaml = self._html_to_yaml(response_html)
                    self._save_yaml(yaml, filename_base)

            return response_html

        except TimeoutException:
            logger.error(f"Timeout waiting for response after {wait_time} seconds")
            raise
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            raise

    def _extract_response_html(self, response_element) -> str:
        """
        Extract the HTML content from the response element.
        
        Args:
            response_element: The Selenium WebElement containing the response
            
        Returns:
            The HTML content as a string
        """
        try:
            # Try to get the innerHTML attribute
            html_content = response_element.get_attribute('innerHTML')
            if html_content:
                return html_content

            # Fallback to outerHTML if innerHTML is empty
            return response_element.get_attribute('outerHTML')
        except Exception as e:
            logger.error(f"Error extracting HTML content: {str(e)}")
            return ""

    def _html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to Markdown.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Markdown content
        """
        try:
            return convert_html_to_markdown(html_content)
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            return ""

    def _html_to_yaml(self, html_content: str) -> str:
        """
        Convert HTML content to YAML.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            YAML content
        """
        try:
            # Extract title from h1 tag if present
            import re
            title_match = re.search(r'<h1>(.*?)</h1>', html_content)
            title = title_match.group(1) if title_match else "Chat Response"

            # Convert HTML to markdown first
            markdown = self._html_to_markdown(html_content)

            # Create a simple YAML representation
            yaml_content = f"title: {title}\ncontent: |\n"
            for line in markdown.split('\n'):
                yaml_content += f"  {line}\n"

            return yaml_content
        except Exception as e:
            logger.error(f"Error converting HTML to YAML: {str(e)}")
            return ""

    def _save_html(self, content: str, filename_base: str):
        """Save content as HTML file."""
        filepath = os.path.join(self.output_dir, f"{filename_base}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved HTML to {filepath}")

    def _save_markdown(self, content: str, filename_base: str):
        """Save content as Markdown file."""
        filepath = os.path.join(self.output_dir, f"{filename_base}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved Markdown to {filepath}")

    def _save_yaml(self, content: str, filename_base: str):
        """Save content as YAML file."""
        filepath = os.path.join(self.output_dir, f"{filename_base}.yaml")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved YAML to {filepath}")

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")

    def __enter__(self):
        """Support for context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self.close()
