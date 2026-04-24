# JavaScript チャンク解析

## 全体構成 (36チャンク, 合計 ~4.1 MB)

```
_next/static/chunks/
│
├── Framework/Runtime (4チャンク, ~360 KB)
│   ├── webpack-*.js           [12 KB]  webpack ランタイム
│   ├── main-app-*.js          [570 B]  Next.js App エントリ
│   ├── 18-*.js                [172 KB] Next.js Router/HTTP/Streaming コア
│   └── 87c73c54-*.js          [173 KB] React コア + Framer Motion (アニメーション)
│
├── Vendor/UI ライブラリ (7チャンク, ~1.7 MB)
│   ├── b1298b8d-*.js          [178 KB] Tailwind CSS ユーティリティ
│   ├── 378e5a93-*.js          [120 KB] Tailwind CSS ユーティリティ
│   ├── 9343-*.js              [984 KB] Tailwind + D3.js (★最大チャンク)
│   ├── 7963-*.js              [249 KB] Next.js + シンタックスハイライト + Amplitude SDK
│   ├── 7bf36345-*.js          [70 KB]  汎用ユーティリティ (minified)
│   ├── 37-5126-*.js           [32 KB]  汎用ユーティリティ
│   └── f7f68e2d-*.js          [49 KB]  汎用ユーティリティ
│
├── Markdown/図表レンダリング (5チャンク, ~832 KB)
│   ├── 6182.*.js              [457 KB] Mermaid + KaTeX + Cytoscape + Dagre
│   ├── 3491.*.js              [61 KB]  Mermaid + KaTeX + Dagre
│   ├── 5231-*.js              [169 KB] Octokit (GitHub API SDK) + GraphQL
│   ├── 6450-*.js              [50 KB]  Mermaid + Markdown + シンタックスハイライト
│   └── 261d06ee.*.js          [95 KB]  Markdown + Chart + Icons
│
├── UI コンポーネント (3チャンク, ~118 KB)
│   ├── 1265-*.js              [48 KB]  Radix UI + React Context
│   ├── 29-7982-*.js           [30 KB]  Radix UI (ドロップダウン/ポップオーバー)
│   └── 4222-*.js              [40 KB]  Radix UI + Next.js ルーター
│
├── データフェッチ (2チャンク, ~50 KB)
│   ├── 659-*.js               [13 KB]  TanStack Query (react-query) コア
│   └── 3447.*.js              [37 KB]  データフェッチ補助
│
└── ★ DeepWiki アプリ固有 (11チャンク, ~155 KB)
    ├── layout-0537*.js        [20 KB]  ルートレイアウト (テーマ/フォント)
    ├── layout-a1cc*.js        [8 KB]   サブレイアウト (ヘッダー/Wiki編集)
    ├── page-57cb*.js          [19 KB]  ホームページ (リポジトリ検索UI)
    ├── page-ad06*.js          [1 KB]   小ページコンポーネント
    ├── 4429-*.js              [5 KB]   ★★ クエリ送信コア (最重要)
    ├── 9437-*.js              [13 KB]  リポジトリインデックス管理
    ├── 8904-*.js              [9 KB]   Amplitude イベント + リポジトリUI
    ├── 6375-*.js              [23 KB]  Amplitude + GitHub連携 + Devin AI統合
    ├── 9885-*.js              [34 KB]  チャット/メッセージング
    ├── 18-c16f53c3-*.js       [5 KB]   Dialog/Modal
    └── 28-175-*.js            [17 KB]  グラフ/チャート + React Context
```

## 最重要発見: バックエンドは Devin AI

```
DeepWiki フロントエンド (deepwiki.com)
         │
         │  REST + WebSocket
         │
         ▼
Devin AI バックエンド (api.devin.ai)
         │
         ├── /ada/*  ← "Ada" = Automatic Documentation Agent
         │
         └── Redis Stream ベースのストリーミング配信
```

JS チャンク内で発見された定数:
- `H = "https://api.devin.ai"` — バックエンド API ベース URL
- `K = "https://app.devin.ai"` — Devin AI フロントエンド URL

## バックエンド API エンドポイント一覧

### クエリ系 (ウィキ生成/質問応答)

| Method | エンドポイント | 説明 |
|--------|--------------|------|
| POST | `/ada/query` | クエリ送信 (非同期開始) |
| GET | `/ada/query/{id}` | クエリ結果ポーリング |
| WS | `/ada/ws/query/{id}` | WebSocket ストリーミング |

### リポジトリ管理

| Method | エンドポイント | 説明 |
|--------|--------------|------|
| GET | `/ada/public_repo_indexing_status` | インデックス状態確認 |
| POST | `/ada/index_public_repo` | インデックス開始 |
| POST | `/ada/warm_public_repo` | ウォームアップ |
| GET | `/ada/list_public_indexes` | 公開インデックス一覧 |
| POST | `/ada/public_repo_update_featured_status` | フィーチャー状態更新 |

