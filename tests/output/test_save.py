"""Tests for save_markdown_to_library - both H1 splitting and structured pages modes."""
import os
import pytest
from deepwiki.output.save import save_markdown_to_library
from deepwiki.core.errors import ConfigError
from deepwiki.extraction.extractor import ContentExtractor

DEEPWIKI_TEST_URL = "https://deepwiki.com/anthropics/anthropic-cookbook"
OFFLINE_MD = "# Section1\ncontent1\n# Section2\ncontent2"


class TestSaveLibraryOffline:
    """Offline unit tests for save_markdown_to_library with H1 splitting."""

    @pytest.mark.unit
    def test_save_creates_correct_directory_structure_from_url(self, tmp_path):
        result = save_markdown_to_library(
            OFFLINE_MD,
            source_url="https://deepwiki.com/myuser/myrepo",
            base_dir=str(tmp_path),
        )
        assert result["username"] == "myuser"
        assert result["library_name"] == "myrepo"
        assert os.path.isdir(result["output_dir"])
        assert result["output_dir"] == str(tmp_path / "myuser" / "myrepo")

    @pytest.mark.unit
    def test_save_creates_correct_directory_structure_from_path_style(self, tmp_path):
        result = save_markdown_to_library(
            OFFLINE_MD,
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
        )
        assert result["username"] == "myuser"
        assert result["library_name"] == "myrepo"
        assert os.path.isdir(result["output_dir"])

    @pytest.mark.unit
    def test_save_generates_index_file_with_links(self, tmp_path):
        result = save_markdown_to_library(
            OFFLINE_MD,
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
        )
        index_path = result["library_file"]
        assert os.path.isfile(index_path)
        content = open(index_path, encoding="utf-8").read()
        assert "Section1" in content or "section1" in content.lower()
        assert "Section2" in content or "section2" in content.lower()
        assert "[" in content and "](" in content

    @pytest.mark.unit
    def test_save_each_section_file_has_content(self, tmp_path):
        result = save_markdown_to_library(
            OFFLINE_MD,
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
        )
        for file_path in result["saved_files"]:
            assert os.path.isfile(file_path)
            content = open(file_path, encoding="utf-8").read()
            assert content.strip()

    @pytest.mark.unit
    def test_save_returns_two_sections_for_offline_md(self, tmp_path):
        result = save_markdown_to_library(
            OFFLINE_MD,
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
        )
        assert len(result["saved_files"]) == 2

    @pytest.mark.unit
    def test_invalid_source_url_no_path_raises_config_error(self, tmp_path):
        with pytest.raises(ConfigError):
            save_markdown_to_library(
                OFFLINE_MD,
                source_url="https://deepwiki.com/",
                base_dir=str(tmp_path),
            )

    @pytest.mark.unit
    def test_source_url_missing_library_raises_config_error(self, tmp_path):
        with pytest.raises(ConfigError):
            save_markdown_to_library(
                OFFLINE_MD,
                source_url="https://deepwiki.com/onlyuser",
                base_dir=str(tmp_path),
            )

    @pytest.mark.unit
    def test_empty_source_url_raises_config_error(self, tmp_path):
        with pytest.raises(ConfigError):
            save_markdown_to_library(OFFLINE_MD, source_url="", base_dir=str(tmp_path))


class TestSaveLibraryNetwork:
    """Network tests for save_markdown_to_library."""

    @pytest.mark.network
    def test_save_from_real_extracted_markdown(self, tmp_output, extracted_markdown):
        result = save_markdown_to_library(
            extracted_markdown,
            source_url=DEEPWIKI_TEST_URL,
            base_dir=tmp_output,
        )
        assert result["username"] == "anthropics"
        assert result["library_name"] == "anthropic-cookbook"
        assert os.path.isdir(result["output_dir"])
        assert os.path.isfile(result["library_file"])
        assert len(result["saved_files"]) >= 1

    @pytest.mark.network
    def test_save_from_real_markdown_index_contains_links(self, tmp_output, extracted_markdown):
        result = save_markdown_to_library(
            extracted_markdown,
            source_url=DEEPWIKI_TEST_URL,
            base_dir=tmp_output,
        )
        content = open(result["library_file"], encoding="utf-8").read()
        assert "](anthropic-cookbook/" in content

    @pytest.mark.network
    def test_save_vscode_wiki(self, tmp_output):
        extractor = ContentExtractor()
        md = extractor.extract_from_url("microsoft/vscode")
        result = save_markdown_to_library(
            md,
            source_url="microsoft/vscode",
            base_dir=tmp_output,
        )
        assert result["username"] == "microsoft"
        assert result["library_name"] == "vscode"
        assert os.path.isdir(result["output_dir"])
        assert len(result["saved_files"]) >= 10


