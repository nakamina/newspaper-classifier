import pathlib
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from classifier.utils import (
    build_model,
    load_dataset,
    preprocess_dataset,
    save_model,
    split_dataset,
    test_model,
    train_model,
)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        """
        `python manage.py train_classifier` を実行するときのコマンドラインオプション
        """
        parser.add_argument(
            "--data-root-dir",
            type=pathlib.Path,
            default=pathlib.Path(__file__).resolve().parents[3] / "data" / "articles",
            help="クローリングしたときに保存したデータのパスの情報",
        )
        parser.add_argument(
            "--label-encoder-save-path",
            type=pathlib.Path,
            default=pathlib.Path(__file__).resolve().parents[3]
            / "data"
            / "label_encoders"
            / "label-encoder.joblib",
            help="教師ラベルを数値化する際に使用する label encoder を保存するパスの情報",
        )
        parser.add_argument(
            "--vectorizer-save-path",
            type=pathlib.Path,
            default=pathlib.Path(__file__).resolve().parents[3]
            / "data"
            / "vectorizers"
            / "count-vectorizer.joblib",
            help="単語列をベクトル化する際に使用する vectorizer を保存するパスの情報",
        )
        parser.add_argument(
            "--model-save-path",
            type=pathlib.Path,
            default=pathlib.Path(__file__).resolve().parents[3]
            / "data"
            / "models"
            / "pretrained-model.joblib",
            help="学習済みの classifier を保存するパスの情報",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        `python manage.py train_classifier` を実行したときに呼び出される関数
        """

        # 1. データの読み込み
        dataset = load_dataset(dataset_dir=options["data_root_dir"])

        # 2. データの train / test への分割
        train_dataset, test_dataset = split_dataset(dataset)

        # 3. データの前処理
        train_dataset, test_dataset = preprocess_dataset(
            train_dataset,
            test_dataset,
            label_encoder_save_path=options["label_encoder_save_path"],
            vectorizer_save_path=options["vectorizer_save_path"],
        )

        # 4. 分類モデルの構築
        model = build_model()

        # 5. 分類モデルの学習
        model = train_model(model, train_dataset)

        # 6. test データを用いたモデルの評価
        model = test_model(model, test_dataset)

        # 7. 学習済み分類器の保存
        save_model(model, options["model_save_path"])
