"""Chat utilities for the DeepWiki CLI.

This module extracts the chat functionality that used to live in the CLI. It provides:
- save_config: Save minimal headers and a body template required for API requests.
- load_config: Load a prepared, complete configuration file.
- send_chat_message: Send an async request to the Devin API and receive a streaming response via WebSocket.

Notes:
- To keep the core package zero-dependency, 'requests' and 'websockets' are lazily imported at send_chat_message runtime.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
import json
import uuid
import logging
from urllib.parse import urlparse
from deepwiki import normalize_deepwiki_url


def save_config(config_data: Dict[str, Any], config_file: str) -> None:
    """Save settings to a JSON file.

    Parameters
    ----------
    config_data : Dict[str, Any]
        Settings data (headers/body_template)
    config_file : str
        Path to the config JSON file
    """
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    print(f"\nCreated/updated '{config_file}'.")


def load_config(config_file: str) -> Optional[Dict[str, Any]]:
    """Load a completed config file.

    - Absolute paths are used as-is.
    - Relative paths resolve relative to the current working directory (CWD) only.
    - Returns None on failure.

    This function only loads an existing, complete config JSON. It does not create files.
    """
    from pathlib import Path

    original_arg = config_file
    path = Path(config_file)

    # Resolve path: absolute as-is; relative against CWD
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()

    if not path.exists():
        print(
            f"Error: Config file '{original_arg}' not found. Resolved path: '{path}'. Please prepare a complete config file.")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.exception("Failed to load config file")
        print(f"Error: Failed to load config file '{path}': {e}")
        return None


class ChatResult(dict):
    """Result object for the Chat API.

    - Inherits from dict, so it can be serialized directly via json.dumps
    - Provides attribute-like access (e.g., result.response_message)
    - print(result) shows a human-readable summary
    """

    # 主要キー（型ヒント用）
    sent_message: str
    response_message: Optional[str]
    status_code: Any
    reference_files: List[str]
    reference_file_contents: Dict[str, str]
    wiki_url: Optional[str]
    use_deep_research: Optional[bool]
    request_headers: Dict[str, Any]
    request_body: Dict[str, Any]

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
        )

    # プロパティで属性アクセスを提供
    @property
    def sent_message(self) -> str:  # type: ignore[override]
        """The message that was sent to the chat API.

        Returns
        -------
        str
            The original message sent by the user.
        """
        return self["sent_message"]

    @property
    def response_message(self) -> Optional[str]:  # type: ignore[override]
        """The response message received from the chat API.

        Returns
        -------
        Optional[str]
            The response message, or None if no response was received or an error occurred.
        """
        return self["response_message"]

    @property
    def status_code(self) -> Any:  # type: ignore[override]
        """The HTTP status code from the API request.

        Returns
        -------
        Any
            The status code (typically int), or "N/A" if the request failed before receiving a response.
        """
        return self["status_code"]

    @property
    def reference_files(self) -> List[str]:  # type: ignore[override]
        """List of reference files mentioned in the response.

        Returns
        -------
        List[str]
            List of file paths or references mentioned in the chat response.
        """
        return self["reference_files"]

    @property
    def reference_file_contents(self) -> Dict[str, str]:  # type: ignore[override]
        """Contents of referenced files.

        Returns
        -------
        Dict[str, str]
            Dictionary mapping file paths to their contents.
        """
        return self["reference_file_contents"]

    @property
    def wiki_url(self) -> Optional[str]:  # type: ignore[override]
        """The DeepWiki page URL used as context for the request."""
        return self.get("wiki_url")

    @property
    def use_deep_research(self) -> Optional[bool]:  # type: ignore[override]
        """Whether Deep Research mode was enabled for this request."""
        return self.get("use_deep_research")

    @property
    def request_headers(self) -> Dict[str, Any]:  # type: ignore[override]
        """The HTTP headers that were sent to the API (sanitized as provided)."""
        return self.get("request_headers", {})

    @property
    def request_body(self) -> Dict[str, Any]:  # type: ignore[override]
        """The JSON body that was sent to the API."""
        return self.get("request_body", {})

    def to_dict(self) -> Dict[str, Any]:
        """Return as a plain dict (for compatibility)."""
        return dict(self)

    def __str__(self) -> str:
        body = (self.response_message or "").strip()
        body_preview = body if len(body) <= 400 else body[:400] + "…"
        refs_count = len(self.reference_files)
        contents_count = len(self.reference_file_contents or {})
        deep = "ON" if self.use_deep_research else "OFF"
        return (
            "ChatResult(\n"
            f"  status_code={self.status_code},\n"
            f"  wiki_url={self.wiki_url!r},\n"
            f"  use_deep_research={deep},\n"
            f"  sent_message={self.sent_message!r},\n"
            f"  response_message={body_preview!r},\n"
            f"  reference_files={refs_count} file(s),\n"
            f"  reference_file_contents={contents_count} item(s)\n"
            ")"
        )


async def send_chat_message(
        wiki_url: str,
        message: str,
        config: Optional[Dict[str, Any]] = None,
        use_deep_research: bool = False,
        devlog: bool = False,
) -> ChatResult:
    """Send a message to the Devin API and receive a streaming response.

    Parameters
    ----------
    wiki_url : str
        DeepWiki page URL used as context.
    message : str
        User message.
    config : Optional[Dict[str, Any]]
        Configuration. When None, this attempts to load 'config.json' located next to this chat.py (i.e., src/config.json).
    use_deep_research : bool
        Whether to enable Deep Research mode.
    devlog : bool
        When True, print a human-readable sending log.

    Returns
    -------
    ChatResult
        Result containing response body, status code, and reference files/contents.
    """
    try:
        import requests  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("'requests' is required for chat. Install via: pip install requests") from e
    try:
        import websockets  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("'websockets' is required for chat. Install via: pip install websockets") from e

    # If config is None, load src/config.json (= next to this file)
    if config is None:
        from pathlib import Path
        default_path = str((Path(__file__).parent / "config.json").resolve())
        loaded = load_config(default_path)
        if not loaded:
            raise RuntimeError(f"Default config not found or failed to load at '{default_path}'")
        config = loaded

    post_url = "https://api.devin.ai/ada/query"
    ws_base_url = "wss://api.devin.ai/ada/ws/query/"

    headers: Dict[str, str] = dict(config.get('headers', {}) or {})
    headers['Content-Type'] = 'application/json'

    # Normalize the URL to support owner/repo and /owner/repo inputs
    normalized_wiki_url = normalize_deepwiki_url(wiki_url)

    parsed = urlparse(normalized_wiki_url)
    repo_name = parsed.path.strip('/')
    context_query = (
        f"<relevant_context>This query was sent from the wiki page: {normalized_wiki_url}</relevant_context>"
        f"{message}"
    )

    data_payload: Dict[str, Any] = dict(config.get('body_template', {}) or {})
    new_query_id = f"plugin_{uuid.uuid4()}"
    data_payload.update({
        'user_query': context_query,
        'repo_names': [repo_name] if repo_name else [],
        'query_id': new_query_id,
        'use_deep_research': use_deep_research,
    })

    result = ChatResult(
        sent_message=message,
        response_message=None,
        status_code=None,
        reference_files=[],
        reference_file_contents={},
        wiki_url=normalized_wiki_url,
        use_deep_research=use_deep_research,
        request_headers=dict(headers),
        request_body=dict(data_payload),
    )

    if devlog:
        print("--- Sending chat message ---")
        print(f"URL context: {normalized_wiki_url}")
        print(f"Message: {message}")
        print(f"Deep Research mode: {'ON' if use_deep_research else 'OFF'}\n")

    # HTTP request
    try:
        response = requests.post(post_url, headers=headers, json=data_payload, timeout=60)
    except requests.RequestException as e:  # type: ignore[attr-defined]
        result["status_code"] = "N/A"
        result["response_message"] = f"HTTP request failed: {e}"
        return result

    result["status_code"] = response.status_code
    if not response.ok:
        result["response_message"] = f"HTTP error: {response.text}"
        return result

    # Prepare for WebSocket stream
    final_response = ""
    reference_files = set()
    file_contents: Dict[str, str] = {}

    ws_url = f"{ws_base_url}{new_query_id}"

    def _handle_ws_message(message_data: Dict[str, Any]) -> bool:
        """Handle a single WebSocket message. Returns True when stream is complete."""
        nonlocal final_response, reference_files, file_contents
        msg_type = message_data.get("type")

        if msg_type == "chunk":
            final_response += message_data.get("data", "")
            return False

        if msg_type == "reference":
            data = message_data.get("data") or {}
            file_path = data.get("file_path")
            if file_path:
                reference_files.add(file_path)
            return False

        if msg_type == "file_contents":
            data = message_data.get("data")
            if isinstance(data, list) and len(data) > 2:
                file_path = f"{data[0]}: {data[1]}"
                content = data[2]
                reference_files.add(file_path)
                file_contents[file_path] = content
            return False

        return msg_type == "done"

    try:
        async with websockets.connect(ws_url) as websocket:  # type: ignore
            while True:
                raw_message = await websocket.recv()
                message_data = json.loads(raw_message)
                if _handle_ws_message(message_data):
                    break
    except Exception as e:
        logging.exception("WebSocket stream failed")
        result["response_message"] = f"WebSocket error: {e}"
        return result

    result["response_message"] = final_response.replace("<cite/>", "").strip()
    result["reference_files"] = sorted(list(reference_files))
    result["reference_file_contents"] = file_contents
    return result


__all__ = [
    "save_config",
    "load_config",
    "ChatResult",
    "send_chat_message",
]
