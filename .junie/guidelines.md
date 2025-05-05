### Python規約

- 明快・清潔なコード、PEP8遵守（black/flake8）
- withでリソース管理、例外は明示的に捕捉
- Dict/List等はtyping明示
- 継承より合成、関数は短く明確に
- 公開コードは英語docstring、必要部分にテスト
- 可変グローバルはNG、仮想環境推奨
- enumerate()/zip()、内包表記、f-string活用
- dataclass活用、命名規則：snake_case / PascalCase / UPPER_CASE
- 循環import回避、標準ライブラリ優先
- 例外ログ出力、print()は避ける
- 修正は慎重、影響・実行確認を必須
- バグ時は原因・妥当性を分析
- データ行数/バイト数多い場合は処理回避
- コメントは日本語と英語両方
- コードとREADMEはセットで更新
