# DeepWiki 内部アーキテクチャ概要

## HARファイル解析結果サマリ

- 対象URL: `https://deepwiki.com/microsoft/vscode`
- HARファイルサイズ: 25.2 MB
- 総リクエスト数: 67
- 解析日: 2026-04-24

## 全体アーキテクチャ

```
[ブラウザ]
  │
  ├── 初回ロード
  │   GET /microsoft/vscode → HTML (1.47 MB)
  │   ├── CSS (153 KB, 2ファイル)
  │   ├── JS  (3.5 MB, ~28チャンク)
  │   └── Fonts (60 KB, woff2)
  │
  ├── ページ遷移 (RSC)
  │   GET /microsoft/vscode/<page-slug>?_rsc=17i7d
  │   ├── Header: RSC: 1
  │   ├── Header: Next-URL: /microsoft/vscode
  │   └── Response: text/x-component (~1.1 MB)
  │       └── 全50ページの Markdown を T-type チャンクで配信
  │
  ├── GitHub API
  │   GET api.github.com/repos/microsoft/vscode/readme
  │   └── リポジトリ README (base64)
  │
  └── アナリティクス
      ├── Amplitude (イベント追跡 + セッションリプレイ)
      └── Hotjar (セッション録画)
```

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| フレームワーク | Next.js App Router (React 18+) |
| レンダリング | React Server Components (RSC) |
| ホスティング | Vercel |
| コンテンツ配信 | RSC ストリーミング (text/x-component) |
| 圧縮 | Brotli (br) |
| 外部API | GitHub REST API v3 |
| アナリティクス | Amplitude + Hotjar |
| 認証 | なし (完全ステートレス) |

## リクエスト分類 (全67リクエスト)

| カテゴリ | 件数 | 合計サイズ | 説明 |
|----------|------|-----------|------|
| 初回HTML | 1 | 1.47 MB | メインページ SSR |
| RSC (wiki) | 16 | ~18.7 MB | React Server Component レスポンス |
| JS チャンク | ~28 | ~3.5 MB | webpack コード分割バンドル |
| CSS | 2 | ~153 KB | スタイルシート |
| フォント | 2 | ~60 KB | woff2 |
| GitHub API | 1 | 10 KB | README 取得 |
| Amplitude | 6 | ~2 KB | 設定 + イベント送信 |
| Hotjar | 2 | ~248 KB | セッション録画スクリプト |
| その他 | 9 | ~150 KB | favicon, プリフェッチ等 |

## 重要な発見

1. **全ページ一括配信**: 各RSCレスポンス (~1.1MB) に全50ページ分の Markdown が含まれる
2. **サーバーサイドレンダリング不要**: 初回以降はRSCプロトコルでクライアント側レンダリング
3. **認証不要**: Cookie・トークン一切なし。GitHub APIも未認証
4. **キャッシュ戦略**: `public, max-age=0, must-revalidate` + ETag
5. **ビルドID管理**: RSCレスポンスに `"b":"ry-TefxPpKznsBkWnL6Qu"` でバージョン管理
