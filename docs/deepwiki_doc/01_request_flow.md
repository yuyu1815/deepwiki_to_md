# リクエストフロー詳細解析

## 1. 初回ページロード

### リクエスト
```
GET /microsoft/vscode HTTP/2
Host: deepwiki.com
Accept: text/html,application/xhtml+xml,...
Accept-Encoding: gzip, deflate, br, zstd
Cache-Control: no-cache
```

### レスポンス
```
HTTP/2 200
Content-Type: text/html; charset=utf-8
Content-Encoding: br
Cache-Control: public, max-age=0, must-revalidate
ETag: W/"m8h3cop20evkfs"
Server: Vercel
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch
X-Vercel-Cache: HIT
```

### 処理フロー
```
ブラウザ → Vercel Edge → Next.js SSR
                            │
                            ├── HTML 生成 (1.47 MB)
                            │   ├── <head> メタ情報 + preload hints
                            │   ├── <body> 初期 React ツリー
                            │   └── <script> ハイドレーション用データ
                            │
                            └── 静的アセット参照
                                ├── /_next/static/css/*.css (2ファイル)
                                ├── /_next/static/chunks/*.js (28ファイル)
                                └── /_next/static/media/*.woff2 (2ファイル)
```

## 2. ページ遷移 (RSC ナビゲーション)

### リクエスト
```
GET /microsoft/vscode/1-vs-code-codebase-overview?_rsc=17i7d HTTP/2
Host: deepwiki.com
RSC: 1
Next-URL: /microsoft/vscode
Next-Router-State-Tree: [エンコードされた状態ツリー]
Next-Router-Prefetch: 1
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Priority: i
```

### レスポンス
```
HTTP/2 200
Content-Type: text/x-component
Content-Encoding: br
Cache-Control: public, max-age=0, must-revalidate
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch
```

### RSC ヘッダーの役割

| ヘッダー | 値 | 役割 |
|----------|-----|------|
| `RSC` | `1` | RSC レスポンスを要求するフラグ |
| `Next-URL` | `/microsoft/vscode` | 現在のルートレイアウトコンテキスト |
| `Next-Router-State-Tree` | `[encoded]` | クライアント側ルーター状態 (差分計算用) |
| `Next-Router-Prefetch` | `1` | プリフェッチリクエストであることを示す |
| `_rsc` (query) | `17i7d` | RSC リクエスト識別子/トークン |

### ナビゲーションの仕組み
```
ユーザーがサイドバーのリンクをクリック
    │
    ▼
Next.js クライアントルーター
    │
    ├── URL を pushState で更新
    ├── RSC: 1 ヘッダー付きで GET リクエスト
    │
    ▼
Vercel Edge / Next.js サーバー
    │
    ├── RSC ヘッダーを検出
    ├── HTML ではなく RSC ストリームを返す
    │
    ▼
クライアント
    │
    ├── RSC ストリームをパース
    ├── React ツリーを差分更新
    └── 対象ページのコンテンツのみ DOM に反映
```

## 3. 全リクエストタイムライン

```
時刻  リクエスト
─────────────────────────────────────────
 t0   GET /microsoft/vscode (HTML)
 t1   GET /_next/static/media/*.woff2 (フォント × 2)
 t2   GET /_next/static/css/*.css (CSS × 2)
 t3   GET /_next/static/chunks/*.js (JS × 28)
 t4   GET /hotjar-*.js (Hotjar)
 t5   GET /?_rsc=17i7d (ホーム RSC)
 t6   GET /amplitude/config (× 3)
 t7   GET /_next/static/chunks/*.js (追加 JS)
 t8   GET /microsoft/vscode/1-vs-code-codebase-overview?_rsc (RSC)
 t9   GET /microsoft/vscode/1.1-...?_rsc (RSC)
 t10  GET /microsoft/vscode/1.2-...?_rsc (RSC)
 ...  (以下、ユーザーのページ遷移に応じて RSC リクエスト)
 t16  GET api.github.com/repos/microsoft/vscode/readme
 t17  POST api2.amplitude.com/2/httpapi (イベント送信)
```

## 4. Vary ヘッダーによるキャッシュ分岐

```
同一 URL に対して:
  ├── RSC: 1 なし → HTML レスポンス (初回ロード / 直接アクセス)
  └── RSC: 1 あり → text/x-component レスポンス (クライアント遷移)

Vercel Edge Cache は Vary ヘッダーに基づき
RSC 有無で異なるキャッシュエントリを保持
```

## 5. レスポンスサイズの特徴

各RSCレスポンスは約 1.17 MB で均一。これは**全50ページの Markdown が毎回含まれる**ため。
ページ固有のコンテンツは数十 KB だが、全ページバンドルにより各レスポンスが大きくなっている。

```
RSC レスポンスサイズ分布:
  Entry 39: 1,172,514 bytes
  Entry 40: 1,172,928 bytes
  Entry 41: 1,172,657 bytes
  ...
  Entry 62: 1,172,854 bytes
  (差分: ±500 bytes 程度 = ほぼ同一コンテンツ)
```