STRUCTURED_PAGES = [
    {
        "id": "1",
        "title": "VS Code Codebase Overview",
        "content": "# VS Code Codebase Overview\n\nThis is the overview page.\n\n## Architecture\n\nDetails here.",
        "slug": "1-vs-code-codebase-overview",
    },
    {
        "id": "1.1",
        "title": "Application Startup",
        "content": "# Application Startup\n\nStartup process details.\n\n## Boot Sequence\n\nStep by step.",
        "slug": "1.1-application-startup",
    },
    {
        "id": "2",
        "title": "Core Editor",
        "content": "# Core Editor\n\nEditor internals.\n\n## Text Model\n\nBuffer implementation.",
        "slug": "2-core-editor",
    },
]


@pytest.mark.unit
class TestSaveWithStructuredPages:
    """Tests for save_markdown_to_library when pages parameter is provided."""

    def test_creates_files_from_structured_pages(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        assert len(result["saved_files"]) == 3

    def test_filenames_use_slug(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        filenames = [os.path.basename(f) for f in result["saved_files"]]
        assert "1-vs-code-codebase-overview.md" in filenames
        assert "1.1-application-startup.md" in filenames
        assert "2-core-editor.md" in filenames

    def test_file_content_matches_page_content(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        for file_path in result["saved_files"]:
            content = open(file_path, encoding="utf-8").read()
            assert content.strip()
            assert "# " in content

    def test_preserves_page_order(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        filenames = [os.path.basename(f) for f in result["saved_files"]]
        assert filenames[0] == "1-vs-code-codebase-overview.md"
        assert filenames[1] == "1.1-application-startup.md"
        assert filenames[2] == "2-core-editor.md"

    def test_index_file_uses_page_titles(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        index_content = open(result["library_file"], encoding="utf-8").read()
        assert "VS Code Codebase Overview" in index_content
        assert "Application Startup" in index_content
        assert "Core Editor" in index_content

    def test_index_file_links_use_slug_filenames(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        index_content = open(result["library_file"], encoding="utf-8").read()
        assert "1-vs-code-codebase-overview.md" in index_content
        assert "1.1-application-startup.md" in index_content

    def test_directory_structure_same_as_h1_mode(self, tmp_path):
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        assert result["username"] == "microsoft"
        assert result["library_name"] == "vscode"
        assert os.path.isdir(result["output_dir"])

    def test_md_param_ignored_when_pages_provided(self, tmp_path):
        result = save_markdown_to_library(
            md="# Wrong Title\nThis should be ignored\n# Another Wrong\nAlso ignored",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=STRUCTURED_PAGES,
        )
        filenames = [os.path.basename(f) for f in result["saved_files"]]
        assert "Wrong_Title.md" not in filenames
        assert len(result["saved_files"]) == 3

    def test_empty_pages_list_falls_back_to_h1(self, tmp_path):
        result = save_markdown_to_library(
            md="# Section A\ncontent A\n# Section B\ncontent B",
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
            pages=[],
        )
        assert len(result["saved_files"]) == 2

    def test_single_page(self, tmp_path):
        single = [STRUCTURED_PAGES[0]]
        result = save_markdown_to_library(
            md="",
            source_url="microsoft/vscode",
            base_dir=str(tmp_path),
            pages=single,
        )
        assert len(result["saved_files"]) == 1
        assert os.path.basename(result["saved_files"][0]) == "1-vs-code-codebase-overview.md"


@pytest.mark.unit
class TestBackwardCompatibility:
    """Ensure existing H1-splitting behavior is unchanged when pages is not provided."""

    def test_no_pages_param_uses_h1_split(self, tmp_path):
        result = save_markdown_to_library(
            md="# Section1\ncontent1\n# Section2\ncontent2",
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
        )
        assert len(result["saved_files"]) == 2

    def test_pages_none_uses_h1_split(self, tmp_path):
        result = save_markdown_to_library(
            md="# Section1\ncontent1\n# Section2\ncontent2",
            source_url="myuser/myrepo",
            base_dir=str(tmp_path),
            pages=None,
        )
        assert len(result["saved_files"]) == 2
