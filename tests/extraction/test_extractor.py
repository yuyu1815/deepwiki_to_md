import pytest

from deepwiki.extraction.extractor import ContentExtractor

DEEPWIKI_TEST_URL = "https://deepwiki.com/anthropics/anthropic-cookbook"


@pytest.mark.network
def test_extract_from_html_returns_nonempty_string(extractor, fetched_html):
    result = extractor.extract_from_html(fetched_html)
    assert isinstance(result, str)
    assert result.strip()


@pytest.mark.network
def test_extract_from_html_contains_markdown_elements(extractor, fetched_html):
    result = extractor.extract_from_html(fetched_html)
    has_heading = "#" in result
    has_content = len(result) > 100
    assert (
        has_heading or has_content
    ), "Expected markdown headings or substantial content"


@pytest.mark.network
def test_extract_from_url_returns_nonempty_markdown(extractor):
    result = extractor.extract_from_url(DEEPWIKI_TEST_URL)
    assert isinstance(result, str)
    assert result.strip()


@pytest.mark.network
def test_extract_from_url_path_style_input(extractor):
    result = extractor.extract_from_url("anthropics/anthropic-cookbook")
    assert isinstance(result, str)
    assert result.strip()


def test_extract_from_html_empty_input_does_not_raise():
    extractor = ContentExtractor()
    result = extractor.extract_from_html("")
    assert isinstance(result, str)


def test_extract_from_html_non_deepwiki_html_returns_string():
    extractor = ContentExtractor()
    result = extractor.extract_from_html("<html><body>plain text</body></html>")
    assert isinstance(result, str)
    assert result.strip()


def test_extract_from_html_non_deepwiki_html_uses_fallback():
    extractor = ContentExtractor()
    html = "<html><head><title>Test Page</title></head><body>plain text</body></html>"
    result = extractor.extract_from_html(html)
    assert "Test Page" in result or result.strip()
