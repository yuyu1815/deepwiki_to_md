# コンテンツ抽出戦略

## HAR 解析から判明した抽出ポイント

### 方法1: RSC レスポンスから T-type チャンクを抽出 (最も確実)

```
優先度: 最高
データソース: text/x-component レスポンス
抽出対象: T-type チャンク (ID:T<hex_len>,<content>)
```

#### 手順

```
1. deepwiki.com/<org>/<repo> に GET リクエスト
   → HTML レスポンスを取得

2. HTML 内から RSC データを探す
   方法A: <script> タグ内の self.__next_f.push([...]) から抽出
   方法B: ?_rsc パラメータ付きで再リクエスト (RSC: 1 ヘッダー)

3. RSC データ内の T-type チャンクをパース
   正規表現: /(\d+):T([0-9a-f]+),/
   → ID, バイト長, コンテンツ開始位置を特定

4. バイト長に基づいてコンテンツを抽出
   → 生の Markdown テキストを取得

5. wiki.pages[] 配列から $<id> 参照を解決
   → ページタイトルと Markdown を紐付け
```

#### 実装のポイント

```python
import re

def parse_rsc_t_chunks(rsc_text):
    """RSC レスポンスから T-type チャンクを抽出"""
    chunks = {}
    pattern = re.compile(r'(\w+):T([0-9a-f]+),')
    
    for match in pattern.finditer(rsc_text):
        chunk_id = match.group(1)
        byte_length = int(match.group(2), 16)
        content_start = match.end()
        content = rsc_text[content_start:content_start + byte_length]
        chunks[chunk_id] = content
    
    return chunks
```

### 方法2: self.__next_f.push() から抽出 (初回 HTML から)

```
優先度: 高
データソース: 初回 HTML レスポンス内の <script> タグ
抽出対象: Next.js フライトデータ
```

#### 手順

```
1. HTML 内の全 <script> タグを検索
2. self.__next_f.push([1, "..."]) パターンを抽出
3. 第2引数の文字列を連結
4. 連結した文字列を RSC 形式としてパース
5. T-type チャンクを方法1と同様に抽出
```

### 方法3: wiki プロパティを JSON として抽出

```
優先度: 中
データソース: RSC レスポンスの React 要素ツリー部分
抽出対象: wiki.pages[] 配列
```

#### 手順

```
1. RSC レスポンス内で "wiki" キーを含む行を検索
2. JSON として部分パース
3. pages[].page_plan から ID とタイトルを取得
4. pages[].content の "$<id>" 参照を T-type チャンクで解決
```

## 現在の deepwiki/ パッケージとの対応

### 既存の抽出戦略

| 戦略クラス | 優先度 | HAR 解析との対応 |
|-----------|--------|-----------------|
| `NextJSPushStrategy` | 90 | 方法2 に対応 (self.__next_f.push) |
| `RSCStreamStrategy` | 85 | 方法1 に対応 (T-type チャンク) |
| `NextJSDataStrategy` | 80 | RSC データの別形式パース |
| `FallbackHTMLStrategy` | 10 | HTML からの直接テキスト抽出 |

### HAR 解析で判明した改善ポイント

```
1. T-type チャンクのバイト長パース
   現状: 行ベースでの分割に依存
   改善: hex バイト長を使った正確な境界検出

2. 全ページ一括取得
   現状: ページごとに個別リクエスト
   改善: 1リクエストで全50ページ取得可能
         (各 RSC レスポンスに全ページが含まれるため)

3. wiki.pages[] の構造化データ活用
   現状: Markdown のみ抽出
   改善: page_plan.id と page_plan.title で
         ファイル名とディレクトリ構造を自動生成

4. メタデータの活用
   現状: 抽出されない
   改善: commit_hash, generated_at を
         出力ファイルに含める
```

## 抽出フロー図

```
[入力: deepwiki.com/<org>/<repo> URL]
    |
    v
[HTTP GET] --- Accept: text/html
    |
    v
[HTML レスポンス (1.47 MB)]
    |
    +-- <script> タグを検索
    |   +-- self.__next_f.push([1, "..."]) を収集
    |
    v
[フライトデータ連結]
    |
    +-- RSC ラインをパース
    |   +-- I-type -> スキップ (import 宣言)
    |   +-- HL-type -> スキップ (プリロードヒント)
    |   +-- T-type -> Markdown 抽出
    |   +-- {...} -> メタデータ抽出
    |   +-- [...] -> wiki.pages[] 構造抽出
    |
    v
[T-type チャンクをマージ]
    |
    +-- チャンク ID <-> ページタイトル対応を解決
    |   ($17 -> "VS Code Codebase Overview")
    |
    v
[ページごとの Markdown ファイル生成]
    |
    +-- 1-vs-code-codebase-overview.md
    +-- 1.1-application-startup-and-process-architecture.md
    +-- 1.2-build-system-and-cicd.md
    +-- ...
```

## HAR から判明した RSC リクエストの再現方法

```python
import requests

url = "https://deepwiki.com/microsoft/vscode/1-vs-code-codebase-overview"
headers = {
    "RSC": "1",
    "Next-URL": "/microsoft/vscode",
    "Accept": "text/x-component",
}
params = {"_rsc": "17i7d"}

response = requests.get(url, headers=headers, params=params)
# response.text -> RSC ストリーム (T-type チャンク含む)
```

ただし、初回 HTML に全データが含まれるため、追加の RSC リクエストは通常不要。
