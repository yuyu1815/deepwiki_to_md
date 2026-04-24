import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deepwiki.extraction.extractor import ContentExtractor
from deepwiki.extraction.http_client import HTTPClient


DEEPWIKI_TEST_URL = "https://deepwiki.com/anthropics/anthropic-cookbook"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _try_fetch(url, timeout=30):
    try:
        client = HTTPClient()
        return client.fetch_url(url)
    except Exception:
        return None


@pytest.fixture(scope="session")
def fetched_html():
    html = _try_fetch(DEEPWIKI_TEST_URL)
    if html is None:
        pytest.skip("Network unavailable: could not fetch DeepWiki HTML")
    return html


@pytest.fixture(scope="session")
def extracted_markdown(fetched_html):
    extractor = ContentExtractor()
    md = extractor.extract_from_html(fetched_html)
    return md


@pytest.fixture(scope="session")
def extractor():
    return ContentExtractor()


@pytest.fixture(scope="session")
def http_client():
    return HTTPClient()


@pytest.fixture(scope="session")
def tmp_output():
    path = os.path.join(PROJECT_ROOT, ".tmp_output")
    os.makedirs(path, exist_ok=True)
    return path
