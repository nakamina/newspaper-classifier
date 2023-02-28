import hashlib
import json
import logging
import os
import pathlib
from dataclasses import asdict, dataclass
from typing import Iterator, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Article(object):
    html: str
    title: str
    content: str
    category: str


@dataclass
class Category(object):
    url: str
    name: str


def get_category_list(url: str) -> List[Category]:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    nav_tag = soup.find("nav", class_="nav")

    li_tags = []
    for i in range(1, 9):
        li_tag = nav_tag.find("li", class_=f"nav_color_{i}")
        li_tags.append(li_tag)

    news_categories = []
    for li_tag in li_tags:
        news_category_a_tag = li_tag.find("a")
        news_category_url = news_category_a_tag["href"]
        news_category_name = news_category_a_tag.get_text()

        news_categories.append(Category(url=news_category_url, name=news_category_name))

    return news_categories


def get_article_url_list_from_article_list(category_url: str) -> List[str]:
    res = requests.get(category_url)
    soup = BeautifulSoup(res.text, "html.parser")

    div_article_list_tag = soup.find("div", class_="article_list")
    div_list_content_tags = div_article_list_tag.find_all("div", class_="list_content")

    article_url_list = []
    for div_list_content_tag in div_list_content_tags:
        div_list_content_a_tag = div_list_content_tag.find("a")
        div_list_content_url = div_list_content_a_tag["href"]

        article_url_list.append(div_list_content_url)

    return article_url_list


def scrape_article_title(soup: BeautifulSoup) -> str:
    return soup.find("h1").get_text()


def scrape_article_content(soup: BeautifulSoup) -> str:
    div_article_tag = soup.find("div", class_="article")
    article_p_tags = div_article_tag.find_all("p")

    article_paragraphs = []
    for article_p_tag in article_p_tags:
        article_text = article_p_tag.get_text()
        article_paragraphs.append(article_text)

    article_content = "\n\n".join(article_paragraphs)
    return article_content


def scrape_article(article_url: str, category_name: str) -> Article:
    print(f"現在の URL: {article_url}")

    res = requests.get(article_url)
    soup = BeautifulSoup(res.text, "html.parser")

    article = Article(
        html=res.text,
        title=scrape_article_title(soup),
        content=scrape_article_content(soup),
        category=category_name,
    )
    return article


def get_next_url_for_article_list(category_url: str) -> Optional[str]:
    res = requests.get(category_url)
    soup = BeautifulSoup(res.text, "html.parser")

    next_page_div_tag = soup.find("div", class_="pager-link-option")
    if next_page_div_tag is None:
        return None  # つぎのページへのタグが見つからなかったら None を返す

    # つぎのページへのタグが見つかったら、そのタグから次ページへのリンクを返す
    next_page_a_tag = next_page_div_tag.find("a", class_="btn")
    next_page_a_tag_url = next_page_a_tag["href"]

    base_url, *_ = category_url.split("?")

    next_page_a_tag_url = base_url + next_page_a_tag_url
    return next_page_a_tag_url


def crawl_category(category: Category) -> Iterator[Article]:
    article_url_list = get_article_url_list_from_article_list(category.url)
    for article_url in article_url_list:
        yield scrape_article(article_url, category.name)

    next_page_url = get_next_url_for_article_list(category.url)
    if next_page_url is not None:
        category = Category(url=next_page_url, name=category.name)
        # 次ページの URL をもとに、再度この関数を呼ぶ (再起関数)
        yield from crawl_category(category)


def crawl_all_articles(url: str) -> List[Article]:
    categories = get_category_list(url)
    assert len(categories) == 8  # カテゴリは現状8個なので

    articles = []
    for category in categories:
        for article in crawl_category(category):
            articles.append(article)

    return articles


def save_article(article: Article, data_root_dir: pathlib.Path) -> None:
    category_root_dir = data_root_dir / article.category
    if not os.path.exists(category_root_dir):
        os.makedirs(category_root_dir)

    title_hash = hashlib.md5(article.title.encode()).hexdigest()
    file_path = category_root_dir / f"{title_hash}.json"

    with open(file_path, "w") as wf:
        json.dump(
            obj=asdict(article),
            fp=wf,
            ensure_ascii=False,
            indent=4,
        )


def save_articles(
    articles: List[Article],
    data_root_dir: pathlib.Path,
) -> None:
    for article in articles:
        save_article(article, data_root_dir)
