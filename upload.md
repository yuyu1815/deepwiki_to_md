# PyPI 公開手順

パッケージ設定はルートの `pyproject.toml` に集約されています。ローカルでは配布物の確認までを行い、PyPI への公開は GitHub Actions の trusted publishing を使用します。

## ローカルビルド

```bash
python -m pip install --upgrade build
python -m build
```

生成された wheel と source distribution は `dist/` に出力されます。

## PyPI 公開

公開ワークフローは `.github/workflows/publish.yml` の 1 本です。GitHub Release を publish すると、次の処理を行います。

1. `python -m build` で配布物を作成する。
2. build artifact を publish job に渡す。
3. PyPI trusted publishing（OIDC）で公開する。

GitHub の `pypi` environment と PyPI 側の trusted publisher を、対象リポジトリ・ワークフロー `publish.yml`・environment `pypi` に対応させて設定してください。API token や `TWINE_PASSWORD` は不要です。

同じバージョンは再公開できないため、Release 作成前に `pyproject.toml` のバージョンを更新してください。
