

## AI Assistant

# setup.pyを使ったPythonパッケージの公開方法

setup.pyを直接使用してPythonパッケージを公開する方法もあります。以下にその手順を説明します。

## setup.pyを使ってPyPIに公開する手順

### 1. 必要なツールのインストール

まず、パッケージング関連のツールをインストールします：

```shell
pip install setuptools wheel twine
```

### 2. 配布用パッケージの作成

setup.pyを使って配布用のパッケージを作成します：

```shell
python setup.py sdist bdist_wheel
```

これにより`dist/`ディレクトリに以下のファイルが作成されます：

* `.tar.gz`形式のソースディストリビューション
* `.whl`形式のホイールパッケージ

### 3. PyPIへのアップロード

作成したパッケージをtwineを使ってアップロードします：

#### テスト環境（TestPyPI）へのアップロード（推奨）

```shell
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

#### 本番環境（PyPI）へのアップロード

```shell
twine upload dist/*
```

### 4. 直接register/uploadコマンドを使う方法（非推奨）

以前は以下のようなコマンドも使われていましたが、セキュリティ上の理由から現在は非推奨です：

```shell
python setup.py register
python setup.py sdist upload
```

## 準備と確認事項

1. **setup.pyの内容確認**：

    * バージョン番号が適切か
    * 作者情報が正しいか
    * 依存関係が正確に記載されているか

2. **PyPIアカウント**：

    * PyPIで事前にアカウント登録が必要です
    * `~/.pypirc`ファイルにユーザー情報を記載しておくと便利です

3. **バージョン管理**：

    * 既に公開したバージョンと同じバージョン番号で再アップロードはできません
    * 更新時は必ずバージョン番号を上げてください

## `.pypirc`ファイルの設定例

```
[distutils]
index-servers =
    pypi
    deepwiki-to-md

[pypi]
username = __token__
password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

[deepwiki-to-md]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

このファイルを`~/.pypirc`に配置することで、twineでのアップロード時にユーザー名とパスワードの入力を省略できます。

- username は必ず `__token__`
- password は PyPI で発行したプロジェクトトークン（`pypi-` で始まる文字列）

## トークンを使ったアップロード（環境変数方式）

`~/.pypirc` を作らずとも、環境変数だけでアップロード可能です。

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD='pypi-...（発行されたトークン）'

# TestPyPI へ
python -m build  # または make build
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 本番 PyPI へ
python -m twine upload dist/*
```

## GitHub Actions による自動公開

本リポジトリには、タグ `v*` の push もしくは Release Publish をトリガーに PyPI へ公開するワークフローを追加しています。

- ワークフロー: `.github/workflows/publish.yml`
- 必要なリポジトリシークレット: `PYPI_API_TOKEN`（PyPI のプロジェクトトークン）
- 使い方:
  1. GitHub リポジトリの Settings → Secrets and variables → Actions → New repository secret で `PYPI_API_TOKEN` を登録
  2. リリースしたいコミットにタグを付与して push（例: `git tag v2.0.2 && git push origin v2.0.2`）
  3. もしくは GitHub の Release を Publish すると自動実行

## Makefile ヘルパー

開発者ローカル用に簡易ターゲットを用意しています。

```bash
# ビルド
make build

# PyPI へアップロード（TWINE_PASSWORD にトークンを設定しておく）
export TWINE_PASSWORD='pypi-...'
make upload

# TestPyPI へアップロード
export TWINE_PASSWORD='pypi-...（TestPyPI トークン）'
make upload-test
```

## 注意点

現在のPythonパッケージングのベストプラクティスとしては、`twine`を使ったアップロードが推奨されています。`setup.py upload`
は安全でない通信を使うため、推奨されていません。ただし、パッケージのビルド自体は`setup.py`を使って行うことができます。

また、トークンはリポジトリにコミットせず、ローカルでは `~/.pypirc` または環境変数、CI では GitHub Secrets に保存してください。