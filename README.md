# deepwiki-to-md

Next.js/DeepWiki 由来のHTMLからMarkdownテキストを抽出するゼロ依存のCLIツール。

- CLI: `deepwiki-to-md`
- 必要要件: Python 3.7+
- 依存関係: 標準ライブラリのみ（オプション機能は extras）

## インストール

```bash
pip install deepwiki-to-md
```

## 使い方

- ローカルHTMLから:
```bash
echo "<html>...</html>" | deepwiki-to-md
```

- URLから:
```bash
deepwiki-to-md https://example.com/page --path ./.deepwiki
```

## ライセンス

MIT License
