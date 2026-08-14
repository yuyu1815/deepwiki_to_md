import asyncio
import json
import sys
from types import SimpleNamespace

from chat import ChatResult, load_config, send_chat_message


def test_load_config_reads_object(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"headers": {}, "body_template": {}}', encoding="utf-8")
    assert load_config(str(path)) == {"headers": {}, "body_template": {}}


def test_load_config_rejects_non_object(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[]", encoding="utf-8")
    assert load_config(str(path)) is None


def test_chat_result_success_and_error_state():
    success = ChatResult(sent_message="hello")
    failure = ChatResult(sent_message="hello", error="failed")
    assert success.success is True
    assert failure.success is False
    assert failure.to_dict()["error"] == "failed"


def test_send_chat_message_requires_config():
    try:
        asyncio.run(send_chat_message("owner/repo", "hello"))
    except ValueError as exc:
        assert "config is required" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_send_chat_message_reports_http_error(monkeypatch):
    class RequestException(Exception):
        pass

    def post(*args, **kwargs):
        return SimpleNamespace(status_code=503, ok=False, text="unavailable")

    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(post=post, RequestException=RequestException),
    )
    monkeypatch.setitem(sys.modules, "websockets", SimpleNamespace(connect=None))
    monkeypatch.setitem(
        sys.modules,
        "websockets.exceptions",
        SimpleNamespace(WebSocketException=Exception),
    )

    result = asyncio.run(
        send_chat_message(
            "owner/repo",
            "hello",
            {"headers": {"Authorization": "secret"}, "body_template": {}},
        )
    )
    assert result.success is False
    assert result.status_code == 503
    assert result.request_headers["Authorization"] == "<redacted>"


def test_send_chat_message_consumes_websocket(monkeypatch):
    class RequestException(Exception):
        pass

    def post(*args, **kwargs):
        return SimpleNamespace(status_code=200, ok=True, text="")

    messages = iter(
        [
            json.dumps({"type": "chunk", "data": "answer<cite/>"}),
            json.dumps({"type": "reference", "data": {"file_path": "a.py"}}),
            json.dumps({"type": "done"}),
        ]
    )

    class WebSocket:
        async def recv(self):
            return next(messages)

    class Connection:
        async def __aenter__(self):
            return WebSocket()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(post=post, RequestException=RequestException),
    )
    monkeypatch.setitem(
        sys.modules,
        "websockets",
        SimpleNamespace(connect=lambda url: Connection()),
    )
    monkeypatch.setitem(
        sys.modules,
        "websockets.exceptions",
        SimpleNamespace(WebSocketException=Exception),
    )

    result = asyncio.run(
        send_chat_message(
            "owner/repo",
            "hello",
            {"headers": {}, "body_template": {}},
        )
    )
    assert result.success is True
    assert result.response_message == "answer"
    assert result.reference_files == ["a.py"]
