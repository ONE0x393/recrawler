# 채용 공고/게시글 알림 봇

네이버 카페 게시글과 사람인 채용 공고를 주기적으로 수집해 디스코드 웹훅으로 전송하는 봇입니다. 중복 전송을 방지하기 위해 SQLite 기반 영속 저장소를 사용합니다.

## 주요 기능

- 네이버 카페 지정 메뉴 최신 게시글 수집
- 사람인 지정 카테고리 최신 공고 수집(최대 20건)
- SQLite 기반 중복 방지
- 디스코드 임베드 카드 일괄 전송
- 기본 10분 주기 실행

## 프로젝트 구조

- `run.py`: 실행 엔트리포인트 및 스케줄 루프
- `config.py`: 크롤링 대상/환경 변수/기본 설정
- `storage.py`: SQLite 중복 저장소
- `discord_client.py`: 디스코드 임베드 전송 클라이언트
- `sources/naver_cafe.py`: 네이버 카페 크롤러
- `sources/saramin.py`: 사람인 크롤러
- `requirements.txt`: 파이썬 의존성
- `Procfile`: Railway 워커 실행 설정

## 실행 환경

- Python 3.9+
- 인터넷 접근 가능

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## 환경 변수

`.env` 또는 Railway 변수로 설정합니다.

- `DISCORD_WEBHOOK`: 네이버 카페 알림용 웹훅
- `SARAMIN_DISCORD_WEBHOOK`: 사람인 알림용 웹훅
- `CRAWL_INTERVAL_SECONDS`: 크롤링 주기(초). 기본 `600`
- `SEEN_DB_PATH`: SQLite 파일 경로. 기본 `seen.db`

### `.env` 예시

```env
DISCORD_WEBHOOK="https://discord.com/api/webhooks/XXXX/XXXX"
SARAMIN_DISCORD_WEBHOOK="https://discord.com/api/webhooks/YYYY/YYYY"
CRAWL_INTERVAL_SECONDS=600
SEEN_DB_PATH=seen.db
```

## Railway 배포

### 1) 레포 연결

- Railway → New Project → Deploy from GitHub → 레포 선택

### 2) 환경 변수 등록

- `DISCORD_WEBHOOK`
- `SARAMIN_DISCORD_WEBHOOK`
- `CRAWL_INTERVAL_SECONDS` (선택)
- `SEEN_DB_PATH=/data/seen.db` (영속 저장 시)

### 3) 볼륨(영속 저장) 추가

- Add Volume → Mount Path: `/data`
- 위 경로로 SQLite를 저장하면 재배포 후에도 중복 기록이 유지됩니다.

### 4) 실행

- `Procfile`이 있으면 `worker: python run.py`로 자동 실행
- 또는 Start Command에 `python run.py` 설정

## 동작 방식

1. 네이버 카페/사람인 목록을 수집
2. SQLite에 저장된 `source + id` 기준으로 중복 필터링
3. 새 항목이 있을 때만 디스코드 임베드로 1회 전송

## 문제 해결

### `sqlite3.OperationalError: unable to open database file`
- `SEEN_DB_PATH` 상위 디렉터리가 존재하는지 확인
- Railway에서는 `/data` 볼륨 마운트 후 `SEEN_DB_PATH=/data/seen.db`

### 디스코드 400 오류
- 메시지가 너무 길거나 빈 경우 발생 가능
- 현재는 길이 제한 및 빈 메시지 스킵 처리

### 크롤링 결과가 비어 있음
- 네이버/사람인 페이지 구조 변경 시 파싱 로직 업데이트 필요
- `sources/`의 셀렉터를 점검
