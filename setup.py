from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deepwiki-to-md",
    version="0.2.0",
    author="yuzumican",
    author_email="author@example.com",
    description="A Python tool to scrape content from deepwiki sites and convert it to Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuyu1815/deepwiki_to_md",
    packages=find_packages(),
    license="MIT",
    license_expression="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.3",
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "deepwiki-to-md=deepwiki_to_md.run_scraper:main",
            "deepwiki-create=deepwiki_to_md.create:main",
            "deepwiki-chat=deepwiki_to_md.chat:main",
        ],
    },
)
