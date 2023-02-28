import json
import pathlib
from typing import List, Tuple

import joblib
import numpy as np
from natto import MeCab
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def load_dataset(dataset_dir: pathlib.Path) -> List[Tuple[str, str]]:
    category_dir_pathes = [p for p in dataset_dir.iterdir() if p.is_dir()]
    assert len(category_dir_pathes) == 8

    dataset = []
    for category_dir_path in category_dir_pathes:
        article_file_paths = [
            p for p in category_dir_path.iterdir() if p.suffix == ".json"
        ]

        # assert len(article_file_paths) == 100

        for article_file_path in article_file_paths:
            with open(article_file_path, "r") as rf:
                article_dict = json.load(rf)

            data = (article_dict["content"], category_dir_path.name)
            dataset.append(data)

    return dataset


def split_dataset(
    dataset: List[Tuple[str, str]],
    test_size: float = 0.2,
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    train_dataset, test_dataset = train_test_split(dataset, test_size=test_size)
    return train_dataset, test_dataset


def tokenize_text(tagger, article_text: str) -> str:
    # "\n\n" でパラグラフごとに分割される
    article_paragraphs = article_text.split("\n\n")

    tokenized_text = ""
    for paragraph in article_paragraphs:
        tmp_tokenized_text = tagger.parse(paragraph)
        assert len(tmp_tokenized_text) > 0
        tmp_tokenized_text = tmp_tokenized_text.replace("\n", " ")
        tokenized_text += tmp_tokenized_text

    return tokenized_text


def tokenize_dataset(
    train_dataset: List[Tuple[str, str]], test_dataset: List[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    tagger = MeCab("-Owakati")

    train_tokenized_dataset = []
    for train_text, train_category in train_dataset:
        train_tokenized_text = tokenize_text(tagger, train_text)

        train_tokenized_data = (train_tokenized_text, train_category)
        train_tokenized_dataset.append(train_tokenized_data)

    test_tokenized_dataset = []
    for test_text, test_category in test_dataset:
        test_tokenized_text = tokenize_text(tagger, test_text)

        test_tokenized_data = (test_tokenized_text, test_category)
        test_tokenized_dataset.append(test_tokenized_data)

    return (train_tokenized_dataset, test_tokenized_dataset)


def vectorize_dataset(
    train_dataset: List[Tuple[str, str]],
    test_dataset: List[Tuple[str, str]],
    vectorizer_save_path: pathlib.Path,
    label_encoder_save_path: pathlib.Path,
) -> Tuple[List[Tuple[np.ndarray, int]], List[Tuple[np.ndarray, int]]]:
    X_train = [data[0] for data in train_dataset]
    y_train = [data[1] for data in train_dataset]

    X_test = [data[0] for data in test_dataset]
    y_test = [data[1] for data in test_dataset]

    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train).todense()
    X_test_vec = vectorizer.transform(X_test).todense()

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    assert len(X_train_vec) == len(y_train)
    assert len(X_test_vec) == len(y_test)

    train_vec_dataset = []
    for i in range(len(y_train)):
        train_text_vector = X_train_vec[i]
        train_label = y_train[i]
        train_vec_data = (train_text_vector, train_label)
        train_vec_dataset.append(train_vec_data)

    test_vec_dataset = []
    for i in range(len(y_test)):
        test_text_vector = X_test_vec[i]
        test_label = y_test[i]
        test_vec_data = (test_text_vector, test_label)
        test_vec_dataset.append(test_vec_data)

    print(f"Save label encoder to {label_encoder_save_path}")
    joblib.dump(label_encoder, label_encoder_save_path)

    print(f"Save vectorizer to {vectorizer_save_path}")
    joblib.dump(vectorizer, vectorizer_save_path)

    return (train_vec_dataset, test_vec_dataset)  # type: ignore


def preprocess_dataset(
    train_dataset: List[Tuple[str, str]],
    test_dataset: List[Tuple[str, str]],
    label_encoder_save_path: pathlib.Path,
    vectorizer_save_path: pathlib.Path,
):
    train_dataset, test_dataset = tokenize_dataset(
        train_dataset,
        test_dataset,
    )
    train_dataset, test_dataset = vectorize_dataset(  # type: ignore
        train_dataset,
        test_dataset,
        vectorizer_save_path=vectorizer_save_path,
        label_encoder_save_path=label_encoder_save_path,
    )

    return train_dataset, test_dataset


def build_model():
    clf = LogisticRegression(random_state=19950815)
    return clf


def train_model(model, train_dataset):
    X_train = [data[0] for data in train_dataset]
    y_train = [data[1] for data in train_dataset]

    X_train = np.array(X_train).squeeze()

    model = model.fit(X_train, y_train)
    train_acc = model.score(X_train, y_train)
    print(f"訓練時正解率 (Accuracy): {train_acc}")

    return model


def test_model(model, test_dataset):
    X_test = [data[0] for data in test_dataset]
    y_test = [data[1] for data in test_dataset]

    X_test = np.array(X_test).squeeze()

    test_acc = model.score(X_test, y_test)
    print(f"評価時正解率 (Accuracy): {test_acc}")

    return model


def save_model(model, model_save_path: pathlib.Path):
    print(f"Save model to {model_save_path}")
    joblib.dump(model, model_save_path)
