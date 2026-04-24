# RSC (React Server Components) プロトコル詳細

## 概要

DeepWiki は Next.js App Router の RSC プロトコルを使用してウィキコンテンツを配信する。
レスポンスの Content-Type は `text/x-component` で、行ベースのシリアライゼーション形式を使用する。

## RSC ライン形式

各行は `<ID>:<TYPE><DATA>` の形式:

```
<hex_id>:<type_prefix><payload>
```

### ラインタイプ一覧

| タイプ接頭辞 | 名称 | 説明 | 例 |
|-------------|------|------|-----|
| `"$S..."` | Symbol | React 特殊シンボル参照 | `1:"$Sreact.fragment"` |
| `I[...]` | Import | Client Component の import 宣言 | `2:I[49138,["9453","static/chunks/b12..."],""]` |
| `T<hex>,` | Text | 生テキストコンテンツ (バイト長指定) | `17:T47ed,# VS Code...` |
| `{...}` | Object | JSON オブジェクト (ルーター状態等) | `0:{"P":null,"b":"ry-Te..."}` |
| `[...]` | Array | React 要素配列 | `5:["$","$L15",null,{...}]` |
| `:HL[...]` | Hint/Link | プリロードヒント (font/CSS) | `:HL["/_next/static/...","font",{...}]` |
| `null` | Null | null 値 | `c:null` |

## T-type チャンク (コンテンツ配信の核心)

### 形式

```
<hex_id>:T<hex_byte_length>,<raw_content>
```

- `hex_id`: チャンク識別子 (16進数)
- `T`: Text チャンクであることを示す接頭辞
- `hex_byte_length`: コンテンツのバイト長 (16進数)
- `raw_content`: 生の Markdown テキスト (改行含む)

### 例

```
17:T47ed,# VS Code Codebase Overview

<details>
<summary>Relevant source files</summary>
The following files were used as context...
</details>

## Architecture Overview
...
```

ここで:
- `17` = チャンクID (16進数で 0x17 = 23)
- `T47ed` = コンテンツ長 (0x47ed = 18,413 バイト)
- カンマ以降 = 生の Markdown テキスト

### T-type チャンクの連結

T-type チャンクはバイト長で区切られるため、改行ではなくバイト数で次のチャンクの開始位置が決まる:

```
...Sources: [file.ts:1-159]()18:T58ca,# Next Page Title
                              ↑
                              前のチャンクのバイト長が尽きた地点で
                              次のチャンクが即座に開始
```

### チャンクID と ページの対応

```
ID (hex) → ID (dec) → ページ
0x17     → 23       → Page 1 (VS Code Codebase Overview)
0x18     → 24       → Page 2 (Application Startup...)
0x19     → 25       → Page 3 (Build System...)
...
0x48     → 72       → Page 50 (最終ページ)
```

全50ページが連続する T-type チャンクとして1つの RSC レスポンスに含まれる。

## RSC ルート構造 (line 0)

```json
{
  "P": null,
  "b": "ry-TefxPpKznsBkWnL6Qu",
  "p": "",
  "c": ["", "microsoft", "vscode", "1-vs-code-codebase-overview"],
  "i": false,
  "f": [["...", {...}]],
  "S": "..."
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `P` | null | Prefetch フラグ |
| `b` | string | Next.js ビルドID |
| `p` | string | パスプレフィックス |
| `c` | string[] | ルートパスセグメント `["", org, repo, page-slug]` |
| `i` | boolean | インタラクティブフラグ |
| `f` | array | React ツリー子要素定義 |
| `S` | string | サーバー状態 |

## I-type (Client Component Import)

```
2:I[49138,["9453","static/chunks/b1298b8d-abc123.js?dpl=xyz"],""]
```

| 部分 | 説明 |
|------|------|
| `49138` | webpack モジュール ID |
| `["9453","static/chunks/..."]` | チャンク ID + JS ファイルパス |
| `""` | エクスポート名 (空 = default export) |
| `?dpl=xyz` | Vercel デプロイメント識別子 |

## HL-type (プリロードヒント)

```
:HL["/_next/static/media/font.woff2","font",{"crossOrigin":"","type":"font/woff2"}]
:HL["/_next/static/css/style.css","style"]
```

ブラウザにフォントやCSSの事前読み込みを指示する。

## React 要素ツリー

RSC レスポンスの後半部分に React コンポーネントツリーが含まれる:

```
5:["$","$L15",null,{"repoName":"microsoft/vscode","hasConfig":false,"canSteer":true,"wiki":{"metadata":{...},"pages":[...]}}]
```

### wiki プロパティの構造

```json
{
  "wiki": {
    "metadata": {
      "repo_name": "microsoft/vscode",
      "commit_hash": "ca3b9bfb",
      "generated_at": "2026-04-16T05:58:02.235259",
      "config": null,
      "config_source": "none"
    },
    "pages": [
      {
        "page_plan": {
          "id": "1",
          "title": "VS Code Codebase Overview"
        },
        "content": "$17"
      },
      {
        "page_plan": {
          "id": "1.1",
          "title": "Application Startup and Process Architecture"
        },
        "content": "$18"
      }
    ]
  }
}
```

### content 参照の仕組み

```
pages[0].content = "$17"  →  T-type チャンク ID 0x17 の内容を参照
pages[1].content = "$18"  →  T-type チャンク ID 0x18 の内容を参照
...

"$<id>" は RSC の内部参照構文で、
同一レスポンス内の対応する ID のチャンクデータを指す
```

## RSC レスポンスの全体構造

```
行番号    内容
────────────────────────────────
  0       ルート構造 (パス情報、ビルドID)
  1       React Fragment シンボル定義
  2-15    I-type: Client Component import 宣言
          HL-type: フォント/CSS プリロードヒント
  16      ルーターパラメータ (org/repo/page)
  17-23   メタ情報、レイアウト構造
  24      T-type 開始: Page 1 の Markdown
  ...     T-type 連続: Page 2-50 の Markdown
  ~16780  React 要素ツリー (wiki プロパティ含む)
  ~16786  最終行
```
