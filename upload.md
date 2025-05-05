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
    testpypi

[pypi]
username = your_username
password = your_password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password
```

このファイルを`~/.pypirc`に配置することで、twineでのアップロード時にユーザー名とパスワードの入力を省略できます。

## 注意点

現在のPythonパッケージングのベストプラクティスとしては、`twine`を使ったアップロードが推奨されています。`setup.py upload`
は安全でない通信を使うため、推奨されていません。ただし、パッケージのビルド自体は`setup.py`を使って行うことができます。

```

Markdownファイルとして保存したい場合は、この内容を `.md` 拡張子のファイルに貼り付けて保存してください。  
必要なら、ファイル形式でお渡しすることもできます。保存用にファイルを出力しましょうか？
```
