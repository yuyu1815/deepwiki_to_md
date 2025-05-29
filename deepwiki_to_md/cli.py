"""
Command Line Interface for DeepWiki to Markdown Converter

This module provides the command-line interface for the DeepWiki to Markdown converter.
It parses command-line arguments and delegates to the appropriate functionality.
"""

import argparse
import logging
import sys
from typing import Dict, List, Optional, Any

from deepwiki_to_md.utils.error_handler import setup_error_handling
from deepwiki_to_md.utils.localization import get_localized_message
from deepwiki_to_md.scraper.deepwiki_scraper import DeepwikiScraper
from deepwiki_to_md.models.config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description=get_localized_message("cli_description")
    )

    parser.add_argument(
        "--url", "-u",
        type=str,
        help=get_localized_message("url_help"),
        required=True
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./output",
        help=get_localized_message("output_help")
    )

    parser.add_argument(
        "--library", "-l",
        type=str,
        help=get_localized_message("library_help"),
        required=True
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help=get_localized_message("verbose_help")
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Set up error handling
    setup_error_handling()

    try:
        # Parse arguments
        args = parse_args()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug(get_localized_message("verbose_mode_enabled"))

        # Create configuration
        config = Config(
            url=args.url,
            output_dir=args.output,
            library_name=args.library
        )

        # Initialize scraper
        scraper = DeepwikiScraper(config)

        # Run scraper
        result = scraper.scrape()

        # Log results
        logger.info(get_localized_message("scraping_complete", count=len(result)))

        return 0

    except Exception as e:
        logger.error(get_localized_message("unexpected_error", error=str(e)))
        if args.verbose:
            logger.exception(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
