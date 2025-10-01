#!/usr/bin/env python3
"""
Next.js/DeepWiki 由来の HTML/スクリプトから Markdown 風テキストを抽出する拡張可能なツール。

目的:
    複数の抽出戦略（プラグイン可能）で、人間可読なテキストをシンプルに抽出する CLI を提供する。

設計:
    - ストラテジーパターン: NextJS / RSC / フォールバックなど複数方式を切替
    - 設定駆動: Config クラスで調整しやすい
    - 拡張容易: コアを変更せず戦略を追加可能
    - 保守容易: 関心の分離により半年後でも理解しやすい

保守メモ:
    - 戦略を追加する場合: ExtractionStrategy を継承し StrategyManager に登録
    - ヒューリスティック調整: ExtractionConfig の定数を編集
    - 出力拡張: OutputFormatter を拡張
    - HTTP 調整: HTTPConfig の設定を変更

使い方:
    # ローカル HTML ファイルから抽出
    python3 deepwikimd.py sample.html --path ./output

    # URL から抽出
    python3 deepwikimd.py https://deepwiki.com/path --path ./output
"""

import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def normalize_deepwiki_url( raw):
    """DeepWiki用のURLを正規化する。"""
    # パス形式の文字列（/owner/repo or owner/repo）であればURLに変換する
    if raw.startswith("/") or ("/" in raw and " " not in raw):
        return f"https://deepwiki.com/{raw.strip('/')}"
    return raw

# ============================================================================
# 設定クラス（6カ月保守ポイント）/ CONFIGURATION CLASSES (6-month maintenance point)
# ============================================================================

class ExtractionConfig:
    """抽出処理の設定
    
    保守メモ（半年後の自分へ）:
    - 新しいコンテンツ種別に応じて CONTENT_MARKERS を追加
    - 新しいフレームワークに応じて NOISE_PATTERNS を調整
    - パフォーマンスに応じて MIN/MAX_CHUNK_LENGTH を見直し
    """
    
    # コア抽出パターン / Core extraction patterns
    STRING_PAYLOAD_PATTERN = re.compile(
        r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"]\)',
        re.DOTALL
    )
    
    # コンテンツフィルタリング設定 / Content filtering settings
    MIN_CHUNK_LENGTH = 8
    MAX_CHUNK_LENGTH = 10000
    
    # コンテンツ識別マーカー（新しいタイプに応じて拡張）/ Content markers (expand for new content types)
    CONTENT_MARKERS = (
        "# ", "## ", "### ", "#### ",  # Markdown の見出し / headings
        "```",                         # コードブロック / Code blocks
        "Sources:",                    # 参考文献 / References
        "<details", "<summary",        # HTML の詳細表示要素 / details
        "mermaid",                     # ダイアグラム / Diagrams
        "graph ", "flowchart ",        # グラフ記法 / Graph syntax
        "Note:", "Warning:",           # 注記・警告 / Admonitions
        "![", "](http",               # 画像・リンク / Images and links
    )
    
    # ノイズパターン（新しいフレームワークに合わせて拡張）/ Noise patterns (expand for new frameworks)
    NOISE_PATTERNS = (
        "static/chunks",
        "/_next/static",
        "$Sreact",
        "__webpack",
        "module.exports",
        "require(",
        "import {",
    )
    
    # RSC 接頭辞（Next.js の変更に応じて更新）/ RSC prefixes (update for Next.js changes)
    RSC_PREFIXES = ('["%24",', '["$', '["%24%24",')
    
    # フィルタリング用のトークンパターン / Token pattern for filtering
    TOKEN_PATTERN = re.compile(r"[0-9a-z]{1,3}:[A-Za-z0-9]+,")


class HTTPConfig:
    """HTTP 通信の設定
    
    保守メモ（半年後の自分へ）:
    - 新しいユーザーエージェントに合わせて DEFAULT_HEADERS を更新
    - セキュリティのため ALLOWED_DOMAINS を拡張
    - パフォーマンスに応じてタイムアウト値を調整
    """
    
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
    }
    
    # セキュリティ: 許可ドメイン（必要に応じて拡張）/ Security: allowed domains (expand as needed)
    ALLOWED_DOMAINS = (
        "deepwiki.com",
        "*.deepwiki.com",
    )


