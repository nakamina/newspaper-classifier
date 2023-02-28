import argparse
import pathlib
import sys
from typing import Tuple

import joblib
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from lime.lime_text import LimeTextExplainer
from natto import MeCab
from sklearn.pipeline import make_pipeline

from classifier.utils import tokenize_text
from crawler.utils import scrape_article_content

st.set_page_config(layout="wide")

tagger = MeCab("-Owakati")
tagger.parse("")


def load_model(model_save_path: pathlib.Path):
    print(f"Load model from {model_save_path}")
    return joblib.load(model_save_path)


def load_label_encoder(label_encoder_save_path: pathlib.Path):
    print(f"Load label encoder from {label_encoder_save_path}")
    return joblib.load(label_encoder_save_path)


def load_vectorizer(vectorizer_save_path: pathlib.Path):
    print(f"Load vectorizer from {vectorizer_save_path}")
    return joblib.load(vectorizer_save_path)


def get_article_content(url: str) -> str:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    return scrape_article_content(soup)


def predict_category(
    article_text, model, label_encoder, vectorizer
) -> Tuple[int, str, float]:
    tokenized_text = tokenize_text(tagger, article_text)

    X = vectorizer.transform([tokenized_text]).todense()
    X = np.array(X)

    y_pred_probas = model.predict_proba(X)
    y_pred = y_pred_probas.argmax()

    y_pred_label, *_ = label_encoder.inverse_transform([y_pred])
    y_pred_proba = y_pred_probas[:, y_pred][0]

    return y_pred, y_pred_label, y_pred_proba


def apply_lime(
    article_text,
    model,
    vectorizer,
    label_encoder,
    y_pred,
):
    tokenized_text = tokenize_text(tagger, article_text)

    pipe = make_pipeline(vectorizer, model)
    explainer = LimeTextExplainer(
        class_names=label_encoder.classes_,
    )

    exp = explainer.explain_instance(
        text_instance=tokenized_text,
        classifier_fn=pipe.predict_proba,
        num_features=10,
        labels=[y_pred],
    )
    html = exp.as_html()
    components.html(html, height=800)


def run_streamlit(model, label_encoder, vectorizer):
    st.title("ニュース記事のカテゴリ予測くん🐶")
    url = st.text_input("記事 URL:", value="")

    if len(url) != 0:
        article_text = get_article_content(url)
        y_pred, y_pred_label, y_pred_proba = predict_category(
            article_text, model, label_encoder, vectorizer
        )

        st.markdown(
            f"""
        ### 📰 入力された記事 URL
        - {url}

        ### 🤖 予測カテゴリ
        - カテゴリ
            - **{y_pred_label}**
        - 確信度
            - **{y_pred_proba:.3f}**

        """
        )
        apply_lime(
            article_text=article_text,
            model=model,
            vectorizer=vectorizer,
            label_encoder=label_encoder,
            y_pred=y_pred,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-save-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[3]
        / "data"
        / "models"
        / "prtrained-model.joblib",
    )
    parser.add_argument(
        "--label-encoder-save-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[3]
        / "data"
        / "label_encoders"
        / "label-encoder.joblib",
    )
    parser.add_argument(
        "--vectorizer-save-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[3]
        / "data"
        / "vectorizers"
        / "count-vectorizer.joblib",
    )
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args()

    model = load_model(
        model_save_path=args.model_save_path,
    )
    label_encoder = load_label_encoder(
        label_encoder_save_path=args.label_encoder_save_path,
    )
    vectorizer = load_vectorizer(
        vectorizer_save_path=args.vectorizer_save_path,
    )
    run_streamlit(model, label_encoder, vectorizer)


if __name__ == "__main__":
    main()
