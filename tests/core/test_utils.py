import pytest
from deepwiki.core.utils import normalize_deepwiki_url, sanitize_filename


class TestNormalizeDeepwikiUrl:

    @pytest.mark.unit
    def test_full_https_url_returned_as_is(self):
        url = "https://deepwiki.com/owner/repo"
        assert normalize_deepwiki_url(url) == url

    @pytest.mark.unit
    def test_http_url_returned_as_is(self):
        url = "http://deepwiki.com/owner/repo"
        assert normalize_deepwiki_url(url) == url

    @pytest.mark.unit
    def test_non_deepwiki_https_url_returned_as_is(self):
        url = "https://github.com/foo/bar"
        assert normalize_deepwiki_url(url) == url

    @pytest.mark.unit
    def test_path_with_leading_slash_converted_to_full_url(self):
        assert normalize_deepwiki_url("/owner/repo") == "https://deepwiki.com/owner/repo"

    @pytest.mark.unit
    def test_path_without_slash_converted_to_full_url(self):
        assert normalize_deepwiki_url("owner/repo") == "https://deepwiki.com/owner/repo"

    @pytest.mark.unit
    def test_path_with_trailing_slash_stripped_and_converted(self):
        assert normalize_deepwiki_url("owner/repo/") == "https://deepwiki.com/owner/repo"

    @pytest.mark.unit
    def test_plain_text_with_no_slash_returned_as_is(self):
        assert normalize_deepwiki_url("justplaintext") == "justplaintext"

    @pytest.mark.unit
    def test_text_with_space_returned_as_is(self):
        assert normalize_deepwiki_url("not a/path") == "not a/path"


class TestSanitizeFilename:

    @pytest.mark.unit
    def test_normal_text_unchanged(self):
        assert sanitize_filename("hello_world") == "hello_world"

    @pytest.mark.unit
    def test_special_characters_removed(self):
        result = sanitize_filename("hello!@#$%^&*world")
        assert result == "helloworld"

    @pytest.mark.unit
    def test_spaces_converted_to_underscores(self):
        assert sanitize_filename("hello world") == "hello_world"

    @pytest.mark.unit
    def test_empty_string_returns_unnamed(self):
        assert sanitize_filename("") == "unnamed"

    @pytest.mark.unit
    def test_only_special_chars_returns_unnamed(self):
        assert sanitize_filename("!!!") == "unnamed"

    @pytest.mark.unit
    def test_very_long_filename_preserved(self):
        long_name = "a" * 300
        assert sanitize_filename(long_name) == long_name

    @pytest.mark.unit
    def test_dots_and_hyphens_preserved(self):
        assert sanitize_filename("my-file.name") == "my-file.name"

    @pytest.mark.unit
    def test_unicode_characters_removed(self):
        result = sanitize_filename("hello\U0001F600world")
        assert result == "helloworld"

    @pytest.mark.unit
    def test_mixed_spaces_and_special_chars(self):
        result = sanitize_filename("My File! (v2)")
        assert result == "My_File_v2"
