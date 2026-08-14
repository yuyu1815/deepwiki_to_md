"""Example: Send a chat message via Devin API using the chat helper functions.

This example relies on external services and requires a prepared config JSON.

How to run:
  PYTHONPATH=src python wiki_tests/chat_example.py \
    --url https://deepwiki.com/microsoft/vscode/some-page \
    --message "質問内容" \
    --config-file ./config.json \
    [--deep-research]

Requirements:
  pip install requests websockets
"""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, Dict, Optional

from chat import ChatResult, load_config, send_chat_message


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DeepWiki chat example (Devin API)")
    p.add_argument(
        "--url",
        default="https://deepwiki.com/microsoft/vscode",
        help="DeepWiki page URL (context). Default: https://deepwiki.com/microsoft/vscode",
    )
    p.add_argument(
        "--message",
        default="What is the purpose of this repository?",
        help="Your question/message to send",
    )
    p.add_argument(
        "--config-file", default="./config.json", help="Path to prepared config JSON"
    )
    p.add_argument(
        "--deep-research", action="store_true", help="Enable Deep Research mode"
    )
    return p.parse_args()


async def run_chat(args: argparse.Namespace) -> ChatResult:
    config: Optional[Dict[str, Any]] = load_config(args.config_file)
    if not config:
        raise SystemExit("Config loading failed. Prepare a complete config file first.")

    result = await send_chat_message(
        wiki_url=args.url,
        message=args.message,
        config=config,
        use_deep_research=args.deep_research,
    )
    return result


def main() -> None:
    args = parse_args()
    result = asyncio.run(run_chat(args))

    # Object-style output (preferred)
    print("\n--- Final result (object) ---")
    print(result)
    print("\n--- send messed ---")
    print(result.sent_message)
    print("\n--- Response message ---")
    print(result.response_message)
    print("\n--- status code ---")
    print(result.status_code)
    print("\n--- response file name ---")
    print(result.reference_files)
    print("\n--- response file contents ---")
    print(result.reference_file_contents)

    # New: show the settings that were actually sent
    print("\n--- request context (wiki_url) ---")
    print(result.wiki_url)
    print("\n--- deep research flag ---")
    print(result.use_deep_research)
    print("\n--- request headers (sent) ---")
    print(json.dumps(result.request_headers, indent=2, ensure_ascii=False))
    print("\n--- request body (sent) ---")
    print(json.dumps(result.request_body, indent=2, ensure_ascii=False))

    # If you still want the raw JSON for debugging/interop, it remains available
    # because ChatResult inherits from dict.
    # print("\n--- Final result (JSON for debugging) ---")
    # print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
