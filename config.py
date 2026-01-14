import os

CAFE_ID = "31258781"
MENU_ID = "8"
MENU_URL = f"https://cafe.naver.com/f-e/cafes/{CAFE_ID}/menus/{MENU_ID}"
MOBILE_MENU_URL = f"https://m.cafe.naver.com/ca-fe/web/cafes/{CAFE_ID}/menus/{MENU_ID}"
API_URL = "https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json"
SARAMIN_URL = (
    "https://www.saramin.co.kr/zf_user/jobs/list/job-category?"
    "cat_kewd=84%2C104%2C127%2C100%2C136&panel_type=&search_optional_item=n"
    "&search_done=y&panel_count=y&preview=y"
)

NAVER_LOGO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/"
    "Naver_logo_initial.svg/240px-Naver_logo_initial.svg.png"
)
SARAMIN_LOGO_URL = "https://www.saraminimage.co.kr/logo/saraminsnslogo.png"

NAVER_COLOR = 0x03C75A
SARAMIN_COLOR = 0x2F80ED

NAVER_SOURCE_NAME = "Naver Cafe"
SARAMIN_SOURCE_NAME = "Saramin"

NAVER_ITEM_LABEL = "게시글"
SARAMIN_ITEM_LABEL = "채용 공고"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}

MAX_SEEN = 500
DEFAULT_INTERVAL_SECONDS = 600
DEFAULT_DB_PATH = "seen.db"
SARAMIN_LIMIT = 20

ENV_DISCORD_WEBHOOK = "DISCORD_WEBHOOK"
ENV_SARAMIN_WEBHOOK = "SARAMIN_DISCORD_WEBHOOK"
ENV_INTERVAL_SECONDS = "CRAWL_INTERVAL_SECONDS"
ENV_DB_PATH = "SEEN_DB_PATH"


def load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            value = value.strip().strip("\"").strip("'")
            os.environ.setdefault(key.strip(), value)
