import json
import locale
import os
from typing import Dict, Any

# Default language is English
DEFAULT_LANGUAGE = 'en_us'

# Dictionary of supported languages
SUPPORTED_LANGUAGES = {
    'ja_JP': 'ja_jp',
    'ja': 'ja_jp',
    'en_US': 'en_us',
    'en': 'en_us',
}


# Load messages from JSON files
def load_messages() -> Dict[str, Dict[str, str]]:
    """
    Load message dictionaries from JSON files in the lang folder.

    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping language codes to message dictionaries
    """
    messages = {}

    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_dir = os.path.join(current_dir, 'lang')

    # Load English messages (default)
    en_path = os.path.join(lang_dir, 'en_us.json')
    try:
        with open(en_path, 'r', encoding='utf-8') as f:
            messages['en_us'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load English messages: {e}")
        messages['en_us'] = {}

    # Load Japanese messages
    ja_path = os.path.join(lang_dir, 'ja_jp.json')
    try:
        with open(ja_path, 'r', encoding='utf-8') as f:
            messages['ja_jp'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load Japanese messages: {e}")
        messages['ja_jp'] = {}

    return messages


# Dictionary of messages by language code
MESSAGES: Dict[str, Dict[str, str]] = load_messages()


def get_system_language() -> str:
    """
    Detect the system language and return the corresponding language code.

    Returns:
        str: Language code (e.g., 'en_us', 'ja_jp')
    """
    try:
        # Get the system's language setting
        system_lang, _ = locale.getdefaultlocale()

        # If system_lang is None, default to English
        if system_lang is None:
            return DEFAULT_LANGUAGE

        # Check if the system language is supported
        for lang_code, normalized_code in SUPPORTED_LANGUAGES.items():
            if system_lang.lower().startswith(lang_code.lower()):
                return normalized_code

        # Default to English if the system language is not supported
        return DEFAULT_LANGUAGE
    except Exception:
        # In case of any error, default to English
        return DEFAULT_LANGUAGE


def get_message(key: str, **kwargs: Any) -> str:
    """
    Get a localized message by key, with optional format arguments.

    Args:
        key (str): The message key
        **kwargs: Format arguments for the message

    Returns:
        str: The localized message
    """
    # Get the current language
    lang = get_system_language()

    # Get the messages for the current language
    messages = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE])

    # Get the message by key, or fall back to the key itself if not found
    message = messages.get(key, key)

    # Format the message with the provided arguments
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            # If formatting fails, return the unformatted message
            return message

    return message
