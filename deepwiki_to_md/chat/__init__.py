"""
Chat Module for DeepWiki to Markdown Converter

This module provides functionality for interacting with the DeepWiki chat interface.
"""

from deepwiki_to_md.chat.chat_interface import ChatInterface, send_message, get_response
from deepwiki_to_md.chat.deep_research import DeepResearchMode, conduct_research

__all__ = [
    "ChatInterface", "send_message", "get_response",
    "DeepResearchMode", "conduct_research"
]
