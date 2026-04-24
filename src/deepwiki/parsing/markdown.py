import re
import logging
from typing import List, Dict


def _parse_sections_state_machine(content: str) -> List[Dict[str, str]]:
    """Parse Markdown into sections using a simple state machine.

    - Splits by H1 (ATX "# ") and Setext ("====") headers.
    - Ignores headers when inside fenced code blocks (``` or ~~~).
    - Produces an initial list of sections with raw (unfiltered) content.
    - Keeps an implicit initial section named "Introduction" and drops it if empty.

    This function preserves the legacy behavior of split_markdown_by_h1.
    """
    sections: List[Dict[str, str]] = []
    lines: List[str] = content.split('\n')

    in_code_block: bool = False
    current_section_title: str = "Introduction"
    current_section_content: List[str] = []

    def _append_section_if_needed(title: str, body_lines: List[str]) -> None:
        # Skip empty initial section (Introduction), but add others even if empty.
        body = '\n'.join(body_lines).strip()
        if title == "Introduction" and body == "":
            return
        sections.append({"title": title, "content": body})

    prev_line: str = ""
    for line in lines:
        stripped = line.strip()
        if not in_code_block:
            is_fence_open = bool(re.match(r'^(`{3,}|~{3,})', stripped))
            if is_fence_open:
                in_code_block = True
                current_section_content.append(line)
                prev_line = line
                continue
        else:
            is_fence_close = bool(re.match(r'^(`{3,}|~{3,})\s*$', stripped))
            if is_fence_close:
                in_code_block = False
                current_section_content.append(line)
                prev_line = line
                continue

        # Detect Setext H1 (previous line is title, this line is ==== etc.)
        if (
            not in_code_block
            and stripped
            and all(ch == '=' for ch in stripped)
            and prev_line.strip()
        ):
            # Save previous section (skip if Introduction is empty)
            prev_content_lines = current_section_content[:-1]
            _append_section_if_needed(current_section_title, prev_content_lines)
            # Start new section (title is previous line)
            current_section_title = prev_line.strip()
            current_section_content = []
            prev_line = line
            continue

        # Check for ATX H1 headers (exact "# ") outside code blocks
        if not in_code_block and line.startswith("# "):
            _append_section_if_needed(current_section_title, current_section_content)
            current_section_title = line[2:].strip()  # Remove "# " prefix
            current_section_content = []
        else:
            current_section_content.append(line)
        prev_line = line

    _append_section_if_needed(current_section_title, current_section_content)
    return sections


def _filter_sections(sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Post-process section contents to remove non-content parts.

    Behavior is kept identical to the legacy implementation:
    - Remove entire <details> blocks (from <details ...> to </details>).
    - Drop <summary ...> lines.
    - Drop navigation list items like "- [title](... .md)".
    - Trim trailing/leading whitespace of each section's content.
    """
    result: List[Dict[str, str]] = []
    for section in sections:
        raw_content = section.get('content', '')
        sec_lines = raw_content.split('\n') if raw_content else []
        filtered_lines: List[str] = []
        skip_details = False

        for l in sec_lines:
            l_strip_lower = l.strip().lower()
            if l_strip_lower.startswith('<details'):
                skip_details = True
                continue
            if l_strip_lower.startswith('</details'):
                skip_details = False
                continue
            if skip_details:
                continue

            if l_strip_lower.startswith('<summary'):
                continue
            if l.strip().startswith('- [') and l.strip().endswith('.md)'):
                continue

            filtered_lines.append(l)

        result.append({
            'title': section.get('title', ''),
            'content': '\n'.join(filtered_lines).strip(),
        })
    return result


def split_markdown_by_h1(content: str) -> List[Dict[str, str]]:
    """Split Markdown by H1 headers while ignoring H1s inside code blocks.

    This is a thin wrapper that delegates to two focused helpers:
    1) _parse_sections_state_machine: builds raw sections.
    2) _filter_sections: removes non-content lines/blocks.

    Args:
        content: The Markdown string to split.

    Returns:
        A list of dicts with 'title' and 'content' keys.
    """
    sections = _parse_sections_state_machine(content)
    return _filter_sections(sections)
