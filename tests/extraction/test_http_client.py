import pytest

from deepwiki.core.errors import HTTPError
from deepwiki.extraction.http_client import HTTPClient

DEEPWIKI_TEST_URL = "https://deepwiki.com/anthropics/anthropic-cookbook"


@pytest.fixture(scope="module")
def client():
    return HTTPClient()


def test_valid_https_url(client):
    assert client._is_valid_url("https://deepwiki.com/foo") is True


def test_valid_http_url(client):
    assert client._is_valid_url("http://example.com/bar") is True


def test_invalid_not_a_url(client):
    assert client._is_valid_url("not-a-url") is False


def test_invalid_ftp_scheme(client):
    assert client._is_valid_url("ftp://x.com") is False


def test_invalid_empty_string(client):
    assert client._is_valid_url("") is False


def test_invalid_no_netloc(client):
    assert client._is_valid_url("https://") is False


@pytest.mark.network
def test_fetch_url_returns_nonempty_html(http_client):
    html = http_client.fetch_url(DEEPWIKI_TEST_URL)
    assert isinstance(html, str)
    assert len(html) > 0
    assert "<html" in html.lower() or "<!doctype" in html.lower()


@pytest.mark.network
def test_fetch_url_nonexistent_repo_raises_or_returns_error(http_client):
    url = "https://deepwiki.com/nonexistent-repo-xxx-yyy-zzz"
    try:
        result = http_client.fetch_url(url)
        assert isinstance(result, str)
    except HTTPError as e:
        assert e.url == url


@pytest.mark.network
def test_fetch_url_invalid_raises_http_error(http_client):
    with pytest.raises(HTTPError):
        http_client.fetch_url("not-a-url")
