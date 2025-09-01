#!/usr/bin/env python3
"""
Setup script for deepwiki-to-md package.

This package is designed with zero external dependencies for maximum portability
and minimal maintenance overhead.
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Ensure we're using Python 3.7+
if sys.version_info < (3, 7):
    print("ERROR: deepwiki-to-md requires Python 3.7 or later.")
    print(f"You are using Python {sys.version}")
    sys.exit(1)

# Get the long description from README
here = Path(__file__).parent.parent  # Go up one level from src/
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read version from package
def get_version():
    """Get version from deepwiki_to_md package."""
    try:
        # Try to read from __init__.py
        init_file = here / "src" / "deepwiki_to_md" / "__init__.py"
        if init_file.exists():
            content = init_file.read_text(encoding="utf-8")
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    return line.split('"')[1]
        
        # Fallback to default version
        return "2.0.0"
    except Exception:
        return "2.0.0"

# Get requirements (should be empty for zero-dependency design)
def get_requirements():
    """Get runtime requirements (intentionally empty)."""
    req_file = here / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        # Filter out comments and empty lines
        requirements = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements
    return []

def get_dev_requirements():
    """Get development requirements."""
    req_file = here / "requirements-dev.txt" 
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        requirements = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements
    return []

setup(
    # Basic package information
    name="deepwiki-to-md",
    version=get_version(),
    description="Zero-dependency Next.js/DeepWiki content extractor with pluggable strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Author and contact information
    author="DeepWiki Content Extractor Team",
    author_email="contact@example.com",  # Update with actual contact
    maintainer="DeepWiki Content Extractor Team",
    maintainer_email="contact@example.com",
    
    # URLs and links
    url="https://github.com/yuyu1815/deepwiki_to_md",
    project_urls={
        "Bug Tracker": "https://github.com/yuyu1815/deepwiki_to_md/issues",
        "Documentation": "https://github.com/yuyu1815/deepwiki_to_md/blob/main/README.md",
        "Source Code": "https://github.com/yuyu1815/deepwiki_to_md",
        "Changelog": "https://github.com/yuyu1815/deepwiki_to_md/blob/main/CHANGELOG.md",
    },
    
    # Package discovery and structure
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    package_dir={"": "."},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "deepwiki_to_md": [
            "py.typed",  # PEP 561 marker for type information
        ],
        "config": [
            "*.yaml", 
            "*.yml",
        ],
        "docs": [
            "*.md",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Dependencies (intentionally minimal/empty)
    install_requires=get_requirements(),
    
    # Optional dependencies for enhanced functionality
    extras_require={
        "dev": get_dev_requirements(),
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
        ],
        # Optional enhancements (not required for core functionality)
        "enhanced": [
            "brotli>=1.0.0",        # Brotli decompression
            "chardet>=5.0.0",       # Character encoding detection
        ],
    },
    
    # Entry points for command-line tools
    entry_points={
        "console_scripts": [
            "deepwiki-to-md=html_formatter:main",
            "html-formatter=html_formatter:main",  # Legacy alias
            "url-check=deepwiki_to_md.url_check_cli:main",
            "md-scraper=deepwiki_to_md.direct_md_scraper:main",
        ],
    },
    
    # Classification and metadata
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
        # Topic and Purpose
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        
        # Natural Language
        "Natural Language :: English",
        "Natural Language :: Japanese",
    ],
    
    # Keywords for discovery
    keywords=[
        "markdown", "html", "nextjs", "content-extraction", 
        "web-scraping", "deepwiki", "zero-dependency",
        "cli-tool", "content-converter", "documentation",
    ],
    
    # Testing
    test_suite="tests",
    
    # Zip safety
    zip_safe=False,
    
    # Platform compatibility
    platforms=["any"],
    
    # License
    license="MIT",
    
    # Additional options
    options={
        "build": {
            "build_base": "build",
        },
        "egg_info": {
            "egg_base": ".",
        },
    },
)

# Post-installation message
def print_installation_message():
    """Print helpful message after installation."""
    print("\n" + "="*60)
    print("🎉 deepwiki-to-md installed successfully!")
    print("="*60)
    print("\nQuick start:")
    print("  deepwiki-to-md --to-md https://deepwiki.com/example")
    print("  url-check --url https://example.com")
    print("  md-scraper --help")
    print("\nDocumentation:")
    print("  https://github.com/yuyu1815/deepwiki_to_md/blob/main/README.md")
    print("\nZero dependencies! 🚀 Pure Python stdlib implementation.")
    print("="*60 + "\n")

# Run post-install message if being installed
if __name__ == "__main__" and "install" in sys.argv:
    print_installation_message()