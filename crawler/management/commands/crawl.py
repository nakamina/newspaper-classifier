import pathlib
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from crawler.utils import crawl_all_articles, save_articles


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        """
        `python manage.py crawl` を実行するときのコマンドラインオプション
        """

        parser.add_argument(
            "--base-url",
            type=str,
            default="https://gunosy.com",
            help="クローリング対象の本元の URL 情報",
        )
        parser.add_argument(
            "--data-root-dir",
            type=pathlib.Path,
            default=pathlib.Path(__file__).resolve().parents[3] / "data" / "articles",
            help="クローリングしたときにどこに保存するかを示すパス情報",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        `python manage.py crawl` を実行したときに呼び出される関数
        """

        # `base_url` に対してページをクローリング & スクレイピングする
        articles = crawl_all_articles(url=options["base_url"])

        # 上記で得られたデータを `data_root_dir` へ保存する
        save_articles(articles=articles, data_root_dir=options["data_root_dir"])
