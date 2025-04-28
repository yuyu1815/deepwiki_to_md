import argparse
import sys

import requests

from .deepwiki_to_md import DeepwikiScraper


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Scrape deepwiki and convert to Markdown.')

    parser.add_argument('--library', '-l', action='append', nargs=2, metavar=('NAME', 'URL'),
                        help='Library name and URL to scrape. Can be specified multiple times.')

    parser.add_argument('--output-dir', '-o', default='Documents',
                        help='Output directory for Markdown files (default: Documents)')

    parser.add_argument('--use-direct-scraper', action='store_true',
                        help='Use DirectDeepwikiScraper after dynamic page loading (default: True)')

    parser.add_argument('--no-direct-scraper', action='store_true',
                        help='Disable DirectDeepwikiScraper after dynamic page loading')

    parser.add_argument('--use-alternative-scraper', action='store_true',
                        help='Use scrape_deepwiki from direct_scraper.py for pages without navigation items (default: True)')

    parser.add_argument('--no-alternative-scraper', action='store_true',
                        help='Disable scrape_deepwiki from direct_scraper.py for pages without navigation items')

    # Selenium-related arguments removed - only static requests are supported

    parser.add_argument('library_url', nargs='?',
                        help='URL of the library to scrape (alternative to --library)')

    args = parser.parse_args()

    # Handle the case where a library URL is provided as a positional argument
    if args.library_url and not args.library:
        # Extract library name from URL path
        from urllib.parse import urlparse
        path = urlparse(args.library_url).path.strip('/')
        library_name = path.split('/')[-1] if path else 'library'
        args.library = [(library_name, args.library_url)]

    # Validate arguments
    if not args.library and not args.library_url:
        parser.error("Either a library URL or at least one library must be specified using --library")

    return args


def main():
    """Main function to run the scraper."""
    args = parse_arguments()

    # Format libraries as expected by DeepwikiScraper
    libraries = [
        {"name": name, "url": url}
        for name, url in args.library
    ]

    # Determine whether to use DirectDeepwikiScraper
    use_direct_scraper = not args.no_direct_scraper

    # Determine whether to use alternative scraper
    use_alternative_scraper = not args.no_alternative_scraper

    # Create and run the scraper
    scraper = DeepwikiScraper(
        output_dir=args.output_dir,
        use_direct_scraper=use_direct_scraper,
        use_alternative_scraper=use_alternative_scraper
    )

    try:
        scraper.run(libraries)
        print(f"Scraping completed successfully. Markdown files saved to {args.output_dir}")
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
