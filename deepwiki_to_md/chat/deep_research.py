"""
Deep Research Mode for DeepWiki to Markdown Converter

This module provides functionality for conducting deep research using the DeepWiki chat.
"""

import logging
import time
import os
from typing import Dict, List, Optional, Any, Union
import json

from deepwiki_to_md.models.config import Config
from deepwiki_to_md.chat.chat_interface import ChatInterface
from deepwiki_to_md.utils.file_io import save_markdown_file, save_json_file, save_yaml_file
from deepwiki_to_md.converters.md_to_yaml import convert_markdown_to_yaml, yaml_to_string

logger = logging.getLogger(__name__)


class DeepResearchMode:
    """
    Deep Research Mode for the DeepWiki chat.
    
    This class provides methods for conducting deep research using the DeepWiki chat,
    including multi-turn conversations and saving results in various formats.
    """

    def __init__(self, config: Config):
        """
        Initialize the deep research mode.
        
        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.chat = None
        self.conversation_history = []
        self.research_results = []

        logger.debug("Initialized DeepResearchMode")

    def __enter__(self):
        """
        Enter context manager.
        
        Returns:
            DeepResearchMode: Self
        """
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.end_session()

    def start_session(self) -> bool:
        """
        Start a deep research session.
        
        Returns:
            bool: True if session started successfully, False otherwise
        """
        try:
            # Initialize chat interface
            self.chat = ChatInterface(self.config)
            success = self.chat.connect()

            if success:
                logger.info("Started deep research session")

                # Send initial system message if configured
                system_prompt = self.config.get('system_prompt')
                if system_prompt:
                    self._add_to_history("system", system_prompt)
                    logger.debug(f"Set system prompt: {system_prompt}")

            return success

        except Exception as e:
            logger.error(f"Error starting deep research session: {str(e)}")
            return False

    def end_session(self) -> None:
        """
        End the deep research session.
        """
        try:
            if self.chat:
                self.chat.disconnect()
                self.chat = None

            logger.info("Ended deep research session")

        except Exception as e:
            logger.error(f"Error ending deep research session: {str(e)}")

    def ask_question(self, question: str, timeout: int = 120) -> Optional[str]:
        """
        Ask a question in the deep research session.
        
        Args:
            question (str): Question to ask
            timeout (int): Maximum time to wait for a response in seconds
            
        Returns:
            Optional[str]: Response text or None if no response received
        """
        if not self.chat:
            logger.error("No active chat session")
            return None

        try:
            # Send the question
            logger.info(f"Asking question: {question}")
            self._add_to_history("user", question)

            if not self.chat.send_message(question):
                logger.error("Failed to send question")
                return None

            # Get the response
            response = self.chat.get_response(timeout)

            if response:
                logger.info("Received response")
                self._add_to_history("assistant", response)
                self.research_results.append({
                    "question": question,
                    "response": response
                })
            else:
                logger.warning("No response received")

            return response

        except Exception as e:
            logger.error(f"Error asking question: {str(e)}")
            return None

    def conduct_research(self, questions: List[str], timeout: int = 120) -> List[Dict[str, str]]:
        """
        Conduct research by asking a series of questions.
        
        Args:
            questions (List[str]): List of questions to ask
            timeout (int): Maximum time to wait for each response in seconds
            
        Returns:
            List[Dict[str, str]]: List of question-response pairs
        """
        results = []

        for i, question in enumerate(questions):
            logger.info(f"Research question {i + 1}/{len(questions)}")

            response = self.ask_question(question, timeout)

            if response:
                results.append({
                    "question": question,
                    "response": response
                })

            # Wait between questions to avoid rate limiting
            if i < len(questions) - 1:
                time.sleep(2)

        return results

    def save_results(self, output_dir: str, formats: List[str] = ["md", "json", "yaml"]) -> Dict[str, List[str]]:
        """
        Save research results in various formats.
        
        Args:
            output_dir (str): Directory to save results in
            formats (List[str]): List of formats to save results in (md, json, yaml)
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping format to list of saved file paths
        """
        saved_files = {fmt: [] for fmt in formats}

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save each result
        for i, result in enumerate(self.research_results):
            question = result["question"]
            response = result["response"]

            # Create a filename based on the question
            base_filename = self._create_filename(question, i)

            # Save in each requested format
            for fmt in formats:
                if fmt.lower() == "md":
                    # Save as Markdown
                    filename = f"{base_filename}.md"
                    filepath = os.path.join(output_dir, filename)

                    content = f"# {question}\n\n{response}"
                    if save_markdown_file(filepath, content):
                        saved_files["md"].append(filepath)

                elif fmt.lower() == "json":
                    # Save as JSON
                    filename = f"{base_filename}.json"
                    filepath = os.path.join(output_dir, filename)

                    if save_json_file(filepath, result):
                        saved_files["json"].append(filepath)

                elif fmt.lower() == "yaml":
                    # Save as YAML
                    filename = f"{base_filename}.yaml"
                    filepath = os.path.join(output_dir, filename)

                    # Convert to YAML structure
                    yaml_data = convert_markdown_to_yaml(
                        response,
                        title=question,
                        include_raw_content=True
                    )

                    # Convert to YAML string and save
                    yaml_str = yaml_to_string(yaml_data)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(yaml_str)

                    saved_files["yaml"].append(filepath)

        # Save conversation history
        if self.conversation_history:
            history_file = os.path.join(output_dir, "conversation_history.json")
            save_json_file(history_file, {"history": self.conversation_history})

        return saved_files

    def _add_to_history(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role (str): Role of the message sender (user, assistant, system)
            content (str): Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

    def _create_filename(self, question: str, index: int) -> str:
        """
        Create a filename based on a question.
        
        Args:
            question (str): Question to create filename from
            index (int): Index of the question
            
        Returns:
            str: Sanitized filename
        """
        # Truncate and sanitize the question for use as a filename
        sanitized = "".join(c if c.isalnum() or c in " -_" else "_" for c in question)
        sanitized = sanitized.strip()

        # Truncate if too long
        if len(sanitized) > 50:
            sanitized = sanitized[:47] + "..."

        # Add index to ensure uniqueness
        return f"{index + 1:02d}_{sanitized}"


def conduct_research(
        config: Config,
        questions: List[str],
        output_dir: Optional[str] = None,
        formats: List[str] = ["md", "json", "yaml"],
        timeout: int = 120
) -> Dict[str, Any]:
    """
    Conduct deep research and save results.
    
    Args:
        config (Config): Configuration object
        questions (List[str]): List of questions to ask
        output_dir (Optional[str]): Directory to save results in
        formats (List[str]): List of formats to save results in
        timeout (int): Maximum time to wait for each response in seconds
        
    Returns:
        Dict[str, Any]: Research results and saved file information
    """
    with DeepResearchMode(config) as research:
        # Conduct research
        results = research.conduct_research(questions, timeout)

        # Save results if output directory is provided
        saved_files = {}
        if output_dir:
            saved_files = research.save_results(output_dir, formats)

        return {
            "results": results,
            "saved_files": saved_files
        }