### 外部 API

| Method | エンドポイント | 説明 |
|--------|--------------|------|
| GET | `api.github.com/repos/{owner}/{repo}` | リポジトリ情報 |
| GET | `api.github.com/repos/{owner}/{repo}/readme` | README 取得 |

## クエリ送信フロー (チャンク 4429 から解析)

```
ユーザーが質問を入力
    │
    ▼
reCAPTCHA トークン取得
  (site key: 6LeK1G0rAAAAAGVDKn-92dkphJzZvEobSLCyZJg4)
    │
    ▼
POST /ada/query
  {
    mode: "MULTIHOP" | "AGENT" | "CODEMAP",
    user_query: "質問テキスト",
    keywords: [...],
    repo_names: ["microsoft/vscode"],
    query_id: "uuid",
    use_notes: true/false,
    source: "ada.deepwiki_public"
  }
    │
    ▼
GET /ada/query/{id} (ポーリング)
  ← { status: "pending" | "processing" | "completed" }
    │
    ├── status == "pending" → 再ポーリング (数秒間隔)
    │
    └── status == "processing" → WebSocket に切り替え
        │
        ▼
WS /ada/ws/query/{id}
  ← { type: "chunk", data: "..." }  (部分結果)
  ← { type: "chunk", data: "..." }
  ← { type: "done" }                (完了)
    │
    ▼
結果を Markdown としてレンダリング
```

## クエリモード

| モード | 説明 | 用途 |
|--------|------|------|
| `MULTIHOP` | 高速マルチホップ検索 (`fast` / `multihop_faster`) | デフォルトの質問応答 |
| `AGENT` | ディープ分析 (`deep` / `omni`) | 複雑な質問への詳細回答 |
| `CODEMAP` | コードマップ生成 | リポジトリ構造の可視化 |

## Amplitude イベント追跡 (チャンク 8904/6375)

| イベント名 | トリガー |
|-----------|----------|
| `wiki_query_sent` | クエリ送信時 |
| `wiki_question_submitted` | 質問送信時 |
| `wiki_mode_switch` | クエリモード切り替え時 |
| `wiki_commit_to_github` | GitHub コミット操作時 |
| `wiki_edit_wiki_click` | ウィキ編集ボタンクリック時 |
| `wiki_open_with_windsurf` | Windsurf で開く操作時 |
| `wiki_preview_generate` | プレビュー生成時 |
| `[Amplitude] Page Viewed` | ページ表示時 |

## リポジトリインデックス管理 (チャンク 9437)

### インデックス状態ポーリング

```
30秒間隔で GET /ada/public_repo_indexing_status?repo_name={name}
    │
    ├── "queued"    → インデックス待ち
    ├── "indexing"  → インデックス処理中
    └── "completed" → 完了 → ポーリング停止
```

### ブロックリスト

以下のリポジトリはブロックされている:
- `bablr-lang/*`
- `lingodotdev/*`
- その他 (JS内にハードコード)

## 図表レンダリングスタック

```
Markdown テキスト
    │
    ├── ```mermaid``` ブロック → Mermaid.js → SVG
    │   ├── graph TD/LR    (有向グラフ)
    │   ├── flowchart TD/LR (フローチャート)
    │   ├── sequenceDiagram (シーケンス図)
    │   └── classDiagram   (クラス図)
    │
    ├── 数式 → KaTeX → HTML
    │
    ├── コードブロック → シンタックスハイライト → HTML
    │
    └── グラフデータ → Cytoscape.js + Dagre → インタラクティブグラフ
                       └── D3.js (SVG レンダリング)
```

## reCAPTCHA によるbot対策

- **タイプ**: reCAPTCHA v3 (invisible)
- **サイトキー**: `6LeK1G0rAAAAAGVDKn-92dkphJzZvEobSLCyZJg4`
- **対象**: `/ada/query` への POST リクエスト
- **バイパス不可**: トークンなしではクエリ送信が拒否される

## 技術スタック更新版

| レイヤー | 技術 |
|----------|------|
| フレームワーク | Next.js App Router (React 18+) |
| スタイル | Tailwind CSS |
| UI コンポーネント | Radix UI |
| アニメーション | Framer Motion |
| データフェッチ | TanStack Query (react-query) |
| GitHub API | Octokit REST SDK |
| 図表 | Mermaid + Cytoscape + Dagre + D3.js |
| 数式 | KaTeX |
| 状態管理 | React Context |
| アナリティクス | Amplitude SDK + Hotjar |
| bot 対策 | reCAPTCHA v3 |
| バックエンド | Devin AI (`api.devin.ai/ada/*`) |
| ストリーミング | WebSocket + Redis Stream |
| ホスティング | Vercel |
