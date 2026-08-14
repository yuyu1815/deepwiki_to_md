"""Optional Devin API chat support for the command-line interface."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, cast
from urllib.parse import urlparse

from deepwiki import normalize_deepwiki_url

_SENSITIVE_HEADERS = {"authorization", "cookie", "proxy-authorization", "x-api-key"}


def save_config(config_data: Dict[str, Any], config_file: str) -> None:
    """Save chat settings as JSON."""
    with open(config_file, "w", encoding="utf-8") as file:
        json.dump(config_data, file, indent=4, ensure_ascii=False)


def load_config(config_file: str) -> Optional[Dict[str, Any]]:
    """Load an existing chat configuration file."""
    path = Path(config_file).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        with path.resolve().open("r", encoding="utf-8") as file:
            config = json.load(file)
        if not isinstance(config, dict):
            raise ValueError("Config must be a JSON object")
        return cast(Dict[str, Any], config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        logging.error("Failed to load config file %s: %s", path, exc)
        return None


def _sanitized_headers(headers: Dict[str, str]) -> Dict[str, str]:
    return {
        key: "<redacted>" if key.lower() in _SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


class ChatResult(dict):
    """Dictionary-compatible result returned by the chat API."""

    def __init__(
        self,
        *,
        sent_message: str,
        response_message: Optional[str] = None,
        status_code: Any = None,
        reference_files: Optional[List[str]] = None,
        reference_file_contents: Optional[Dict[str, str]] = None,
        wiki_url: Optional[str] = None,
        use_deep_research: Optional[bool] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        super().__init__(
            sent_message=sent_message,
            response_message=response_message,
            status_code=status_code,
            reference_files=reference_files or [],
            reference_file_contents=reference_file_contents or {},
            wiki_url=wiki_url,
            use_deep_research=use_deep_research,
            request_headers=request_headers or {},
            request_body=request_body or {},
            error=error,
        )

    @property
    def sent_message(self) -> str:
        return cast(str, self["sent_message"])

    @property
    def response_message(self) -> Optional[str]:
        return cast(Optional[str], self["response_message"])

    @property
    def status_code(self) -> Any:
        return self["status_code"]

    @property
    def reference_files(self) -> List[str]:
        return cast(List[str], self["reference_files"])

    @property
    def reference_file_contents(self) -> Dict[str, str]:
        return cast(Dict[str, str], self["reference_file_contents"])

    @property
    def wiki_url(self) -> Optional[str]:
        return cast(Optional[str], self.get("wiki_url"))

    @property
    def use_deep_research(self) -> Optional[bool]:
        return cast(Optional[bool], self.get("use_deep_research"))

    @property
    def request_headers(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self.get("request_headers", {}))

    @property
    def request_body(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self.get("request_body", {}))

    @property
    def error(self) -> Optional[str]:
        return cast(Optional[str], self.get("error"))

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> Dict[str, Any]:
        return dict(self)

    def __str__(self) -> str:
        body = (self.response_message or "").strip()
        body_preview = body if len(body) <= 400 else body[:400] + "…"
        return (
            "ChatResult(\n"
            f"  success={self.success},\n"
            f"  status_code={self.status_code},\n"
            f"  wiki_url={self.wiki_url!r},\n"
            f"  sent_message={self.sent_message!r},\n"
            f"  response_message={body_preview!r},\n"
            f"  reference_files={len(self.reference_files)} file(s)\n"
            ")"
        )


async def send_chat_message(
    wiki_url: str,
    message: str,
    config: Optional[Dict[str, Any]] = None,
    use_deep_research: bool = False,
    devlog: bool = False,
) -> ChatResult:
    """Send a Devin API query and consume its WebSocket response."""
    if config is None:
        raise ValueError("config is required; load it with load_config(config_file)")

    try:
        import requests  # type: ignore
        import websockets  # type: ignore
        from websockets.exceptions import WebSocketException  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Chat dependencies are missing. Install deepwiki-to-md[chat]."
        ) from exc

    post_url = "https://api.devin.ai/ada/query"
    ws_base_url = "wss://api.devin.ai/ada/ws/query/"
    headers: Dict[str, str] = dict(config.get("headers", {}) or {})
    headers["Content-Type"] = "application/json"

    normalized_wiki_url = normalize_deepwiki_url(wiki_url)
    repo_name = urlparse(normalized_wiki_url).path.strip("/")
    query_id = f"plugin_{uuid.uuid4()}"
    payload: Dict[str, Any] = dict(config.get("body_template", {}) or {})
    payload.update(
        {
            "user_query": (
                "<relevant_context>This query was sent from the wiki page: "
                f"{normalized_wiki_url}</relevant_context>{message}"
            ),
            "repo_names": [repo_name] if repo_name else [],
            "query_id": query_id,
            "use_deep_research": use_deep_research,
        }
    )

    result = ChatResult(
        sent_message=message,
        wiki_url=normalized_wiki_url,
        use_deep_research=use_deep_research,
        request_headers=_sanitized_headers(headers),
        request_body=dict(payload),
    )

    if devlog:
        print(f"Sending chat message for {normalized_wiki_url}")

    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(post_url, headers=headers, json=payload, timeout=60),
        )
    except requests.RequestException as exc:
        result["status_code"] = "N/A"
        result["error"] = f"HTTP request failed: {exc}"
        result["response_message"] = result["error"]
        return result

    result["status_code"] = response.status_code
    if not response.ok:
        result["error"] = f"HTTP {response.status_code}: {response.text}"
        result["response_message"] = result["error"]
        return result

    final_response = ""
    reference_files = set()
    file_contents: Dict[str, str] = {}
    try:
        async with websockets.connect(f"{ws_base_url}{query_id}") as websocket:
            while True:
                raw_message = await websocket.recv()
                message_data = json.loads(raw_message)
                message_type = message_data.get("type")
                if message_type == "chunk":
                    final_response += str(message_data.get("data", ""))
                elif message_type == "reference":
                    data = message_data.get("data") or {}
                    file_path = data.get("file_path")
                    if file_path:
                        reference_files.add(str(file_path))
                elif message_type == "file_contents":
                    data = message_data.get("data")
                    if isinstance(data, list) and len(data) > 2:
                        file_path = f"{data[0]}: {data[1]}"
                        reference_files.add(file_path)
                        file_contents[file_path] = str(data[2])
                elif message_type == "done":
                    break
    except (WebSocketException, OSError, ValueError, json.JSONDecodeError) as exc:
        logging.error("WebSocket stream failed: %s", exc)
        result["error"] = f"WebSocket error: {exc}"
        result["response_message"] = result["error"]
        return result

    result["response_message"] = final_response.replace("<cite/>", "").strip()
    result["reference_files"] = sorted(reference_files)
    result["reference_file_contents"] = file_contents
    return result


__all__ = ["save_config", "load_config", "ChatResult", "send_chat_message"]