# ============================================================================
# ユーティリティ関数 / UTILITY FUNCTIONS
# ============================================================================
def sanitize_filename(name: str) -> str:
    """ファイル名として使用可能な文字列へ正規化する。

    引数:
        name: 正規化対象の文字列

    戻り値:
        ファイル名として安全に使用できる文字列
    """
    # スペースをアンダースコアへ置換 / Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # ファイル名として不適切な文字を削除または置換 / Remove or replace invalid characters for filenames
    # このパターンは英数字・アンダースコア・ハイフン・ドットのみを許可 / keeps alphanumeric, underscores, hyphens, dots
    name = re.sub(r'[^\w\-_.]', '', name)
    
    # 空文字列にならないように保証 / Ensure the filename is not empty
    if not name:
        name = "unnamed"
        
    return name


def split_markdown_by_h1(content: str) -> List[Dict[str, str]]:
    """コードブロック内の H1 を無視して、H1 見出しごとに Markdown を分割する。

    引数:
        content: 分割対象の Markdown 文字列

    戻り値:
        'title' と 'content' を持つ辞書のリスト
    """
    # H1 見出し（# ）で分割（ただしコードブロック内は無視）/ Split by H1 headers but ignore those in code blocks
    sections: List[Dict[str, str]] = []
    lines: List[str] = content.split('\n')

    # 現在コードブロック内かどうかを追跡 / Track if inside a code block
    in_code_block: bool = False
    current_section_title: str = "Introduction"
    current_section_content: List[str] = []

    def _append_section_if_needed(title: str, body_lines: List[str]) -> None:
        # 初期セクション(Introduction)で中身が空の場合はスキップ。それ以外は空でも追加する。
        body = '\n'.join(body_lines).strip()
        if title == "Introduction" and body == "":
            return
        sections.append({"title": title, "content": body})

    prev_line: str = ""
    for line in lines:
        # 囲みコードブロック記号を検出（先頭の空白は許容）/ Check for fenced code block markers
        stripped = line.strip()
        is_backtick_fence = stripped != "" and all(ch == '`' for ch in stripped) and len(stripped) >= 2
        is_tilde_fence = stripped != "" and all(ch == '~' for ch in stripped) and len(stripped) >= 3
        if is_backtick_fence or is_tilde_fence:
            in_code_block = not in_code_block
            current_section_content.append(line)
            prev_line = line
            continue

        # セットext形式の H1 を検出（直前行がタイトルで、この行が ==== など）/ Detect Setext H1
        if (
            not in_code_block
            and stripped
            and all(ch == '=' for ch in stripped)
            and prev_line.strip()
        ):
            # 直前のセクションを保存（Introduction で空ならスキップ）
            prev_content_lines = current_section_content[:-1]
            _append_section_if_needed(current_section_title, prev_content_lines)
            # 新しいセクションを開始（タイトルは直前行）
            current_section_title = prev_line.strip()
            current_section_content = []
            prev_line = line
            continue

        # コードブロック外なら ATX 形式の H1（厳密に「# 」）を検出 / Check for ATX H1 headers (exact "# ")
        if not in_code_block and line.startswith("# "):
            # 直前のセクションを保存（Introduction で空ならスキップ）
            _append_section_if_needed(current_section_title, current_section_content)
            # 新しいセクションを開始 / Start a new section
            current_section_title = line[2:].strip()  # 先頭の「# 」を除去 / Remove "# " prefix
            current_section_content = []
        else:
            current_section_content.append(line)
        prev_line = line

    # 最後のセクションを追加（Introduction で空ならスキップ）/ Add the last section (skip empty initial placeholder)
    _append_section_if_needed(current_section_title, current_section_content)

    # 不要な行を除去するため事後処理 / Post-process sections to remove unwanted content
    for section in sections:
        sec_lines = section['content'].split('\n') if section['content'] else []
        filtered_lines: List[str] = []
        skip_details = False

        for l in sec_lines:
            l_strip_lower = l.strip().lower()
            # Skip entire <details> blocks regardless of attributes (e.g., <details open>)
            if l_strip_lower.startswith('<details'):
                skip_details = True
                continue
            elif l_strip_lower.startswith('</details'):
                skip_details = False
                continue
            elif skip_details:
                continue

            # Skip <summary> lines that introduce source file references or similar metadata
            if l_strip_lower.startswith('<summary'):
                # Treat <summary> as non-content metadata; omit from Markdown output.
                continue
            if l.strip().startswith('- [') and l.strip().endswith('.md)'):
                continue

            filtered_lines.append(l)

        section['content'] = '\n'.join(filtered_lines).strip()

    return sections


