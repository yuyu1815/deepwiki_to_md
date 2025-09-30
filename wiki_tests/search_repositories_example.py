"""Example: Search public indexes (Devin API) using search_repositories.

How to run:
  PYTHONPATH=src python wiki_tests/search_repositories_example.py --search Gemini [--devlog]

This prints JSON summary by default, or a human-readable log style when --devlog is specified.
"""
from __future__ import annotations

import argparse
from typing import Any, Dict, List
from search_repository import search_repositories, API_URL


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search public indexes (Devin API)")
    p.add_argument("--search", default="Gemini", help="Search term (default: Gemini)")
    p.add_argument("--devlog", action="store_true", help="Print human-readable log format")
    return p.parse_args()


def print_devlog(result: Dict[str, Any]) -> None:
    indices: List[Dict[str, Any]] = result.get("indices", [])
    for item in indices:
        repo = item.get("repo_name")
        lang = item.get("language")
        stars = item.get("stargazers_count")
        desc = (item.get("description") or "").strip().replace("\n", " ")

        # topics can be None or non-list; normalize and cap to 8
        raw_topics = item.get("topics")
        topics_list = raw_topics if isinstance(raw_topics, list) else []
        topics_str = ", ".join([str(t) for t in topics_list[:8] if t is not None])
        topics_out = topics_str if topics_str else "(none)"

        last_modified = item.get("last_modified")

        print(f"- {repo} ({lang}) ⭐ {stars}")
        print(f"  id: {item.get('schedule_id') or item.get('id')}")
        if desc:
            print(f"  description: {desc}")
        # Always show topics line; show placeholder when empty/None
        print(f"  topics: {topics_out}")
        if last_modified:
            print(f"  last_modified: {last_modified}")
        print("=" * 30)
        print()
    print(f"indices: {len(indices)}")


def main() -> None:
    args = parse_args()

    print(API_URL)
    result = search_repositories(args.search)

    if args.devlog:
        print_devlog(result)
    else:
        indices = result.get("indices", [])
        print({"indices": indices[:3], "count": len(indices)})


if __name__ == "__main__":
    main()
