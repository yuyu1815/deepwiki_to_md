"""
Content Model for DeepWiki to Markdown Converter

This module provides the content data model for the DeepWiki to Markdown converter.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import datetime


@dataclass
class Content:
    """
    Content data model for storing scraped content.
    
    This class stores the content scraped from DeepWiki sites, including metadata.
    """

    # Required fields
    title: str
    content: str
    url: str

    # Optional fields with defaults
    library: str = ""
    file_path: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    navigation: List[Dict[str, str]] = field(default_factory=list)

    # Timestamps
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: Optional[datetime.datetime] = None

    def __post_init__(self):
        """
        Initialize additional fields after creation.
        """
        # Set updated_at to created_at initially
        if self.updated_at is None:
            self.updated_at = self.created_at

    def update_content(self, new_content: str) -> None:
        """
        Update the content and update timestamp.
        
        Args:
            new_content (str): New content to set
        """
        self.content = new_content
        self.updated_at = datetime.datetime.now()

    def add_navigation_item(self, title: str, url: str) -> None:
        """
        Add a navigation item.
        
        Args:
            title (str): Title of the navigation item
            url (str): URL of the navigation item
        """
        self.navigation.append({"title": title, "url": url})

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the content to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the content
        """
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "library": self.library,
            "file_path": self.file_path,
            "metadata": self.metadata,
            "navigation": self.navigation,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, content_dict: Dict[str, Any]) -> 'Content':
        """
        Create a content object from a dictionary.
        
        Args:
            content_dict (Dict[str, Any]): Dictionary containing content data
            
        Returns:
            Content: Content object
        """
        # Handle datetime fields
        if "created_at" in content_dict and isinstance(content_dict["created_at"], str):
            content_dict["created_at"] = datetime.datetime.fromisoformat(content_dict["created_at"])

        if "updated_at" in content_dict and isinstance(content_dict["updated_at"], str):
            content_dict["updated_at"] = datetime.datetime.fromisoformat(content_dict["updated_at"])

        return cls(**content_dict)

    def __str__(self) -> str:
        """
        Get a string representation of the content.
        
        Returns:
            str: String representation of the content
        """
        return f"Content(title='{self.title}', url='{self.url}', library='{self.library}')"