# ============================================================================
# エラーハンドリング用クラス / ERROR HANDLING CLASSES
# ============================================================================

class ExtractorError(Exception):
    """抽出エラーの基底クラス"""
    pass


class HTTPError(ExtractorError):
    """HTTP 通信に関するエラー"""
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message} for {url}")


class ContentError(ExtractorError):
    """コンテンツ処理に関するエラー"""
    pass


class ConfigError(ExtractorError):
    """設定に関するエラー"""
    pass


# ============================================================================
# 抽出ストラテジーパターン（6カ月保守ポイント）/ EXTRACTION STRATEGY PATTERN (6-month maintenance point)
# ============================================================================

class ExtractionStrategy(ABC):
    """抽出戦略のための抽象基底クラス
    
    保守メモ（半年後の自分へ）:
    1. このクラスを継承して新しい戦略クラスを作成
    2. can_handle() と extract_content() を実装
    3. StrategyManager._register_default_strategies() に登録
    4. 適切な優先度を設定
    """
    
    @abstractmethod
    def can_handle(self, html: str, url: str = None) -> bool:
        """与えられた HTML をこの戦略で処理可能かを判定する"""
        pass
    
    @abstractmethod
    def extract_content(self, html: str, url: str = None) -> str:
        """この戦略を用いてコンテンツを抽出する"""
        pass
    
    def get_priority(self) -> int:
        """戦略の優先度を返す（高いほど優先）"""
        return 50
    
    def get_name(self) -> str:
        """識別用に戦略名を返す"""
        return self.__class__.__name__


class NextJSPushStrategy(ExtractionStrategy):
    """現行の Next.js self.__next_f.push 形式に対する抽出戦略"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "self.__next_f.push" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """self.__next_f.push のペイロードからコンテンツを抽出する"""
        chunks: List[str] = []
        
        for match in ExtractionConfig.STRING_PAYLOAD_PATTERN.finditer(html):
            raw = match.group(1)
            try:
                # JSON 形式のエスケープをデコード / Decode JSON-style escapes
                decoded = json.loads(f'"{raw}"')
            except Exception:
                # フォールバック: 手動置換 / Fallback: manual replacement
                decoded = (
                    raw.replace('\\n', '\n')
                       .replace('\\t', '\t')
                       .replace('\\"', '"')
                       .replace('\\r', '\r')
                       .replace('\\u003c', '<')
                       .replace('\\u003e', '>')
                       .replace('\\u0026', '&')
                )
                
            if self._is_content_chunk(decoded):
                chunks.append(decoded.strip())
        
        # 連続する重複をまとめる / Coalesce consecutive duplicates
        merged: List[str] = []
        for chunk in chunks:
            if not merged or merged[-1] != chunk:
                merged.append(chunk)
                
        return "\n\n".join(merged).strip() + "\n" if merged else ""
    
    def _is_content_chunk(self, s: str) -> bool:
        """ユーザー向けコンテンツらしい文字列かどうかを判定する"""
        if not s:
            return False
            
        t = s.strip()
        
        # Too short
        if len(t) < ExtractionConfig.MIN_CHUNK_LENGTH:
            return False
            
        # Control tokens
        if ExtractionConfig.TOKEN_PATTERN.fullmatch(t):
            return False
            
        # RSC wiring
        if t.startswith(ExtractionConfig.RSC_PREFIXES):
            return False
            
        # Contains content markers
        if any(marker in t for marker in ExtractionConfig.CONTENT_MARKERS):
            return True
            
        # Numeric-prefixed wiring
        if re.match(r"^[0-9]+:", t):
            return False
            
        # Static asset references
        if any(noise in t for noise in ExtractionConfig.NOISE_PATTERNS):
            return False
            
        return False
    
    def get_priority(self) -> int:
        return 90  # Highest priority (current method)


class NextJSDataStrategy(ExtractionStrategy):
    """__NEXT_DATA__ スクリプトタグから抽出する戦略"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "__NEXT_DATA__" in html and "type=\"application/json\"" in html
    
    def extract_content(self, html: str, url: str = None) -> str:
        """__NEXT_DATA__ スクリプトタグからコンテンツを抽出する"""
        match = re.search(
            r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>([^<]+)</script>', 
            html, 
            re.IGNORECASE
        )
        
        if not match:
            return ""
            
        try:
            data = json.loads(match.group(1))
            return self._extract_from_next_data(data)
        except Exception:
            return ""
    
    def _extract_from_next_data(self, data: Dict[str, Any]) -> str:
        """Next.js のデータ構造からコンテンツを抽出する"""
        try:
            # Try common paths
            props = data.get("props", {})
            page_props = props.get("pageProps", {})
            
            # Look for source.source pattern
            if "source" in page_props and isinstance(page_props["source"], dict):
                source_content = page_props["source"].get("source", "")
                if source_content and isinstance(source_content, str):
                    return source_content
                    
            # Look for content field
            content = page_props.get("content", "")
            if content and isinstance(content, str):
                return content
                
            return ""
        except Exception:
            return ""
    
    def get_priority(self) -> int:
        return 80


