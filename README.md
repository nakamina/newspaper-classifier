# ニュース記事を分類くん 🐶

[![CI](https://github.com/nakamina/newspaper-classifier/actions/workflows/ci.yaml/badge.svg)](https://github.com/nakamina/newspaper-classifier/actions/workflows/ci.yaml)

![](https://user-images.githubusercontent.com/11523725/221865809-dc936a0b-e791-458a-b99d-b726d33e04d7.png)

## 全体像

本プロジェクトは [`django`](https://github.com/django/django) をベースとした 3 つのアプリケーションから構成されている。これらのアプリケーションは [django の custom command](https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/) を利用して実装されている：

- [`crawler`](https://github.com/nakamina/newspaper-classifier/tree/master/crawler) app.
  - [gunosy.com](https://gunosy.com/) からニュース記事を取得する君
- [`classifier`](https://github.com/nakamina/newspaper-classifier/tree/master/classifier) app.
  - `crawler` で取得した記事を元にカテゴリを予測する分類器を学習させる君
- [`predictor`](https://github.com/nakamina/newspaper-classifier/tree/master/predictor) app.
  - `classifier` で学習させた分類器を元に 記事 URL からカテゴリを予測する君

## 使用している主要ライブラリ

### 環境構築関連

- [poetry](https://github.com/python-poetry/poetry)
  - python の依存関係やパッケージ配布の管理を簡素化するパッケージマネージャ
  - プロジェクトの依存関係を簡単に指定、インストール、管理し、公開するための配布ファイルを生成することが可能

### 開発支援関連

- [flake8](https://github.com/PyCQA/flake8)
  - python コードに含まれる文法エラーやコーディングスタイル違反などの問題をチェックする code linter
- [black](https://github.com/psf/black)
  - python コードを一貫したスタイルガイドに沿って自動的に再フォーマットし、読みやすく、保守しやすくする code formatter
- [isort](https://github.com/PyCQA/isort)
  - python の import 文を PEP8 ガイドラインに従って自動的にソートし、一貫した方法で整理するライブラリ
- [mypy](https://github.com/python/mypy)
  - mypy は Python 用の静的型チェッカーで、コードが実行される前に一般的なエラーやバグを検出するのに役立つ

### Web フレームワーク

- [django](https://github.com/django/django)
  - 安全でスケーラブルなウェブアプリケーションを迅速に開発できる高水準のウェブフレームワーク
  - model/view/controller (MVC) のアーキテクチャパターンに従っている
  - object relational mapper (ORM) やテンプレートエンジン、認証システムなどの様々な組み込み機能を有している

### `crawler` app. 関連

- [requests](https://github.com/psf/requests)
  - python のコードで HTTP リクエストを行うプロセスを簡素化する、幅広く利用されているサードパーティーライブラリ
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
  - HTML や XML 文書からデータを抽出する Web スクレイピングの目的で使用されるサードパーティライブラリ

### `classifier` app. 関連

- [numpy](https://github.com/numpy/numpy)
  - python で科学計算やデータ解析に使用されるサードパーティモジュール
- [scikit-learn](https://github.com/scikit-learn/scikit-learn)
  - データマイニングやデータ分析のための効率的で使いやすいツールを提供する python 用のサードパーティ製機械学習ライブラリ
- [natto-py](https://github.com/buruzaemon/natto-py)
  - Python と日本語の品詞・形態素解析ツール [MeCab](https://taku910.github.io/mecab/) を組み合わせたパッケージ
- [joblib](https://github.com/joblib/joblib)
  - Python の軽量パイプラインに使用されるサードパーティモジュール。今回は学習した機械学習モデルを保存するために使用

### `predictor` app. 関連

- [streamlit](https://github.com/streamlit/streamlit)
  - Python でインタラクティブなデータサイエンス・アプリケーションを作成するために使用される
- [lime](https://github.com/marcotcr/lime)
  - 機械学習モデルの予測値を説明するための Lime（Local Interpretable Model-Agnostic Explanations）ライブラリ

### その他関連するライブラリ

- pathlib
- dataclass
- typing
- argparse

## セットアップの仕方

- 本レポジトリを clone する

```shell
git clone https://github.com/nakamina/newspaper-classifier
cd newspaper-classifier
```

- python の環境を用意する

```shell
pyenv virtualenv 3.9.9 newspaper-classifier-dev
pyenv local newspaper-classifier-dev
```

- poetry を使って依存ライブラリをインストールする

```shell
pip install -U pip wheel setuptools poetry
poetry install
```

## 本プロジェクト `ニュース記事分類くん` を動かす

### 学習用のニュース記事を収集する

- 以下の django custom command である [`crawl`](https://github.com/nakamina/newspaper-classifier/blob/master/crawler/management/commands/crawl.py) コマンドを実行する。
- このコマンドで呼ばれている実装は [crawler/utils.py](https://github.com/nakamina/newspaper-classifier/blob/master/crawler/utils.py) を参照

- デフォルトの設定

```shell
python manage.py crawl
```

- オプションを使って詳細を設定

```shell
python manage.py crawl \
    --base-url https://gunosy.com \
    --data-root-dir ./data/articles
```

### ニュース記事分類くんを訓練する

- 以下の django custom command である [`train_classifier`](https://github.com/nakamina/newspaper-classifier/blob/master/classifier/management/commands/train_classifier.py) コマンドを実行する。
- このコマンドで呼ばれている実装は [classifier/utils.py](https://github.com/nakamina/newspaper-classifier/blob/master/classifier/utils.py) を参照

- デフォルトの設定

```shell
python manage.py train_classifier
```

- オプションを使って詳細を設定

```shell
python manage.py train_classifier \
    --data-root-dir ./data/articles \
    --label-encoder-save-path ./data/label_encoders \
    --vectorizer-save-path ./data/vectorizers/ \
    --model-save-path ./data/models/
```

### ニュース記事分類くんウェブアプリを動かす

- 以下の django custom command である [`predict`](https://github.com/nakamina/newspaper-classifier/blob/master/predictor/management/commands/predict.py) コマンドを用いてニュース記事分類くんのウェブアプリを動かす。
- このコマンドで呼ばれている実装は [predictor/utils.py](https://github.com/nakamina/newspaper-classifier/blob/master/predictor/utils.py) を参照

- デフォルトの設定

```shell
python manage.py predict
```

- オプションを使って詳細を設定

```shell
python manage.py predict \
    --script-path ./predictor/streamlit.py \
    --port 8501 \
    --label-encoder-save-path ./data/label_encoders \
    --vectorizer-save-path ./data/vectorizers/ \
    --model-save-path ./data/models/

#   You can now view your Streamlit app in your browser.

#   Local URL: http://localhost:8501
#   Network URL: http://172.20.10.8:8501

#   For better performance, install the Watchdog module:

#   $ xcode-select --install
#   $ pip install watchdog

# Load model from /Users/nakamina/ghq/github.com/nakamina/newspaper-classifier/data/models/pretrained-model.joblib
# Load label encoder from /Users/nakamina/ghq/github.com/nakamina/newspaper-classifier/data/label_encoders/label-encoder.joblib
# Load vectorizer from /Users/nakamina/ghq/github.com/nakamina/newspaper-classifier/data/vectorizers/count-vectorizer.joblib
```

## GitHub Actions による CI

CI を GitHub Actions で構築している。以下はその内容である：
- black によるコードフォーマットの確認
- flake8 による文法エラー、コーディング規約の確認
- mypy による型チェック

## ToDo

- [ ] django の custom command を使わない場合の実装
- [ ] django の ORM を使って crawl したデータを DB へ格納
  - [ ] HTML どうやって保持しておくか問題
- [ ] pathlib vs. os.path 検証
- [ ] 入力特徴の検討
  - [ ] 単語 vs. 文字 検証
  - [ ] 入力文全体 vs. 名詞のみ 検証
  - [ ] ベクトル化手法 (count vectorizer, etc.)
- [ ] 機械学習モデルの検討
  - [ ] ロジスティック回帰以外
  - [ ] 各条件化で比較した際の機械学習モデルの予測性能の評価
- [ ] Web アプリケーション
  - [ ] LIME 以外にも機械学習モデルの予測の解釈手法の検討    
