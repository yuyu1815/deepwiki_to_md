"""
JSONパス解析ユーティリティ

JSONデータ内の複雑な階層構造を効率的にナビゲートし、
Markdownコンテンツを動的に検索するためのユーティリティ。
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable


class JSONPathNavigator:
    """JSON階層パス解析とナビゲーション"""
    
    def __init__(self):
        """初期化"""
        self.search_cache = {}
    
    def navigate_path(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        """
        指定されたパスでJSONデータを辿る
        
        Args:
            data: JSONデータ
            path: ドット区切りのパス（例: "props.pageProps.source.source"）
            
        Returns:
            Any: 見つかったデータ、見つからない場合はNone
        """
        try:
            keys = self._parse_path(path)
            current = data
            
            for key in keys:
                current = self._navigate_single_key(current, key)
                if current is None:
                    return None
            
            return current
            
        except Exception:
            return None
    
    def _parse_path(self, path: str) -> List[str]:
        """
        パス文字列を解析してキーのリストに変換
        
        Args:
            path: パス文字列
            
        Returns:
            List[str]: キーのリスト
        """
        # 配列インデックスもサポート（例: "data[0].items"）
        parts = []
        current_part = ""
        
        i = 0
        while i < len(path):
            char = path[i]
            
            if char == '.':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif char == '[':
                # 配列インデックス処理
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                
                # ]までの内容を取得
                end_bracket = path.find(']', i)
                if end_bracket != -1:
                    index_str = path[i+1:end_bracket]
                    try:
                        # 数値インデックスの場合
                        int(index_str)
                        parts.append(f"[{index_str}]")
                    except ValueError:
                        # 文字列キーの場合
                        parts.append(index_str.strip('"\''))
                    i = end_bracket
                else:
                    current_part += char
            else:
                current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def _navigate_single_key(self, data: Any, key: str) -> Optional[Any]:
        """
        単一のキーでデータをナビゲート
        
        Args:
            data: 現在のデータ
            key: キー（配列インデックスも含む）
            
        Returns:
            Any: 次のデータ、見つからない場合はNone
        """
        if data is None:
            return None
        
        # 配列インデックスの処理
        if key.startswith('[') and key.endswith(']'):
            try:
                index = int(key[1:-1])
                if isinstance(data, list) and 0 <= index < len(data):
                    return data[index]
            except (ValueError, IndexError):
                pass
            return None
        
        # 辞書のキーアクセス
        if isinstance(data, dict):
            return data.get(key)
        
        return None
    
    def search_by_pattern(
        self, 
        data: Any, 
        pattern: str, 
        max_depth: int = 10,
        value_filter: Optional[Callable[[Any], bool]] = None
    ) -> List[tuple]:
        """
        パターンマッチングによる検索
        
        Args:
            data: 検索対象のデータ
            pattern: 検索パターン（正規表現）
            max_depth: 最大検索深度
            value_filter: 値のフィルタ関数
            
        Returns:
            List[tuple]: (パス, 値) のタプルのリスト
        """
        results = []
        pattern_regex = re.compile(pattern, re.IGNORECASE)
        
        def _search_recursive(current_data: Any, current_path: str, depth: int):
            if depth >= max_depth:
                return
            
            if isinstance(current_data, dict):
                for key, value in current_data.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    
                    # キーがパターンにマッチする場合
                    if pattern_regex.search(key):
                        if value_filter is None or value_filter(value):
                            results.append((new_path, value))
                    
                    # 再帰的に検索
                    _search_recursive(value, new_path, depth + 1)
            
            elif isinstance(current_data, list):
                for i, item in enumerate(current_data):
                    new_path = f"{current_path}[{i}]" if current_path else f"[{i}]"
                    _search_recursive(item, new_path, depth + 1)
        
        _search_recursive(data, "", 0)
        return results
    
    def find_markdown_paths(self, data: Dict[str, Any]) -> List[str]:
        """
        Markdownコンテンツが格納されている可能性のあるパスを検索
        
        Args:
            data: JSONデータ
            
        Returns:
            List[str]: 候補パスのリスト
        """
        # Markdownを示唆するキーパターン
        markdown_patterns = [
            r'source',
            r'markdown',
            r'content',
            r'mdx',
            r'body',
            r'text'
        ]
        
        candidate_paths = []
        
        for pattern in markdown_patterns:
            results = self.search_by_pattern(
                data, 
                pattern,
                value_filter=lambda v: isinstance(v, str) and len(v) > 100
            )
            
            for path, value in results:
                if self._is_potential_markdown(value):
                    candidate_paths.append(path)
        
        return candidate_paths
    
    def _is_potential_markdown(self, content: str) -> bool:
        """
        文字列がMarkdownである可能性を判定
        
        Args:
            content: 判定対象の文字列
            
        Returns:
            bool: Markdownの可能性がある場合True
        """
        if not isinstance(content, str) or len(content) < 50:
            return False
        
        # Markdownの特徴的なパターン
        markdown_indicators = [
            r'^#{1,6}\s+.+$',  # ヘッダー
            r'^\*\s+.+$',      # リスト
            r'^\-\s+.+$',      # リスト
            r'^\d+\.\s+.+$',   # 番号付きリスト
            r'```[\s\S]*?```', # コードブロック
            r'`[^`]+`',        # インラインコード
            r'\[.+?\]\(.+?\)', # リンク
            r'!\[.*?\]\(.+?\)', # 画像
        ]
        
        score = 0
        for pattern in markdown_indicators:
            if re.search(pattern, content, re.MULTILINE):
                score += 1
        
        # 2つ以上のパターンにマッチした場合はMarkdownと判定
        return score >= 2
    
    def extract_with_fallback_paths(
        self, 
        data: Dict[str, Any], 
        primary_paths: List[str],
        fallback_search: bool = True
    ) -> Optional[str]:
        """
        複数のパスでコンテンツ抽出を試行し、フォールバック検索も実行
        
        Args:
            data: JSONデータ
            primary_paths: 優先パスのリスト
            fallback_search: フォールバック検索を実行するかどうか
            
        Returns:
            str: 見つかったコンテンツ、見つからない場合はNone
        """
        # 優先パスで検索
        for path in primary_paths:
            content = self.navigate_path(data, path)
            if content and isinstance(content, str) and self._is_potential_markdown(content):
                return content
        
        # フォールバック検索
        if fallback_search:
            candidate_paths = self.find_markdown_paths(data)
            for path in candidate_paths:
                content = self.navigate_path(data, path)
                if content and isinstance(content, str):
                    return content
        
        return None
    
    def get_path_info(self, data: Dict[str, Any], path: str) -> Dict[str, Any]:
        """
        指定されたパスの詳細情報を取得
        
        Args:
            data: JSONデータ
            path: パス
            
        Returns:
            dict: パス情報（存在確認、データ型、サイズなど）
        """
        content = self.navigate_path(data, path)
        
        info = {
            'exists': content is not None,
            'path': path,
            'type': type(content).__name__ if content is not None else None,
            'is_string': isinstance(content, str),
            'length': len(content) if hasattr(content, '__len__') else None,
            'is_potential_markdown': False
        }
        
        if isinstance(content, str):
            info['is_potential_markdown'] = self._is_potential_markdown(content)
        
        return info
    
    def debug_structure(self, data: Any, max_depth: int = 3, current_path: str = "") -> Dict[str, Any]:
        """
        JSONデータ構造をデバッグ用に分析
        
        Args:
            data: 分析対象のデータ
            max_depth: 最大分析深度
            current_path: 現在のパス
            
        Returns:
            dict: 構造分析結果
        """
        def _analyze_recursive(current_data: Any, path: str, depth: int) -> Dict[str, Any]:
            if depth >= max_depth:
                return {"type": type(current_data).__name__, "truncated": True}
            
            analysis = {
                "type": type(current_data).__name__,
                "path": path
            }
            
            if isinstance(current_data, dict):
                analysis["keys"] = list(current_data.keys())
                analysis["children"] = {}
                for key, value in current_data.items():
                    new_path = f"{path}.{key}" if path else key
                    analysis["children"][key] = _analyze_recursive(value, new_path, depth + 1)
            
            elif isinstance(current_data, list):
                analysis["length"] = len(current_data)
                analysis["sample_items"] = []
                for i, item in enumerate(current_data[:3]):  # 最初の3項目のみ
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    analysis["sample_items"].append(_analyze_recursive(item, new_path, depth + 1))
            
            elif isinstance(current_data, str):
                analysis["length"] = len(current_data)
                analysis["preview"] = current_data[:100] + "..." if len(current_data) > 100 else current_data
                analysis["is_potential_markdown"] = self._is_potential_markdown(current_data)
            
            return analysis
        
        return _analyze_recursive(data, current_path, 0)