class RSCStreamStrategy(ExtractionStrategy):
    """React Server Components のストリーミング形式に対する抽出戦略"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return "_rsc=" in (url or "") or re.search(r'^[0-9]+:', html[:1000], re.MULTILINE)
    
    def extract_content(self, html: str, url: str = None) -> str:
        """RSC ストリーム形式からコンテンツを抽出する"""
        lines = html.split('\n')
        content_lines = []
        
        for line in lines:
            # RSC のストリーム行は多くの場合、数字で始まる / RSC stream lines typically start with numbers
            if re.match(r'^[0-9]+:', line):
                # JSON ペイロードがあれば抽出 / Extract JSON payload if present
                try:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        payload = parts[1].strip()
                        if payload.startswith('"') and payload.endswith('"'):
                            decoded = json.loads(payload)
                            if self._is_meaningful_content(decoded):
                                content_lines.append(decoded)
                except Exception:
                    pass
                    
        return "\n\n".join(content_lines) if content_lines else ""
    
    def _is_meaningful_content(self, content: str) -> bool:
        """フレームワークのノイズではなく有意なコンテンツかどうかを判定する"""
        if not content or len(content) < ExtractionConfig.MIN_CHUNK_LENGTH:
            return False
        return any(marker in content for marker in ExtractionConfig.CONTENT_MARKERS)
    
    def get_priority(self) -> int:
        return 85


class FallbackHTMLStrategy(ExtractionStrategy):
    """HTML の title/meta から抽出するフォールバック戦略"""
    
    def can_handle(self, html: str, url: str = None) -> bool:
        return True  # フォールバックとして常に処理可能
    
    def extract_content(self, html: str, url: str = None) -> str:
        """HTML の title と meta から基本的な内容を抽出する"""
        result = []
        
        # title を抽出 / Extract title
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            result.append(f"# {title_match.group(1).strip()}")
            
        # meta description を抽出 / Extract meta description
        meta_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]*)', 
            html, 
            re.IGNORECASE
        )
        if meta_match:
            result.append(f"\n{meta_match.group(1).strip()}")
            
        # twitter:description を抽出 / Extract twitter:description
        twitter_match = re.search(
            r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\'>]*)', 
            html, 
            re.IGNORECASE
        )
        if twitter_match and not meta_match:
            result.append(f"\n{twitter_match.group(1).strip()}")
            
        return "\n".join(result) if result else "# Content extraction failed"
    
    def get_priority(self) -> int:
        return 10  # Lowest priority (fallback)


# ============================================================================
# STRATEGY MANAGER (6-month maintenance focal point)
# ============================================================================

class StrategyManager:
    """抽出戦略を動的に選択して管理するクラス。
    
    保守メモ（半年後の自分へ）:
    - 既定戦略の追加: _register_default_strategies() に追記
    - 失敗する戦略の無効化: disable_strategy()
    - 優先度調整: 各戦略の get_priority() を変更
    - 成果の監視: 必要に応じて統計取得を追加
    """
    
    def __init__(self):
        self.strategies: List[ExtractionStrategy] = []
        self.disabled_strategies: set = set()
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """既定の抽出戦略を登録する
        
        保守メモ（半年後の自分へ）: 新しい戦略はここに追加
        """
        self.add_strategy(NextJSPushStrategy())
        self.add_strategy(NextJSDataStrategy())
        self.add_strategy(RSCStreamStrategy())
        self.add_strategy(FallbackHTMLStrategy())
    
    def add_strategy(self, strategy: ExtractionStrategy):
        """新しい抽出戦略を追加する"""
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: s.get_priority(), reverse=True)
    
    def disable_strategy(self, strategy_name: str):
        """戦略名を指定して無効化する"""
        self.disabled_strategies.add(strategy_name)
    
    def enable_strategy(self, strategy_name: str):
        """無効化した戦略を再度有効化する"""
        self.disabled_strategies.discard(strategy_name)
    
    def extract_content(self, html: str, url: str = None) -> str:
        """利用可能な最良の戦略でコンテンツを抽出する"""
        strategies = self.strategies
        
        # 優先度順に戦略を試す / Try strategies in priority order
        for strategy in strategies:
            name = strategy.get_name()
            
            if name in self.disabled_strategies:
                continue
                
            if strategy.can_handle(html, url):
                result = self._try_extract(strategy, html, url)
                if result.strip():  # 非空の結果なら返す / Non-empty result
                    return result
                    
        return "# No suitable extraction strategy found"
    
    def _try_extract(self, strategy: ExtractionStrategy, html: str, url: str = None) -> str:
        """特定の戦略で抽出を試み、必要に応じて統計やログを更新する"""
        try:
            return strategy.extract_content(html, url)
        except Exception as e:
            logging.warning(f"Strategy {strategy.get_name()} failed: {e}")
            return ""


# ============================================================================
# 中核クラス / CORE CLASSES
# ============================================================================

class HTTPClient:
    """HTTP 通信の処理を担当するクラス
    
    保守メモ（半年後の自分へ）:
    - __init__ にプロキシ対応を追加
    - _create_request() に認証対応を実装
    - fetch_url() にキャッシュ層を追加
    """
    
    def __init__(self, timeout: float = None, headers: Dict[str, str] = None):
        self.timeout = timeout or HTTPConfig.DEFAULT_TIMEOUT
        self.headers = headers or HTTPConfig.DEFAULT_HEADERS.copy()
    
    def fetch_url(self, url: str) -> str:
        """URL から HTML を取得（エラーハンドリング付き）"""
        if not self._is_valid_url(url):
            raise HTTPError(url, 0, "Invalid URL format")
            
        request = self._create_request(url)
        
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return self._process_response(response)
        except Exception as e:
            raise HTTPError(url, 0, str(e))
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 形式と安全性を検証する"""
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    
    def _create_request(self, url: str) -> Request:
        """適切なヘッダーを付与して HTTP リクエストを作成する"""
        return Request(url, headers=self.headers)
    
    def _process_response(self, response) -> str:
        """HTTP 応答を処理し、エンコーディングを考慮してデコードする。
        
        ネストを浅く保つため、圧縮解除は小さな関数に分離し、
        早期リターン（ガード節）で読みやすさを担保する。
        """
        data = response.read()

        def _decompress(data_bytes: bytes, enc: str) -> bytes:
            enc = (enc or "").lower().strip()
            if not enc:
                return data_bytes

            # br (Brotli)
            if enc == "br":
                try:
                    import brotli
                    return brotli.decompress(data_bytes)
                except Exception:
                    return data_bytes

            # gzip / x-gzip
            if enc in ("gzip", "x-gzip"):
                try:
                    import gzip
                    return gzip.decompress(data_bytes)
                except Exception:
                    return data_bytes

            # deflate (zlib/raw)
            if enc == "deflate":
                try:
                    import zlib
                    return zlib.decompress(data_bytes)
                except Exception:
                    try:
                        import zlib as _z
                        return _z.decompress(data_bytes, -_z.MAX_WBITS)
                    except Exception:
                        return data_bytes

            return data_bytes

        # 圧縮を処理する / Handle compression
        data = _decompress(data, response.headers.get("Content-Encoding"))

        # 文字セットを判定する / Determine charset
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")


