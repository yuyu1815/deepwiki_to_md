import io
import json
from urllib.error import HTTPError, URLError

import pytest

import search_repository


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_search_repositories_returns_json_object(monkeypatch):
    monkeypatch.setattr(
        search_repository.urllib.request,
        "urlopen",
        lambda request, timeout: Response(json.dumps({"indices": []}).encode()),
    )
    assert search_repository.search_repositories("test") == {"indices": []}


def test_search_repositories_rejects_non_object(monkeypatch):
    monkeypatch.setattr(
        search_repository.urllib.request,
        "urlopen",
        lambda request, timeout: Response(b"[]"),
    )
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        search_repository.search_repositories("test")


def test_search_repositories_preserves_http_status(monkeypatch):
    error = HTTPError("https://example.test", 429, "limited", {}, io.BytesIO())

    def raise_error(request, timeout):
        raise error

    monkeypatch.setattr(search_repository.urllib.request, "urlopen", raise_error)
    with pytest.raises(RuntimeError, match="429"):
        search_repository.search_repositories("test")


def test_search_repositories_reports_network_error(monkeypatch):
    def raise_error(request, timeout):
        raise URLError("offline")

    monkeypatch.setattr(search_repository.urllib.request, "urlopen", raise_error)
    with pytest.raises(RuntimeError, match="Network error"):
        search_repository.search_repositories("test")
