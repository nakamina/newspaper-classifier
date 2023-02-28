import pathlib
from typing import Any

import streamlit.web.bootstrap
from django.core.management.base import BaseCommand, CommandParser
from streamlit import config as st_config


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        """
        `python manage.py predict` を実行するときのコマンドラインオプション
        """
        parser.add_argument(
            "--script-path",
            type=str,
            default=str(pathlib.Path(__file__).resolve().parents[2] / "streamlit.py"),
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8501,
        )
        parser.add_argument(
            "--model-save-path",
            type=str,
            default=str(
                pathlib.Path(__file__).resolve().parents[3]
                / "data"
                / "models"
                / "pretrained-model.joblib"
            ),
        )
        parser.add_argument(
            "--label-encoder-save-path",
            type=str,
            default=str(
                pathlib.Path(__file__).resolve().parents[3]
                / "data"
                / "label_encoders"
                / "label-encoder.joblib"
            ),
        )
        parser.add_argument(
            "--vectorizer-save-path",
            type=str,
            default=str(
                pathlib.Path(__file__).resolve().parents[3]
                / "data"
                / "vectorizers"
                / "count-vectorizer.joblib"
            ),
        )

    def handle(self, *args: Any, **options: Any):
        """
        `python manage.py predict` を実行したときに呼び出される関数

        streamlit は通常、対象スクリプトのパスを指定して以下のように実行する:
        `streamlit run hogehoge.py`
        今回は django のカスタムコマンドを通して streamlit server を起動したいため、
        以下のように `streamlit.web.bootstrap.run` 関数を通してスクリプトを実行する。
        """
        # streamlit のポート番号の設定
        st_config.set_option("server.port", options["port"])

        # streamlit server を起動する
        # `main_script_path` に対象となる streamlit.py を渡している
        # - /path/to/newspaper-classifier/predictor/streamlit.py
        #
        # その他、コマンドラインオプションとして、以下の3つを与えている:
        # - model-save-path
        # - label-encoder-save-path
        # - vectorizer-save-path
        streamlit.web.bootstrap.run(
            main_script_path=options["script_path"],
            command_line="",
            args=[
                "--model-save-path",
                options["model_save_path"],
                "--label-encoder-save-path",
                options["label_encoder_save_path"],
                "--vectorizer-save-path",
                options["vectorizer_save_path"],
            ],
            flag_options={},
        )
