"""
Configuration Model for DeepWiki to Markdown Converter

This module provides the configuration data model for the DeepWiki to Markdown converter.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Config:
    """
    Configuration settings for the DeepWiki to Markdown converter.
    
    This class stores configuration settings for the scraper, converter, and other components.
    """

    # Required settings
    url: str
    library_name: str

    # Optional settings with defaults
    output_dir: str = "./output"
    verbose: bool = False
    max_depth: int = 5
    timeout: int = 30

    # Advanced settings
    headers: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 3
    retry_delay: int = 2

    def __post_init__(self):
        """
        Validate and normalize configuration after initialization.
        """
        # Normalize URL (ensure it ends with a slash)
        if not self.url.endswith('/'):
            self.url = f"{self.url}/"

        # Normalize output directory (convert to absolute path)
        self.output_dir = os.path.abspath(self.output_dir)

        # Set default User-Agent if not provided
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = (
                "DeepWiki-to-MD/0.3.2 "
                "(https://github.com/yuyu1815/deepwiki_to_md)"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the configuration
        """
        return {
            "url": self.url,
            "library_name": self.library_name,
            "output_dir": self.output_dir,
            "verbose": self.verbose,
            "max_depth": self.max_depth,
            "timeout": self.timeout,
            "headers": self.headers,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        Create a configuration from a dictionary.
        
        Args:
            config_dict (Dict[str, Any]): Dictionary containing configuration settings
            
        Returns:
            Config: Configuration object
        """
        return cls(**config_dict)

    def __str__(self) -> str:
        """
        Get a string representation of the configuration.
        
        Returns:
            str: String representation of the configuration
        """
        return (
            f"Config(url='{self.url}', "
            f"library_name='{self.library_name}', "
            f"output_dir='{self.output_dir}')"
        )
