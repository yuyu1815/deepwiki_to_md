"""DeepWiki CLI 用のチャットユーティリティ。

このモジュールは、CLI に内蔵されていたチャット機能を切り出したものです。提供機能は次のとおりです。
- save_config: API リクエストに必要な最小限のヘッダーとボディのテンプレートを保存
- load_or_create_config: 完成済みの設定ファイルを読み込む
- send_chat_message: Devin API へ非同期でリクエストし、WebSocket でストリーム応答を受信

注意:
- 本体パッケージをゼロ依存に保つため、'requests' と 'websockets' は send_chat_message 実行時に遅延インポートされます。
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
import json
import uuid
import logging
from urllib.parse import urlparse
from deepwiki_to_md import normalize_deepwiki_url


def save_config(config_data: Dict[str, Any], config_file: str) -> None:
    """設定を JSON ファイルに保存する。

    パラメータ
    ----------
    config_data : Dict[str, Any]
        設定データ（headers/body_template）
    config_file : str
        設定 JSON ファイルのパス
    """
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    print(f"\nCreated/updated '{config_file}'.")


def load_or_create_config(config_file: str) -> Optional[Dict[str, Any]]:
    """設定ファイルを読み込む（完成済み前提）。

    この関数は設定ファイルが既に完成していることを前提に、単に読み込んで返します。
    ファイルが存在しない場合や読み込みに失敗した場合は None を返します。

    パスの解決規則:
    - 絶対パスの場合: そのまま使用。
    - 相対パスの場合: この関数の呼び出し元ファイル（ユーザー側スクリプト）からの相対で解決し、
      それが見つからなければカレントディレクトリからの相対で解決を試みます（後方互換）。

    パラメータ
    ----------
    config_file : str
        設定 JSON ファイルのパス

    戻り値
    ------
    Optional[Dict[str, Any]]
        設定ディクショナリ（失敗時は None）
    """
    from pathlib import Path
    import inspect

    original_arg = config_file
    path = Path(config_file)

    # 相対パスなら、呼び出し元ファイルを基準に解決する
    if not path.is_absolute():
        caller_path: Optional[Path] = None
        # スタックから chat.py 以外の最初のフレームを探す（不要な try は使わない）
        for frame_info in inspect.stack()[1:]:
            fname = Path(frame_info.filename)
            if fname.name != Path(__file__).name:
                caller_path = fname
                break

        if caller_path is not None:
            candidate = (caller_path.parent / path).resolve()
            if candidate.exists():
                path = candidate
            else:
                # 後方互換: CWD からの相対も試す
                cwd_candidate = (Path.cwd() / path).resolve()
                if cwd_candidate.exists():
                    path = cwd_candidate
        else:
            # 呼び出し元が特定できない場合は CWD 基準
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
    """Chat API の結果オブジェクト。

    - dict を継承しているため json.dumps でそのままシリアライズ可能
    - 属性アクセスも提供（result.response_message など）
    - print(result) で読みやすい要約を表示
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
        """辞書として取得（互換目的）。"""
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
        config: Dict[str, Any],
        use_deep_research: bool,
        devlog: bool = False,
) -> ChatResult:
    """Devin API にメッセージを送り、応答をストリームで受け取る。

    パラメータ
    ----------
    wiki_url : str
        コンテキストとして使用する DeepWiki ページ URL
    message : str
        ユーザーのメッセージ
    config : Dict[str, Any]
        load_or_create_config で読み込んだ設定
    use_deep_research : bool
        Deep Research モードを有効にするかどうか

    戻り値
    ------
    ChatResult
        応答本文、ステータスコード、参照ファイル/内容を含む結果
    """
    try:
        import requests  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("'requests' is required for chat. Install via: pip install requests") from e
    try:
        import websockets  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("'websockets' is required for chat. Install via: pip install websockets") from e

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
    "load_or_create_config",
    "ChatResult",
    "send_chat_message",
]
