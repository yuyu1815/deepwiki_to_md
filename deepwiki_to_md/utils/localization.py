"""
Localization Utilities for DeepWiki to Markdown Converter

This module provides localization utility functions for the DeepWiki to Markdown converter.
"""

import os
import logging
import locale
import json
from typing import Dict, Any, Optional

from deepwiki_to_md.utils.file_io import read_json_file

logger = logging.getLogger(__name__)

# Default language
DEFAULT_LANGUAGE = "en"

# Current language
_current_language = None

# Messages cache
_messages: Dict[str, Dict[str, str]] = {}


def _get_locale_dir() -> str:
    """
    Get the directory containing locale files.

    Returns:
        str: Path to the locale directory
    """
    # Get the package directory
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(package_dir, "locales")


def _load_messages(language: str) -> Dict[str, str]:
    """
    Load messages for the specified language.

    Args:
        language (str): Language code (e.g., "en", "ja")

    Returns:
        Dict[str, str]: Dictionary of messages
    """
    # Check if messages are already loaded
    if language in _messages:
        return _messages[language]

    # Load messages from file
    locale_dir = _get_locale_dir()
    locale_file = os.path.join(locale_dir, f"{language}.json")

    messages = read_json_file(locale_file)

    if not messages:
        # If messages couldn't be loaded, try the default language
        if language != DEFAULT_LANGUAGE:
            logger.warning(f"Could not load messages for language '{language}'. Falling back to '{DEFAULT_LANGUAGE}'.")
            return _load_messages(DEFAULT_LANGUAGE)
        else:
            # If default language couldn't be loaded, use empty dictionary
            logger.error(f"Could not load messages for default language '{DEFAULT_LANGUAGE}'.")
            messages = {}

    # Cache messages
    _messages[language] = messages

    return messages


def set_language(language: str) -> None:
    """
    Set the current language.

    Args:
        language (str): Language code (e.g., "en", "ja")
    """
    global _current_language
    _current_language = language
    logger.debug(f"Set language to '{language}'")


def get_current_language() -> str:
    """
    Get the current language.

    Returns:
        str: Current language code
    """
    global _current_language

    # If language is not set, try to detect it
    if _current_language is None:
        try:
            # Try to get the system language
            system_locale = locale.getlocale()[0]
            if system_locale:
                language = system_locale.split('_')[0]

                # Check if we have messages for this language
                locale_dir = _get_locale_dir()
                locale_file = os.path.join(locale_dir, f"{language}.json")

                if os.path.exists(locale_file):
                    _current_language = language
                    logger.debug(f"Detected language: '{language}'")
                else:
                    _current_language = DEFAULT_LANGUAGE
                    logger.debug(f"No messages for detected language '{language}'. Using default: '{DEFAULT_LANGUAGE}'")
            else:
                _current_language = DEFAULT_LANGUAGE
                logger.debug(f"Could not detect system language. Using default: '{DEFAULT_LANGUAGE}'")
        except Exception as e:
            _current_language = DEFAULT_LANGUAGE
            logger.error(f"Error detecting language: {str(e)}. Using default: '{DEFAULT_LANGUAGE}'")

    return _current_language


def get_localized_message(key: str, **kwargs) -> str:
    """
    Get a localized message.

    Args:
        key (str): Message key
        **kwargs: Format parameters for the message

    Returns:
        str: Localized message
    """
    language = get_current_language()
    messages = _load_messages(language)

    # Get message for the key
    message = messages.get(key)

    # If message is not found, try the default language
    if message is None and language != DEFAULT_LANGUAGE:
        messages = _load_messages(DEFAULT_LANGUAGE)
        message = messages.get(key)

    # If message is still not found, use the key
    if message is None:
        logger.warning(f"No message found for key '{key}' in any language.")
        message = key

    # Format the message with parameters
    try:
        if kwargs:
            message = message.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing parameter for message '{key}': {str(e)}")
    except Exception as e:
        logger.error(f"Error formatting message '{key}': {str(e)}")

    return message
