"""Tests for RSC parsing and structured page extraction."""

from deepwiki.parsing.rsc import (
    extract_structured_pages,
    parse_rsc_t_chunks,
    parse_wiki_pages,
    resolve_wiki_pages,
)


class TestParseRscTChunks:
    """Tests for parse_rsc_t_chunks() - extracts T-type chunks from RSC text using byte-length boundaries."""

    def test_single_chunk(self):
        rsc = "17:T5,Hello"
        result = parse_rsc_t_chunks(rsc)
        assert result == {"17": "Hello"}

    def test_multiple_chunks_concatenated(self):
        rsc = "17:T5,Hello18:T5,World"
        result = parse_rsc_t_chunks(rsc)
        assert result == {"17": "Hello", "18": "World"}

    def test_chunk_with_newlines(self):
        content = "# Title\n\nBody text"
        byte_len = format(len(content.encode("utf-8")), "x")
        rsc = f"17:T{byte_len},{content}"
        result = parse_rsc_t_chunks(rsc)
        assert result == {"17": "# Title\n\nBody text"}

    def test_chunk_with_markdown(self):
        content = "# VS Code Overview\n\n<details>\n<summary>Sources</summary>\n</details>\n\n## Architecture\n\nSome text here."
        byte_len = format(len(content.encode("utf-8")), "x")
        rsc = f"17:T{byte_len},{content}"
        result = parse_rsc_t_chunks(rsc)
        assert result["17"] == content

    def test_hex_chunk_id(self):
        rsc = "1a:T5,Hello"
        result = parse_rsc_t_chunks(rsc)
        assert result == {"1a": "Hello"}

    def test_large_byte_length(self):
        content = "# Page Title\n\n" + "Lorem ipsum. " * 1000
        byte_len = format(len(content.encode("utf-8")), "x")
        rsc = f"17:T{byte_len},{content}"
        result = parse_rsc_t_chunks(rsc)
        assert result["17"] == content

    def test_mixed_rsc_lines(self):
        rsc = '0:{"P":null}\n1:"$Sreact.fragment"\n2:I[49138,["9453"]]\n17:T5,Hello\n5:["$","div"]'
        result = parse_rsc_t_chunks(rsc)
        assert "17" in result
        assert result["17"] == "Hello"

    def test_empty_input(self):
        assert parse_rsc_t_chunks("") == {}

    def test_no_t_chunks(self):
        rsc = '0:{"P":null}\n1:"$Sreact.fragment"'
        assert parse_rsc_t_chunks(rsc) == {}

    def test_multibyte_utf8_content(self):
        content = "# 日本語タイトル\n\n本文テキスト"
        byte_len = format(len(content.encode("utf-8")), "x")
        rsc = f"17:T{byte_len},{content}"
        result = parse_rsc_t_chunks(rsc)
        assert result["17"] == content

    def test_consecutive_chunks_boundary_accuracy(self):
        content1 = "Page one content"
        content2 = "Page two content"
        bl1 = format(len(content1.encode("utf-8")), "x")
        bl2 = format(len(content2.encode("utf-8")), "x")
        rsc = f"17:T{bl1},{content1}18:T{bl2},{content2}"
        result = parse_rsc_t_chunks(rsc)
        assert result["17"] == content1
        assert result["18"] == content2


class TestParseWikiPages:
    """Tests for parse_wiki_pages() - extracts wiki.pages[] array from RSC text."""

    def test_basic_pages_extraction(self):
        rsc_text = """5:["$","$L15",null,{"wiki":{"metadata":{"repo_name":"org/repo"},"pages":[{"page_plan":{"id":"1","title":"Overview"},"content":"$17"},{"page_plan":{"id":"1.1","title":"Startup"},"content":"$18"}]}}]"""
        result = parse_wiki_pages(rsc_text)
        assert len(result) == 2
        assert result[0] == {"id": "1", "title": "Overview", "content_ref": "17"}
        assert result[1] == {"id": "1.1", "title": "Startup", "content_ref": "18"}

    def test_content_ref_strips_dollar(self):
        rsc_text = """5:["$","$L15",null,{"wiki":{"metadata":{},"pages":[{"page_plan":{"id":"1","title":"Test"},"content":"$17"}]}}]"""
        result = parse_wiki_pages(rsc_text)
        assert result[0]["content_ref"] == "17"

    def test_empty_pages(self):
        rsc_text = """5:["$","$L15",null,{"wiki":{"metadata":{},"pages":[]}}]"""
        result = parse_wiki_pages(rsc_text)
        assert result == []

    def test_no_wiki_data(self):
        rsc_text = '0:{"P":null}\n1:"$Sreact.fragment"'
        result = parse_wiki_pages(rsc_text)
        assert result == []

    def test_hierarchical_ids(self):
        rsc_text = """5:["$","$L15",null,{"wiki":{"metadata":{},"pages":[{"page_plan":{"id":"1","title":"A"},"content":"$17"},{"page_plan":{"id":"1.1","title":"B"},"content":"$18"},{"page_plan":{"id":"1.2","title":"C"},"content":"$19"},{"page_plan":{"id":"2","title":"D"},"content":"$1a"}]}}]"""
        result = parse_wiki_pages(rsc_text)
        ids = [p["id"] for p in result]
        assert ids == ["1", "1.1", "1.2", "2"]


