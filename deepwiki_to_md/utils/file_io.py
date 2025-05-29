"""
File I/O Utilities for DeepWiki to Markdown Converter

This module provides file I/O utility functions for the DeepWiki to Markdown converter.
"""

import os
import logging
from typing import Optional, Dict, Any
import json
import yaml

logger = logging.getLogger(__name__)


def save_markdown_file(file_path: str, content: str) -> bool:
    """
    Save content to a Markdown file.
    
    Args:
        file_path (str): Path to save the file
        content (str): Content to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Saved Markdown file: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving Markdown file {file_path}: {str(e)}")
        return False


def read_markdown_file(file_path: str) -> Optional[str]:
    """
    Read content from a Markdown file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Optional[str]: File content or None if an error occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.debug(f"Read Markdown file: {file_path}")
        return content

    except Exception as e:
        logger.error(f"Error reading Markdown file {file_path}: {str(e)}")
        return None


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        file_path (str): Path to save the file
        data (Dict[str, Any]): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"Saved JSON file: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False


def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Read data from a JSON file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Optional[Dict[str, Any]]: File data or None if an error occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.debug(f"Read JSON file: {file_path}")
        return data

    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {str(e)}")
        return None


def save_yaml_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a YAML file.
    
    Args:
        file_path (str): Path to save the file
        data (Dict[str, Any]): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        logger.debug(f"Saved YAML file: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving YAML file {file_path}: {str(e)}")
        return False


def read_yaml_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Read data from a YAML file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Optional[Dict[str, Any]]: File data or None if an error occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        logger.debug(f"Read YAML file: {file_path}")
        return data

    except Exception as e:
        logger.error(f"Error reading YAML file {file_path}: {str(e)}")
        return None
