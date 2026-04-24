# 外部サービス連携

## 1. GitHub API

### エンドポイント

```
GET https://api.github.com/repos/microsoft/vscode/readme
Accept: application/vnd.github.v3+json
```

### 認証

認証なし。GitHub の公開 API レート制限 (60 req/hour per IP) に依存。

### レスポンス構造

```json
{
  "name": "README.md",
  "path": "README.md",
  "sha": "abc123...",
  "size": 12345,
  "url": "https://api.github.com/repos/microsoft/vscode/contents/README.md",
  "html_url": "https://github.com/microsoft/vscode/blob/main/README.md",
  "content": "base64エンコードされたREADME内容...",
  "encoding": "base64",
  "_links": {
    "self": "...",
    "git": "...",
    "html": "..."
  }
}
```

### 用途

リポジトリのREADME内容をウィキページのコンテキストとして使用。
CORS リクエスト (ブラウザから直接呼び出し) で取得される。

## 2. Amplitude アナリティクス

### 設定取得

```
GET https://sr-client-cfg.amplitude.com/config
```

3回呼び出されている (初期化、セッションリプレイ、追加設定)。

### イベント送信

```
POST https://api2.amplitude.com/2/httpapi
Content-Type: application/json
```

### 送信データ

```json
{
  "api_key": "31817a083e6793ab0c94e295885d7021",
  "events": [
    {
      "device_id": "...",
      "session_id": 1234567890,
      "event_type": "[Amplitude] Page Viewed",
      "platform": "Web",
      "language": "ja",
      "event_properties": {
        "page_domain": "deepwiki.com",
        "page_location": "https://deepwiki.com/microsoft/vscode",
        "page_path": "/microsoft/vscode",
        "page_title": "DeepWiki"
      }
    }
  ]
}
```

### 追跡イベント

| イベント | トリガー |
|----------|----------|
| `[Amplitude] Page Viewed` | ページ表示時 |
| セッションリプレイ | ユーザー操作の録画 |

### CORS プリフライト

```
OPTIONS https://api2.amplitude.com/2/httpapi
→ 200 (Access-Control-Allow-Origin 確認)
→ POST (実際のイベント送信)
```

## 3. Hotjar セッション録画

### スクリプト読み込み

```
GET https://static.hotjar.com/c/hotjar-6382967.js
```

- サイト ID: `6382967`
- 機能: ユーザー操作のセッション録画・ヒートマップ
- 追加モジュール: hotjar-modules スクリプト (233 KB)

### 動作

```
ページロード → Hotjar スクリプト初期化
                    │
                    ├── DOM 変更の監視
                    ├── マウス/クリック/スクロール追跡
                    ├── フォーム入力追跡
                    └── セッションデータを Hotjar サーバーに送信
```

## 4. Vercel ホスティング

### 確認されたヘッダー

```
Server: Vercel
X-Vercel-Cache: HIT / MISS
X-Vercel-Id: iad1::xxxxx-1234567890
```

### キャッシュ戦略

```
Cache-Control: public, max-age=0, must-revalidate
ETag: W/"m8h3cop20evkfs"
```

- `max-age=0, must-revalidate`: 毎回 ETag で再検証
- `X-Vercel-Cache: HIT`: Vercel Edge Cache からの配信
- Vary ヘッダーにより RSC/非RSC で異なるキャッシュエントリ

### CDN 動作

```
ブラウザ → Vercel Edge (最寄りのPoP)
              │
              ├── Cache HIT → キャッシュから即座に返却
              │                (ETag が一致する場合)
              │
              └── Cache MISS → Origin (Next.js サーバー)
                                  │
                                  └── レスポンス生成 → Edge にキャッシュ → 返却
```

## 5. 通信フロー全体図

```
[ブラウザ]
    │
    ├──── deepwiki.com (Vercel) ──────────────────┐
    │     ├── HTML (初回)                          │
    │     ├── RSC (ページ遷移)                     │ Next.js App Router
    │     ├── Static Assets (JS/CSS/fonts)         │
    │     └── favicon.ico                          │
    │                                              │
    ├──── api.github.com ─────────────────────────┐
    │     └── /repos/{owner}/{repo}/readme         │ 公開 API (認証なし)
    │                                              │
    ├──── api2.amplitude.com ─────────────────────┐
    │     └── /2/httpapi (POST)                    │ イベント追跡
    │                                              │
    ├──── sr-client-cfg.amplitude.com ────────────┐
    │     └── /config (GET)                        │ 設定取得
    │                                              │
    └──── static.hotjar.com ──────────────────────┐
          └── /c/hotjar-*.js                       │ セッション録画
```

## 6. セキュリティ特性

| 項目 | 状態 |
|------|------|
| 認証 | なし (完全公開) |
| Cookie | なし |
| CORS | GitHub API + Amplitude で使用 |
| CSP | 確認されず |
| HTTPS | 全通信で使用 |
| API キー露出 | Amplitude API キーがクライアントに露出 (仕様通り) |
