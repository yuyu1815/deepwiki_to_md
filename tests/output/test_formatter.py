import pytest
from deepwiki.output.formatter import OutputFormatter


@pytest.mark.unit
def test_format_content_no_metadata_returns_content_only():
    formatter = OutputFormatter()
    result = formatter.format_content("Hello, world.")
    assert result == "Hello, world."
    assert "---" not in result


@pytest.mark.unit
def test_format_content_with_metadata_prepends_yaml_front_matter():
    formatter = OutputFormatter()
    result = formatter.format_content("Body text.", metadata={"title": "My Doc", "author": "yusei"})
    lines = result.splitlines()
    assert lines[0] == "---"
    assert "title: My Doc" in lines
    assert "author: yusei" in lines
    closing_index = lines.index("---", 1)
    assert closing_index > 0
    assert "Body text." in result


@pytest.mark.unit
def test_format_content_empty_content_with_metadata():
    formatter = OutputFormatter()
    result = formatter.format_content("", metadata={"source": "test"})
    assert "---" in result
    assert "source: test" in result


@pytest.mark.unit
def test_format_content_empty_content_no_metadata():
    formatter = OutputFormatter()
    result = formatter.format_content("")
    assert result == ""


@pytest.mark.unit
def test_format_content_none_metadata_no_front_matter():
    formatter = OutputFormatter()
    result = formatter.format_content("Content here.", metadata=None)
    assert "---" not in result
    assert result == "Content here."


@pytest.mark.unit
def test_format_content_non_markdown_format_returns_content_as_is():
    formatter = OutputFormatter(format_type="plain")
    result = formatter.format_content("Raw content.", metadata={"key": "value"})
    assert result == "Raw content."
