from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    article_id: str
    title: str
    url: str
