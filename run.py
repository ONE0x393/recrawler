import logging
import os
import time

from config import (
    DEFAULT_DB_PATH,
    DEFAULT_INTERVAL_SECONDS,
    ENV_DB_PATH,
    ENV_DISCORD_WEBHOOK,
    ENV_INTERVAL_SECONDS,
    ENV_SARAMIN_WEBHOOK,
    MAX_SEEN,
    NAVER_COLOR,
    NAVER_ITEM_LABEL,
    NAVER_LOGO_URL,
    NAVER_SOURCE_NAME,
    SARAMIN_COLOR,
    SARAMIN_ITEM_LABEL,
    SARAMIN_LIMIT,
    SARAMIN_LOGO_URL,
    SARAMIN_SOURCE_NAME,
    load_env_file,
)
from discord_client import post_batch_embed
from sources.naver_cafe import fetch_naver_articles
from sources.saramin import fetch_saramin_jobs
from storage import SeenStore


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set in .env")
    return value


def crawl_naver_cafe(store: SeenStore, webhook_url: str) -> int:
    articles = fetch_naver_articles()
    if not articles:
        logging.info("No Naver Cafe posts found.")
        return 0

    article_ids = [article.article_id for article in articles]
    seen_ids = store.get_seen_set(NAVER_SOURCE_NAME, article_ids)
    new_articles = [article for article in articles if article.article_id not in seen_ids]
    if not new_articles:
        logging.info("No new Naver Cafe posts found.")
        return 0

    ordered_articles = list(reversed(new_articles))
    post_batch_embed(
        webhook_url,
        ordered_articles,
        NAVER_SOURCE_NAME,
        NAVER_COLOR,
        NAVER_LOGO_URL,
        NAVER_ITEM_LABEL,
    )

    store.mark_seen_many(NAVER_SOURCE_NAME, [article.article_id for article in new_articles])
    for article in ordered_articles:
        logging.info("Posted Naver Cafe article %s", article.article_id)
    return len(new_articles)


def crawl_saramin(store: SeenStore, webhook_url: str, limit: int) -> int:
    articles = fetch_saramin_jobs(limit=limit)
    if not articles:
        logging.info("No Saramin jobs found.")
        return 0

    article_ids = [article.article_id for article in articles]
    seen_ids = store.get_seen_set(SARAMIN_SOURCE_NAME, article_ids)
    new_articles = [article for article in articles if article.article_id not in seen_ids]
    if not new_articles:
        logging.info("No new Saramin jobs found.")
        return 0

    ordered_articles = list(reversed(new_articles))
    post_batch_embed(
        webhook_url,
        ordered_articles,
        SARAMIN_SOURCE_NAME,
        SARAMIN_COLOR,
        SARAMIN_LOGO_URL,
        SARAMIN_ITEM_LABEL,
    )

    store.mark_seen_many(SARAMIN_SOURCE_NAME, [article.article_id for article in new_articles])
    for article in ordered_articles:
        logging.info("Posted Saramin job %s", article.article_id)
    return len(new_articles)


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    load_env_file(os.path.join(base_dir, ".env"))

    naver_webhook_url = get_required_env(ENV_DISCORD_WEBHOOK)
    saramin_webhook_url = get_required_env(ENV_SARAMIN_WEBHOOK)

    interval_seconds = int(os.getenv(ENV_INTERVAL_SECONDS, str(DEFAULT_INTERVAL_SECONDS)))
    db_path = os.getenv(ENV_DB_PATH, DEFAULT_DB_PATH)
    if not os.path.isabs(db_path):
        db_path = os.path.join(base_dir, db_path)

    store = SeenStore(db_path, MAX_SEEN)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    while True:
        try:
            naver_count = crawl_naver_cafe(store, naver_webhook_url)
            saramin_count = crawl_saramin(store, saramin_webhook_url, SARAMIN_LIMIT)
            logging.info(
                "Crawl complete. Naver: %s, Saramin: %s",
                naver_count,
                saramin_count,
            )
        except Exception:
            logging.exception("Crawl failed")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
