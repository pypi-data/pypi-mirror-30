# Python tool for SAKURA Secure Mobile Connect

## What is this

このツールは、 [さくらのクラウド](https://cloud.sakura.ad.jp/) のAPIを利用して、
[セキュアモバイルコネクト](https://www.sakura.ad.jp/services/sim/) のSIMを管理するためのPythonツールです。

SIMの登録、有効化、無効化、登録解除などができます。

## How To use

* [ドキュメント](https://hitsumabushi.github.io/python-sakura-secure-mobile-connect/index.html)
* [PyPI](https://pypi.org/project/ssmc/)

### Install

```
$ pip install ssmc
```

### Usage

```python
import ssmc

api = ssmc.APIClient(token=_token_, secret=_secret_, zone="is1b")
# List MGWs
mgws, _ = api.list_mgws()
print(mgws)
```

# 開発者向けメモ

## テストについて

さくらのクラウドのテスト用のゾーン(tk1v) がセキュアモバイルコネクトに対応していないようなので、
ひとまず、プライベートリポジトリで実際のICCIDなどを使ってテストしています。

## ドキュメント

```
$ pip install -r requirements-dev.txt
$ cd docs
$ make html
```
