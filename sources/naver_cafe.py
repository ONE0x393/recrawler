import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from config import API_URL, CAFE_ID, HEADERS, MENU_ID, MENU_URL, MOBILE_MENU_URL
from models import Article


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def extract_article_id(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"articleid=(\d+)", value)
    if match:
        return match.group(1)
    match = re.search(r"/articles/(\d+)", value)
    if match:
        return match.group(1)
    return None


def normalize_article(
    article_id: str | None,
    title: str | None,
    href: str | None,
    base_url: str,
) -> Article | None:
    if not article_id:
        return None
    safe_title = title.strip() if title else "새 글"
    if href:
        full_url = urljoin(base_url, href)
    else:
        full_url = (
            f"https://cafe.naver.com/ArticleRead.nhn?clubid={CAFE_ID}"
            f"&articleid={article_id}"
        )
    return Article(article_id=article_id, title=safe_title, url=full_url)


def get_attr_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def parse_articles(html: str, base_url: str) -> list[Article]:
    soup = BeautifulSoup(html, "html.parser")
    articles: list[Article] = []
    seen_ids: set[str] = set()

    for tag in soup.select("[data-articleid]"):
        article_id = get_attr_str(tag.get("data-articleid"))
        title = tag.get_text(" ", strip=True)
        href = get_attr_str(tag.get("href") or tag.get("data-articlelink"))
        article = normalize_article(article_id, title, href, base_url)
        if article and article.article_id not in seen_ids:
            seen_ids.add(article.article_id)
            articles.append(article)

    for anchor in soup.select("a[href]"):
        href = get_attr_str(anchor.get("href"))
        article_id = extract_article_id(href)
        if not article_id or article_id in seen_ids:
            continue
        title = anchor.get_text(" ", strip=True)
        article = normalize_article(article_id, title, href, base_url)
        if article:
            seen_ids.add(article.article_id)
            articles.append(article)

    return articles


def fetch_articles_from_api() -> list[Article]:
    params = {
        "search.clubid": CAFE_ID,
        "search.menuid": MENU_ID,
        "search.queryType": "lastArticle",
        "search.page": "1",
        "search.pageSize": "50",
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    result: dict = {}
    if isinstance(data, dict):
        message = data.get("message")
        if isinstance(message, dict):
            msg_result = message.get("result")
            if isinstance(msg_result, dict):
                result = msg_result
        if not result:
            top_result = data.get("result")
            if isinstance(top_result, dict):
                result = top_result

    article_list = result.get("articleList") or result.get("articles") or []

    articles: list[Article] = []
    seen_ids: set[str] = set()
    for item in article_list:
        if not isinstance(item, dict):
            continue
        raw_id = item.get("articleId") or item.get("articleid") or item.get("articleID")
        if raw_id is None:
            continue
        article_id = str(raw_id)
        if article_id in seen_ids:
            continue
        title = item.get("subject") or item.get("title") or "새 글"
        url = (
            f"https://cafe.naver.com/ArticleRead.nhn?clubid={CAFE_ID}"
            f"&articleid={article_id}"
        )
        articles.append(Article(article_id=article_id, title=title, url=url))
        seen_ids.add(article_id)

    return articles


def fetch_naver_articles() -> list[Article]:
    html_sources = [
        (MENU_URL, "https://cafe.naver.com"),
        (MOBILE_MENU_URL, "https://m.cafe.naver.com"),
    ]

    try:
        articles = fetch_articles_from_api()
    except Exception:
        logging.exception("API fetch failed; falling back to HTML")
        articles = []

    if not articles:
        for url, base_url in html_sources:
            html = fetch_html(url)
            articles.extend(parse_articles(html, base_url))

    return articles
