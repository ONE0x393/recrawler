import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from config import HEADERS, SARAMIN_URL
from models import Article


def extract_rec_idx(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"rec_idx=(\d+)", value)
    if match:
        return match.group(1)
    return None


def get_attr_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def fetch_saramin_jobs(limit: int = 20) -> list[Article]:
    response = requests.get(SARAMIN_URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    articles: list[Article] = []
    seen_ids: set[str] = set()
    anchors = soup.select("a.str_tit")
    for anchor in anchors:
        href = get_attr_str(anchor.get("href"))
        if not href or "/zf_user/jobs/relay/view" not in href or "rec_idx=" not in href:
            continue
        article_id = extract_rec_idx(href)
        if not article_id or article_id in seen_ids:
            continue
        title = anchor.get_text(" ", strip=True) or "새 공고"
        url = urljoin("https://www.saramin.co.kr", href)
        articles.append(Article(article_id=article_id, title=title, url=url))
        seen_ids.add(article_id)
        if len(articles) >= limit:
            break

    return articles
