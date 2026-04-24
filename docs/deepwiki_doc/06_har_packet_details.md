# HAR パケット詳細一覧

## 全67リクエストの分類と詳細

### カテゴリ A: 初回ページロード

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 0 | GET | `deepwiki.com/microsoft/vscode` | 200 | 1.47 MB | text/html |

### カテゴリ B: 静的アセット (フォント)

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 1 | GET | `_next/static/media/*.woff2` | 200 | ~30 KB | font/woff2 |
| 2 | GET | `_next/static/media/*.woff2` | 200 | ~30 KB | font/woff2 |

### カテゴリ C: 静的アセット (CSS)

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 3 | GET | `_next/static/css/*.css` | 200 | ~76 KB | text/css |
| 4 | GET | `_next/static/css/*.css` | 200 | ~77 KB | text/css |

### カテゴリ D: JavaScript チャンク (初期)

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 5-32 | GET | `_next/static/chunks/*.js` | 200 | 各 5-500 KB | application/javascript |

28個の webpack コード分割チャンク。主要なもの:
- `main-app-*.js`: メインアプリケーションバンドル
- `webpack-*.js`: webpack ランタイム
- `framework-*.js`: React + Next.js フレームワーク
- `[hash].js`: 各コンポーネント/機能のチャンク

### カテゴリ E: アナリティクス

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 33 | GET | `static.hotjar.com/c/hotjar-6382967.js` | 200 | 15 KB | application/javascript |
| 35 | GET | `static.hotjar.com/.../hotjar-modules-*.js` | 200 | 233 KB | application/javascript |
| 36 | GET | `sr-client-cfg.amplitude.com/config` | 200 | 616 B | application/json |
| 44 | GET | `sr-client-cfg.amplitude.com/config` | 200 | 616 B | application/json |
| 47 | GET | `sr-client-cfg.amplitude.com/config` | 200 | 616 B | application/json |
| 50 | GET | `sr-client-cfg.amplitude.com/config` | 200 | 616 B | application/json |
| 58 | POST | `api2.amplitude.com/2/httpapi` | 200 | 92 B | application/json |
| 59 | OPTIONS | `api2.amplitude.com/2/httpapi` | 200 | 0 | - |

### カテゴリ F: RSC (React Server Components) レスポンス

| # | Method | URL (ページスラッグ) | Status | Size | Next-URL |
|---|--------|---------------------|--------|------|----------|
| 34 | GET | `/?_rsc=17i7d` (ホーム) | 200 | 7.5 KB | / |
| 39 | GET | `1-vs-code-codebase-overview` | 200 | 1,172,514 | /microsoft/vscode |
| 40 | GET | `1.1-application-startup-and-process-architecture` | 200 | 1,172,928 | /microsoft/vscode |
| 41 | GET | `1.2-build-system-and-cicd` | 200 | 1,172,657 | /microsoft/vscode |
| 42 | GET | `2-core-editor-(monaco)` | 200 | 1,172,630 | /microsoft/vscode |
| 43 | GET | `2.1-text-model-and-view-model` | 200 | 1,172,700 | /microsoft/vscode |
| 48 | GET | `2.2-editor-widget-configuration-and-minimap` | 200 | 1,172,878 | /microsoft/vscode |
| 51 | GET | `2.3-inline-completions-and-editor-contributions` | 200 | 1,172,916 | /microsoft/vscode |
| 52 | GET | `3-extension-system` | 200 | 1,172,574 | /microsoft/vscode |
| 53 | GET | `3.1-extension-host-architecture-and-protocol` | 200 | 1,172,890 | /microsoft/vscode |
| 54 | GET | `3.2-vs-code-extension-api` | 200 | 1,172,652 | /microsoft/vscode |
| 56 | GET | `3.3-extension-marketplace-and-management` | 200 | 1,172,832 | /microsoft/vscode |
| 57 | GET | `4-workbench-shell` | 200 | 1,172,567 | /microsoft/vscode |
| 60 | GET | `4.1-layout-and-parts-system` | 200 | 1,172,676 | /microsoft/vscode |
| 61 | GET | `4.2-window-management-and-titlebar` | 200 | 1,172,760 | /microsoft/vscode |
| 62 | GET | `4.3-views-tree-controls-and-ui-primitives` | 200 | 1,172,854 | /microsoft/vscode |

### カテゴリ G: 追加 JavaScript チャンク

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 37-38, 45-46, 55, 63-65 | GET | `_next/static/chunks/*.js` | 200 | 各 5-200 KB | application/javascript |

ページ遷移に伴い動的にロードされるコンポーネントチャンク。

### カテゴリ H: GitHub API

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 49 | GET | `api.github.com/repos/microsoft/vscode/readme` | 200 | 10 KB | application/json |

### カテゴリ I: その他

| # | Method | URL | Status | Size | Content-Type |
|---|--------|-----|--------|------|-------------|
| 66 | GET | `deepwiki.com/favicon.ico` | 200 | 26 KB | image/x-icon |

## リクエスト統計

```
カテゴリ別リクエスト数:
  A. 初回ページロード:      1  (  1.5%)
  B. フォント:              2  (  3.0%)
  C. CSS:                   2  (  3.0%)
  D. JS チャンク (初期):   28  ( 41.8%)
  E. アナリティクス:        8  ( 11.9%)
  F. RSC レスポンス:       16  ( 23.9%)
  G. JS チャンク (追加):    8  ( 11.9%)
  H. GitHub API:            1  (  1.5%)
  I. その他:                1  (  1.5%)
  ────────────────────────────────
  合計:                    67  (100.0%)
```

```
カテゴリ別データ転送量:
  F. RSC レスポンス:   ~18.7 MB  ( 74.2%)  ← 大部分
  D. JS チャンク:       ~3.5 MB  ( 13.9%)
  A. HTML:              ~1.5 MB  (  6.0%)
  E. アナリティクス:    ~0.25 MB (  1.0%)
  G. 追加 JS:          ~0.6 MB   (  2.4%)
  C. CSS:              ~0.15 MB  (  0.6%)
  B. フォント:         ~0.06 MB  (  0.2%)
  H. GitHub API:       ~0.01 MB  (  0.0%)
  I. その他:           ~0.03 MB  (  0.1%)
  ────────────────────────────────
  合計:                ~25.2 MB  (100.0%)
```

## 重要な観察

1. **RSC が全データ転送の 74% を占める**: ウィキコンテンツ配信が通信の大部分
2. **各 RSC レスポンスは ~1.17 MB で均一**: 全ページのデータを毎回転送 (冗長)
3. **16回の RSC リクエストで ~18.7 MB**: 実質的に同じ ~1.1 MB のデータを16回転送
4. **効率改善の余地**: ページ差分のみ配信すれば大幅に削減可能
5. **JS チャンクは効率的**: コード分割 + キャッシュにより適切なサイズ
