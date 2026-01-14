import logging

import requests

from models import Article


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def post_batch_embed(
    webhook_url: str,
    articles: list[Article],
    source_name: str,
    color: int,
    logo_url: str,
    item_label: str,
) -> None:
    if not articles:
        return

    description_lines: list[str] = []
    for index, article in enumerate(articles, 1):
        title = (article.title or "새 글").strip() or "새 글"
        title = _truncate(title, 100)
        description_lines.append(f"**{index}.** [**{title}**]({article.url})")

    description = "\n\n".join(description_lines)
    description = _truncate(description, 3500)

    embed = {
        "title": f"{source_name} 새 {item_label} {len(articles)}건",
        "description": description,
        "color": color,
        "author": {"name": source_name, "icon_url": logo_url},
        "footer": {"text": f"{source_name} 알림", "icon_url": logo_url},
    }

    payload = {"embeds": [embed]}
    response = requests.post(webhook_url, json=payload, timeout=15)
    if response.status_code >= 400:
        logging.error("Discord webhook error %s: %s", response.status_code, response.text)
    response.raise_for_status()
