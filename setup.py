from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deepwiki-to-md",
    version="0.1.0",
    author="Original Author",
    author_email="author@example.com",
    description="A Python tool to scrape content from deepwiki sites and convert it to Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deepwiki_to_md",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
    ],
    entry_points={
        "console_scripts": [
            "deepwiki-to-md=deepwiki_to_md.run_scraper:main",
        ],
    },
)
