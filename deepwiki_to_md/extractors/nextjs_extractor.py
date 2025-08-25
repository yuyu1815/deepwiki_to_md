"""
Next.js データ抽出システム

DeepwikiサイトのNext.jsアーキテクチャから__NEXT_DATA__スクリプトタグを
抽出し、Markdownコンテンツを取得するための抽出器。
"""

import json
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class ContentResult:
    """コンテンツ抽出結果"""
    content: str
    metadata: Dict[str, Any]
    strategy_used: str
    success: bool
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """コンテンツ検証結果"""
    is_valid: bool
    checks: Dict[str, bool]
    error_message: Optional[str] = None


class NextJSExtractor:
    """Next.jsベースのサイトからMarkdownコンテンツを抽出"""
    
    def __init__(self, timeout: int = 30):
        """
        初期化
        
        Args:
            timeout: HTTP リクエストのタイムアウト時間（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # デフォルトのJSONパス（設定可能）
        self.default_json_paths = [
            "props.pageProps.source.source",
            "props.pageProps.content.markdown", 
            "props.pageProps.mdxSource.compiledSource"
        ]
    
    def extract_content(self, url: str) -> ContentResult:
        """
        指定されたURLからMarkdownコンテンツを抽出
        
        Args:
            url: 抽出対象のURL
            
        Returns:
            ContentResult: 抽出結果
        """
        try:
            # HTMLを取得
            html_content = self._fetch_html(url)
            if not html_content:
                return ContentResult(
                    content="",
                    metadata={},
                    strategy_used="NextJSExtractor",
                    success=False,
                    error="HTMLの取得に失敗しました"
                )
            
            # __NEXT_DATA__を解析
            json_data = self._parse_next_data(html_content)
            if not json_data:
                return ContentResult(
                    content="",
                    metadata={},
                    strategy_used="NextJSExtractor",
                    success=False,
                    error="__NEXT_DATA__の解析に失敗しました"
                )
            
            # Markdownコンテンツを抽出
            markdown_content = self._extract_markdown_from_json(json_data)
            if not markdown_content:
                return ContentResult(
                    content="",
                    metadata={},
                    strategy_used="NextJSExtractor",
                    success=False,
                    error="Markdownコンテンツが見つかりませんでした"
                )
            
            # 検証
            validation = self._validate_markdown(markdown_content)
            if not validation.is_valid:
                return ContentResult(
                    content=markdown_content,
                    metadata={"validation_errors": validation.checks},
                    strategy_used="NextJSExtractor",
                    success=False,
                    error=validation.error_message
                )
            
            # メタデータを抽出
            metadata = self._extract_metadata(json_data)
            
            return ContentResult(
                content=markdown_content,
                metadata=metadata,
                strategy_used="NextJSExtractor",
                success=True
            )
            
        except Exception as e:
            return ContentResult(
                content="",
                metadata={},
                strategy_used="NextJSExtractor",
                success=False,
                error=f"予期しないエラー: {str(e)}"
            )
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """
        指定されたURLからHTMLコンテンツを取得
        
        Args:
            url: 取得対象のURL
            
        Returns:
            str: HTMLコンテンツ、取得に失敗した場合はNone
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException:
            return None
    
    def _parse_next_data(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        HTMLから__NEXT_DATA__スクリプトタグを解析してJSONデータを取得
        
        Args:
            html_content: HTMLコンテンツ
            
        Returns:
            dict: JSONデータ、解析に失敗した場合はNone
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # id="__NEXT_DATA__"のscriptタグを検索
            next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
            if next_data_script and next_data_script.string:
                return json.loads(next_data_script.string)
            
            # 見つからない場合は全scriptタグを検索
            return self._search_next_data_in_scripts(soup)
            
        except (json.JSONDecodeError, Exception):
            return None
    
    def _search_next_data_in_scripts(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        全scriptタグから__NEXT_DATA__パターンを検索
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            dict: JSONデータ、見つからない場合はNone
        """
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.string:
                # __NEXT_DATA__パターンを検索
                if '__NEXT_DATA__' in script.string or 'pageProps' in script.string:
                    try:
                        # JSONとして解析を試行
                        return json.loads(script.string)
                    except json.JSONDecodeError:
                        continue
        
        return None
    
    def _extract_markdown_from_json(self, json_data: Dict[str, Any]) -> Optional[str]:
        """
        JSONデータからMarkdownコンテンツを抽出
        
        Args:
            json_data: __NEXT_DATA__のJSONデータ
            
        Returns:
            str: Markdownコンテンツ、見つからない場合はNone
        """
        # デフォルトパスを試行
        for path in self.default_json_paths:
            content = self._navigate_json_path(json_data, path)
            if content and self._is_valid_markdown(content):
                return content
        
        # 動的検索
        return self._search_markdown_in_json(json_data)
    
    def _navigate_json_path(self, data: Dict[str, Any], path: str) -> Optional[str]:
        """
        指定されたパスでJSONデータを辿る
        
        Args:
            data: JSONデータ
            path: ドット区切りのパス
            
        Returns:
            str: 見つかったコンテンツ、見つからない場合はNone
        """
        try:
            keys = path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            
            return current if isinstance(current, str) else None
            
        except (KeyError, TypeError):
            return None
    
    def _search_markdown_in_json(self, data: Any, max_depth: int = 5, current_depth: int = 0) -> Optional[str]:
        """
        JSONデータ内でMarkdownコンテンツを再帰的に検索
        
        Args:
            data: 検索対象のデータ
            max_depth: 最大検索深度
            current_depth: 現在の深度
            
        Returns:
            str: 見つかったMarkdownコンテンツ、見つからない場合はNone
        """
        if current_depth >= max_depth:
            return None
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and self._is_valid_markdown(value):
                    return value
                elif isinstance(value, (dict, list)):
                    result = self._search_markdown_in_json(value, max_depth, current_depth + 1)
                    if result:
                        return result
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and self._is_valid_markdown(item):
                    return item
                elif isinstance(item, (dict, list)):
                    result = self._search_markdown_in_json(item, max_depth, current_depth + 1)
                    if result:
                        return result
        
        return None
    
    def _is_valid_markdown(self, content: str) -> bool:
        """
        文字列がMarkdownコンテンツかどうかを判定
        
        Args:
            content: 判定対象の文字列
            
        Returns:
            bool: Markdownと判定される場合True
        """
        if not content or len(content) < 50:
            return False
        
        # Markdownの特徴的なパターンをチェック
        markdown_patterns = [
            r'^#\s+.+',  # ヘッダー
            r'^\*\s+.+',  # リスト
            r'^\-\s+.+',  # リスト
            r'```[\s\S]*?```',  # コードブロック
            r'\[.*?\]\(.*?\)',  # リンク
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        return False
    
    def _validate_markdown(self, content: str) -> ValidationResult:
        """
        Markdownコンテンツの品質を検証
        
        Args:
            content: 検証対象のMarkdownコンテンツ
            
        Returns:
            ValidationResult: 検証結果
        """
        checks = {
            'has_headers': bool(re.search(r'^#\s+.+', content, re.MULTILINE)),
            'sufficient_length': len(content) > 100,
            'valid_encoding': self._check_encoding(content),
            'no_html_artifacts': not self._check_html_artifacts(content)
        }
        
        is_valid = all(checks.values())
        error_message = None
        
        if not is_valid:
            failed_checks = [key for key, value in checks.items() if not value]
            error_message = f"検証に失敗: {', '.join(failed_checks)}"
        
        return ValidationResult(
            is_valid=is_valid,
            checks=checks,
            error_message=error_message
        )
    
    def _check_encoding(self, content: str) -> bool:
        """エンコーディングの確認"""
        try:
            content.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
    
    def _check_html_artifacts(self, content: str) -> bool:
        """HTMLアーティファクトの検出"""
        html_patterns = [
            r'<[^>]+>',  # HTMLタグ
            r'&[a-zA-Z]+;',  # HTMLエンティティ
        ]
        
        for pattern in html_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _extract_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSONデータからメタデータを抽出
        
        Args:
            json_data: __NEXT_DATA__のJSONデータ
            
        Returns:
            dict: 抽出されたメタデータ
        """
        metadata = {}
        
        try:
            # ページ情報
            if 'page' in json_data:
                metadata['page'] = json_data['page']
            
            # クエリ情報
            if 'query' in json_data:
                metadata['query'] = json_data['query']
            
            # ビルドID
            if 'buildId' in json_data:
                metadata['buildId'] = json_data['buildId']
                
        except Exception:
            pass
        
        return metadata