class TestResolveWikiPages:
    """Tests for resolve_wiki_pages() - combines pages metadata with T-type chunk content."""

    def test_basic_resolution(self):
        pages = [
            {"id": "1", "title": "Overview", "content_ref": "17"},
            {"id": "1.1", "title": "Startup", "content_ref": "18"},
        ]
        chunks = {
            "17": "# Overview\n\nThis is the overview.",
            "18": "# Startup\n\nStartup process details.",
        }
        result = resolve_wiki_pages(pages, chunks)
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["title"] == "Overview"
        assert result[0]["content"] == "# Overview\n\nThis is the overview."
        assert result[1]["id"] == "1.1"
        assert result[1]["content"] == "# Startup\n\nStartup process details."

    def test_missing_chunk_skipped(self):
        pages = [
            {"id": "1", "title": "Overview", "content_ref": "17"},
            {"id": "1.1", "title": "Missing", "content_ref": "99"},
        ]
        chunks = {"17": "# Overview\n\nContent."}
        result = resolve_wiki_pages(pages, chunks)
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_empty_inputs(self):
        assert resolve_wiki_pages([], {}) == []
        assert resolve_wiki_pages([], {"17": "content"}) == []

    def test_preserves_page_order(self):
        pages = [
            {"id": "2", "title": "Second", "content_ref": "18"},
            {"id": "1", "title": "First", "content_ref": "17"},
        ]
        chunks = {"17": "First content", "18": "Second content"}
        result = resolve_wiki_pages(pages, chunks)
        assert result[0]["id"] == "2"
        assert result[1]["id"] == "1"

    def test_generates_slug(self):
        pages = [{"id": "1", "title": "VS Code Codebase Overview", "content_ref": "17"}]
        chunks = {"17": "# VS Code Codebase Overview\n\nContent."}
        result = resolve_wiki_pages(pages, chunks)
        assert result[0]["slug"] == "1-vs-code-codebase-overview"

    def test_slug_special_chars(self):
        pages = [{"id": "2.1", "title": "Build System & CI/CD", "content_ref": "17"}]
        chunks = {"17": "content"}
        result = resolve_wiki_pages(pages, chunks)
        slug = result[0]["slug"]
        assert slug.startswith("2.1-")
        assert "/" not in slug or "." in slug


def _build_mock_html(rsc_payload: str) -> str:
    escaped = rsc_payload.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'<html><script>self.__next_f.push([1, "{escaped}"])</script></html>'


class TestExtractStructuredPages:
    """Tests for extract_structured_pages() - extracts structured page data from HTML."""

    def test_extracts_pages_from_html_with_rsc_data(self):
        content1 = "# Overview\n\nPage one content."
        content2 = "# Startup\n\nPage two content."
        bl1 = format(len(content1.replace("\\n", "\n").encode("utf-8")), "x")
        bl2 = format(len(content2.replace("\\n", "\n").encode("utf-8")), "x")
        rsc_data = (
            f"17:T{bl1},{content1}"
            f"18:T{bl2},{content2}"
            "\n"
            '5:["$","$L15",null,{"wiki":{"metadata":{"repo_name":"org/repo"},"pages":[{"page_plan":{"id":"1","title":"Overview"},"content":"$17"},{"page_plan":{"id":"1.1","title":"Startup"},"content":"$18"}]}}]'
        )
        html = _build_mock_html(rsc_data)
        result = extract_structured_pages(html)
        assert result is not None
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["title"] == "Overview"
        assert "Page one content" in result[0]["content"]
        assert result[0]["slug"] == "1-overview"

    def test_returns_none_when_no_push_data(self):
        html = "<html><body>No push data</body></html>"
        result = extract_structured_pages(html)
        assert result is None

    def test_returns_none_when_no_wiki_pages(self):
        rsc_data = '0:{"P":null}\n1:"$Sreact.fragment"'
        html = _build_mock_html(rsc_data)
        result = extract_structured_pages(html)
        assert result is None

    def test_returns_none_when_no_t_chunks(self):
        rsc_data = '5:["$","$L15",null,{"wiki":{"metadata":{},"pages":[{"page_plan":{"id":"1","title":"Test"},"content":"$17"}]}}]'
        html = _build_mock_html(rsc_data)
        result = extract_structured_pages(html)
        assert result is None

    def test_returns_none_when_only_some_pages_resolve(self):
        rsc_data = (
            '5:["$","$L15",null,{"wiki":{"pages":['
            '{"page_plan":{"id":"1","title":"One"},"content":"$17"},'
            '{"page_plan":{"id":"2","title":"Two"},"content":"$18"}'
            "]}}]\n17:T5,Hello"
        )
        html = _build_mock_html(rsc_data)
        assert extract_structured_pages(html) is None

    def test_result_has_required_fields(self):
        content = "# Test Page\n\nContent here."
        bl = format(len(content.replace("\\n", "\n").encode("utf-8")), "x")
        rsc_data = (
            f"17:T{bl},{content}"
            "\n"
            '5:["$","$L15",null,{"wiki":{"metadata":{},"pages":[{"page_plan":{"id":"1","title":"Test Page"},"content":"$17"}]}}]'
        )
        html = _build_mock_html(rsc_data)
        result = extract_structured_pages(html)
        assert result is not None
        page = result[0]
        assert "id" in page
        assert "title" in page
        assert "content" in page
        assert "slug" in page
