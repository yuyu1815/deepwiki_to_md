import pytest
from deepwiki.parsing.markdown import split_markdown_by_h1


@pytest.mark.unit
def test_single_h1_section():
    md = "# Title\n\nSome content here."
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    assert sections[0]["title"] == "Title"
    assert "Some content here." in sections[0]["content"]


@pytest.mark.unit
def test_multiple_h1_sections():
    md = "# First\n\nContent A.\n\n# Second\n\nContent B."
    sections = split_markdown_by_h1(md)
    assert len(sections) == 2
    assert sections[0]["title"] == "First"
    assert sections[1]["title"] == "Second"
    assert "Content A." in sections[0]["content"]
    assert "Content B." in sections[1]["content"]


@pytest.mark.unit
def test_h1_inside_code_block_not_split():
    md = "# Real Section\n\n```\n# Not a heading\n```\n\nText after."
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    assert sections[0]["title"] == "Real Section"
    assert "# Not a heading" in sections[0]["content"]


@pytest.mark.unit
def test_content_before_first_h1_omitted_when_empty():
    md = "# First Section\n\nHello."
    sections = split_markdown_by_h1(md)
    assert all(s["title"] != "Introduction" for s in sections)


@pytest.mark.unit
def test_content_before_first_h1_kept_when_nonempty():
    md = "Preamble text here.\n\n# First Section\n\nHello."
    sections = split_markdown_by_h1(md)
    intro = next((s for s in sections if s["title"] == "Introduction"), None)
    assert intro is not None
    assert "Preamble text here." in intro["content"]


@pytest.mark.unit
def test_empty_input_returns_empty_list():
    sections = split_markdown_by_h1("")
    assert sections == []


@pytest.mark.unit
def test_setext_style_h1_heading():
    md = "My Title\n========\n\nSome content."
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    assert sections[0]["title"] == "My Title"
    assert "Some content." in sections[0]["content"]


@pytest.mark.unit
def test_details_summary_blocks_filtered():
    md = (
        "# Section\n\n"
        "<details>\n"
        "<summary>Expand</summary>\n"
        "Hidden content\n"
        "</details>\n\n"
        "Visible content."
    )
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    content = sections[0]["content"]
    assert "Hidden content" not in content
    assert "<details>" not in content
    assert "<summary>" not in content
    assert "Visible content." in content


@pytest.mark.unit
def test_nav_list_items_filtered():
    md = (
        "# Section\n\n"
        "- [Introduction](intro.md)\n"
        "- [API Reference](api.md)\n\n"
        "Real content."
    )
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    content = sections[0]["content"]
    assert "- [Introduction](intro.md)" not in content
    assert "- [API Reference](api.md)" not in content
    assert "Real content." in content


@pytest.mark.unit
def test_tilde_fenced_code_block_h1_not_split():
    md = "# Outer\n\n~~~\n# Inside tilde fence\n~~~\n\nAfter."
    sections = split_markdown_by_h1(md)
    assert len(sections) == 1
    assert sections[0]["title"] == "Outer"
