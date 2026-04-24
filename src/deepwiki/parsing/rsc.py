import re
import json
import logging
from typing import Optional, List, Dict, Any

from deepwiki.core.config import ExtractionConfig


def parse_rsc_t_chunks(rsc_text: str) -> Dict[str, str]:
    """Parse T-type chunks from RSC text using byte-length boundaries.

    Format: <hex_id>:T<hex_byte_length>,<raw_content>
    """
    rsc_bytes = rsc_text.encode('utf-8')
    chunks: Dict[str, str] = {}
    pattern = re.compile(rb'(\w+):T([0-9a-f]+),')
    pos = 0
    while pos < len(rsc_bytes):
        match = pattern.search(rsc_bytes, pos)
        if not match:
            break
        chunk_id = match.group(1).decode('utf-8')
        byte_length = int(match.group(2), 16)
        content_start = match.end()
        content_bytes = rsc_bytes[content_start:content_start + byte_length]
        chunks[chunk_id] = content_bytes.decode('utf-8')
        pos = content_start + byte_length
    return chunks


def parse_wiki_pages(rsc_text: str) -> List[Dict[str, str]]:
    """Extract wiki.pages[] metadata from RSC text.

    Returns list of {id, title, content_ref} dicts.
    """
    for line in rsc_text.split('\n'):
        if '"pages"' not in line:
            continue
        colon_pos = line.find(':')
        if colon_pos < 0:
            continue
        payload = line[colon_pos + 1:]
        try:
            parsed = json.loads(payload)
            pages_array = _find_wiki_pages(parsed)
            if pages_array is not None:
                return _extract_page_metadata(pages_array)
        except (json.JSONDecodeError, ValueError):
            continue
    return []


def _find_wiki_pages(data: Any) -> Optional[List]:
    """Recursively search for wiki.pages in nested data."""
    if isinstance(data, dict):
        if 'wiki' in data and isinstance(data['wiki'], dict):
            wiki = data['wiki']
            if 'pages' in wiki:
                return wiki['pages']
        for v in data.values():
            result = _find_wiki_pages(v)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _find_wiki_pages(item)
            if result is not None:
                return result
    return None


def _extract_page_metadata(pages_array: List) -> List[Dict[str, str]]:
    """Extract id, title, content_ref from pages array."""
    result = []
    for page in pages_array:
        if not isinstance(page, dict):
            continue
        plan = page.get('page_plan', {})
        content_raw = page.get('content', '')
        content_ref = content_raw.lstrip('$') if isinstance(content_raw, str) else ''
        result.append({
            'id': plan.get('id', ''),
            'title': plan.get('title', ''),
            'content_ref': content_ref,
        })
    return result


def _generate_page_slug(page_id: str, title: str) -> str:
    """Generate URL-style slug: 'id-title-lowercased-hyphenated'."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return f"{page_id}-{slug}"


def resolve_wiki_pages(pages: List[Dict[str, str]], chunks: Dict[str, str]) -> List[Dict[str, Any]]:
    """Combine page metadata with T-type chunk content.

    Skips pages whose content_ref is not found in chunks.
    """
    result = []
    for page in pages:
        ref = page.get('content_ref', '')
        if ref not in chunks:
            continue
        result.append({
            'id': page['id'],
            'title': page['title'],
            'content': chunks[ref],
            'slug': _generate_page_slug(page['id'], page['title']),
        })
    return result


def extract_structured_pages(html: str) -> Optional[List[Dict[str, Any]]]:
    """Extract structured page data from DeepWiki HTML.

    Pipeline: HTML → self.__next_f.push extraction → T-chunk parse → wiki.pages[] parse → resolve.
    Returns None if any step fails to produce usable data.
    """
    chunks_list: List[str] = []
    for match in ExtractionConfig.STRING_PAYLOAD_PATTERN.finditer(html):
        raw = match.group(1)
        try:
            decoded = json.loads(f'"{raw}"')
        except Exception:
            decoded = (
                raw.replace('\\n', '\n')
                   .replace('\\t', '\t')
                   .replace('\\"', '"')
                   .replace('\\r', '\r')
                   .replace('\\u003c', '<')
                   .replace('\\u003e', '>')
                   .replace('\\u0026', '&')
            )
        chunks_list.append(decoded)

    if not chunks_list:
        return None

    rsc_text = ''.join(chunks_list)
    t_chunks = parse_rsc_t_chunks(rsc_text)
    wiki_pages = parse_wiki_pages(rsc_text)

    if not wiki_pages or not t_chunks:
        return None

    resolved = resolve_wiki_pages(wiki_pages, t_chunks)
    return resolved if resolved else None