class OutputFormatter:
    """複数形式に対応した出力フォーマッタ
    
    保守メモ（半年後の自分へ）:
    - format_content() に JSON 出力を追加
    - YAML 出力のサポートを検討
    - カスタムテンプレートへの対応
    """
    
    def __init__(self, format_type: str = "markdown"):
        self.format_type = format_type
    
    def format_content(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """指定された種類に基づいてコンテンツを整形する"""
        if self.format_type == "markdown":
            return self._format_markdown(content, metadata)
        else:
            return content
    
    def _format_markdown(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Markdown として整形（メタデータは任意）"""
        result = []
        
        if metadata:
            result.append("---")
            for key, value in metadata.items():
                result.append(f"{key}: {value}")
            result.append("---")
            result.append("")
        
        result.append(content)
        return "\n".join(result)


def save_markdown_to_library(md: str, source_url: str, base_dir: str = ".deepwiki") -> Dict[str, Any]:
    """Split Markdown by H1 and save as files under .deepwiki/<username>/<library>/.
    
    - Also creates/overwrites a library index file: .deepwiki/<username>/<library>.md
    - Returns a dict with paths and metadata.
    - Raises ConfigError if source_url does not include /<username>/<library>.
    
    Parameters:
        md: The markdown content extracted from a DeepWiki/Next.js page.
        source_url: The original URL used for extraction (used to derive save path).
        base_dir: Base directory for saving outputs (default: ".deepwiki").
    
    Note:
        The source_url is normalized via normalize_deepwiki_url() so that
        path-like inputs such as "owner/repo" or "/owner/repo" also work.
        DeepWiki full URLs and non-DeepWiki full URLs are preserved as-is per policy.
    """
    if not source_url:
        raise ConfigError("source_url is required to determine save location")
    # Normalize according to shared policy (no-op for full deepwiki URLs and non-deepwiki URLs)
    normalized_url = normalize_deepwiki_url(source_url)
    try:
        parsed_url = urlparse(normalized_url)
    except Exception as e:
        raise ConfigError(f"Invalid source_url: {e}")
    path_parts = [p for p in (parsed_url.path or "").split('/') if p]
    if len(path_parts) < 2:
        raise ConfigError("source_url must include '/<username>/<library>' path components")
    username, library_name = path_parts[0], path_parts[1]

    output_dir = os.path.join(base_dir, username, library_name)
    os.makedirs(output_dir, exist_ok=True)

    sections = split_markdown_by_h1(md)
    saved_files: List[str] = []
    for section in sections:
        title = section["title"]
        section_content = section["content"]
        filename = sanitize_filename(title) + ".md"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(section_content)
        saved_files.append(file_path)

    library_file_path = os.path.join(base_dir, username, f"{library_name}.md")
    with open(library_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {library_name} Documentation Index\n\n")
        f.write("This file contains links to all extracted documents.\n")
        f.write("Please refer to the files below for detailed information.\n\n")
        for file_path in saved_files:
            filename = os.path.basename(file_path)
            title = filename[:-3].replace('_', ' ')
            f.write(f"- [{title}]({library_name}/{filename})\n")

    logging.info("Saved %d sections under %s", len(saved_files), output_dir)
    return {
        "username": username,
        "library_name": library_name,
        "output_dir": output_dir,
        "saved_files": saved_files,
        "library_file": library_file_path,
    }


class ContentExtractor:
    """コンテンツ抽出のオーケストレーター。"""
    
    def __init__(self, strategy_manager: StrategyManager = None, 
                 http_client: HTTPClient = None):
        self.strategy_manager = strategy_manager or StrategyManager()
        self.http_client = http_client or HTTPClient()
    
    def extract_from_url(self, url: str) -> str:
        """URL からコンテンツを抽出する。"""
        normalized = normalize_deepwiki_url(url)
        html = self.http_client.fetch_url(normalized)
        return self.extract_from_html(html, normalized)
    
    def extract_from_html(self, html: str, url: str = None) -> str:
        """HTML 文字列からコンテンツを抽出する。"""
        raw_content = self.strategy_manager.extract_content(html, url)
        metadata = {"extraction_url": url} if url else None
        formatter = OutputFormatter()
        return formatter.format_content(raw_content, metadata)

# ============================================================================
# メインエントリーポイント / MAIN ENTRY POINT
# ============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """Backward-compatible entrypoint that delegates to cli.main()."""
    from cli import main as cli_main
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())