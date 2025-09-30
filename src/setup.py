#!/usr/bin/env python3
"""
DeepWiki-to-MD パッケージのセットアップスクリプト。

このパッケージは外部依存ゼロを目指し、移植性と保守性を最大化しています。
"""

from setuptools import setup, find_packages
import sys
from pathlib import Path

# README から長い説明文を取得する / Get the long description from README
here = Path(__file__).parent.parent  # Go up one level from src/
long_description = (here / "README.md").read_text(encoding="utf-8")

# バージョン情報をパッケージから取得する / Read version from package
def get_version():
    """deepwiki_to_md パッケージからバージョンを取得する。"""
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

# 依存関係（ゼロ依存設計のため基本的に空）/ Get requirements (should be empty for zero-dependency design)
def get_requirements():
    """実行時の依存関係を取得する（基本的に空）。"""
    req_file = here / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        # コメント行と空行を除外する / Filter out comments and empty lines
        requirements = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements
    return []

def get_dev_requirements():
    """開発用の依存関係を取得する。"""
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
    # 基本的なパッケージ情報 / Basic package information
    name="deepwiki-to-md",
    version=get_version(),
    description="Zero-dependency Next.js/DeepWiki content extractor with pluggable strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # 著者と連絡先情報 / Author and contact information
    author="DeepWiki Content Extractor Team",
    author_email="contact@example.com",  # Update with actual contact
    maintainer="DeepWiki Content Extractor Team",
    maintainer_email="contact@example.com",
    
    # URL とリンク / URLs and links
    url="https://github.com/yuyu1815/deepwiki_to_md",
    project_urls={
        "Bug Tracker": "https://github.com/yuyu1815/deepwiki_to_md/issues",
        "Documentation": "https://github.com/yuyu1815/deepwiki_to_md/blob/main/README.md",
        "Source Code": "https://github.com/yuyu1815/deepwiki_to_md",
        "Changelog": "https://github.com/yuyu1815/deepwiki_to_md/blob/main/CHANGELOG.md",
    },
    
    # パッケージの検出と構成 / Package discovery and structure
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    package_dir={"": "."},
    
    # 非Pythonファイルを含める / Include non-Python files
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
    
    # 対応するPythonバージョンの要件 / Python version requirement
    python_requires=">=3.7",
    
    # 依存関係（意図的に最小/空）/ Dependencies (intentionally minimal/empty)
    install_requires=get_requirements(),
    
    # 機能拡張のためのオプション依存関係 / Optional dependencies for enhanced functionality
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
    
    # コマンドラインツールのエントリポイント / Entry points for command-line tools
    entry_points={
        "console_scripts": [
            "deepwiki-to-md=cli:main",
        ],
    },
    
    # 分類とメタデータ / Classification and metadata
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
    
    # 検索用キーワード / Keywords for discovery
    keywords=[
        "markdown", "html", "nextjs", "content-extraction", 
        "web-scraping", "deepwiki", "zero-dependency",
        "cli-tool", "content-converter", "documentation",
    ],
    
    # テスト設定 / Testing
    test_suite="tests",
    
    # Zip セーフティ / Zip safety
    zip_safe=False,
    
    # 対応プラットフォーム / Platform compatibility
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
    """インストール後に役立つメッセージを表示する。"""
    print("\n" + "="*60)
    print("🎉 deepwiki-to-md installed successfully!")
    print("="*60)
    print("\nQuick start:")
    print("  deepwiki-to-md https://deepwiki.com/path --path ./.deepwiki")
    print("  url-check --url https://example.com")
    print("  md-scraper --help")
    print("\nDocumentation:")
    print("  https://github.com/yuyu1815/deepwiki_to_md/blob/main/README.md")
    print("\nZero dependencies! 🚀 Pure Python stdlib implementation.")
    print("="*60 + "\n")

# Run post-install message if being installed
if __name__ == "__main__" and "install" in sys.argv:
    print_installation_message()