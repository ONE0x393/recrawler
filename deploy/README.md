# Docker & 사설망 배포 가이드

이 가이드는 Proxmox LXC 컨테이너(사설망)에서 Docker로 봇을 실행하고, GitHub Actions Self-Hosted Runner를 사용하여 배포를 자동화하는 방법을 설명합니다.

## 1. Proxmox LXC 준비 (Docker 호환 설정)

Proxmox에서 LXC 컨테이너를 생성할 때, Docker 실행을 위해 다음 옵션을 반드시 설정해야 합니다.

1.  **Create CT**: Ubuntu 22.04/24.04 템플릿 사용 권장.
2.  **Options 탭**: `Features` 편집 → 다음 항목 체크:
    *   [x] **Nesting** (필수)
    *   [x] **keyctl** (필수, 최신 Docker 호환)
3.  컨테이너 생성 및 부팅.

## 2. Docker & Actions Runner 설치

LXC 컨테이너(Shell)에 접속하여 Docker와 GitHub Runner를 설치합니다.

### 2.1 Docker 설치

```bash
# 기본 패키지 업데이트
apt update && apt install -y curl

# Docker 설치 스크립트 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 설치 확인
docker version
```

### 2.2 GitHub Self-Hosted Runner 설치

사설망에 있는 서버가 GitHub의 명령을 받아 배포를 수행하려면 **Self-Hosted Runner**를 등록해야 합니다.

1.  **GitHub 레포지토리로 이동**: `Settings` → `Actions` → `Runners`.
2.  **New self-hosted runner** 클릭.
3.  **Linux** 선택 후 화면에 표시된 명령어를 LXC 터미널에 차례대로 입력합니다.
    *   *주의: Runner는 `root`로 실행하는 것을 권장하지 않으므로, 새 사용자(예: `runner`)를 생성하거나 안내에 따라 `--allow-root` 옵션을 사용해야 할 수 있습니다.*
    *   가장 간단한 방법은 전용 사용자 추가 후 실행:
        ```bash
        useradd -m runner -s /bin/bash
        usermod -aG docker runner
        su - runner
        # 이후 GitHub에서 복사한 명령어 실행...
        ```
4.  설치가 완료되면 `./run.sh`를 실행하여 Runner를 대기 상태로 만듭니다. (백그라운드 실행 서비스 등록은 GitHub 안내 페이지 하단의 `svc.sh` 섹션 참고)

## 3. 환경 변수 설정 (.env)

자동 배포 워크플로우(`deploy.yml`)는 서버의 `.env` 파일을 참조하여 컨테이너를 실행합니다.
Runner가 실행되는 디렉토리(또는 워크플로우 상의 `$(pwd)`)에 `.env` 파일을 생성해야 합니다.

```bash
# Runner 작업 디렉토리 (보통 actions-runner 폴더 내부의 _work/학습봇/학습봇)
# 배포가 한 번 실행되면 _work 폴더가 생성됩니다. 
# 미리 /home/runner/recruit-bot/.env 경로를 잡고 워크플로우를 수정하거나,
# 가장 쉬운 방법은 GitHub Secrets를 사용하는 것입니다 (현재 워크플로우는 .env 파일 의존).

# 서버의 적절한 위치(예: ~/recruit-bot)에 .env 파일 생성
nano .env
```

`.env` 내용 예시:
```env
DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
SARAMIN_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
CRAWL_INTERVAL_SECONDS=600
```

> **참고**: 제공된 `deploy.yml` 워크플로우는 Runner의 현재 디렉토리에 있는 `.env` 파일을 사용하도록 설정되어 있습니다. 최초 배포 실패 후 디렉토리가 생성되면 그곳에 `.env`를 넣어두거나, 워크플로우 파일을 수정하여 절대 경로의 `.env`를 참조하게 하세요.

## 4. 배포 실행

모든 설정이 완료되었습니다.
이제 로컬에서 코드를 수정하고 `main` 브랜치에 `push`하면 다음 과정이 자동으로 진행됩니다:

1.  **GitHub 서버**: Docker 이미지 빌드 → GHCR(GitHub Container Registry) 업로드.
2.  **LXC (내부망)**: Self-Hosted Runner가 신호를 감지.
3.  **LXC (내부망)**: 새 이미지를 다운로드(`pull`)하고, 기존 컨테이너를 중지/삭제 후 새 버전으로 재실행(`docker run`).

## 트러블슈팅

*   **권한 문제 (`permission denied`)**: Runner 계정이 `docker` 그룹에 포함되어 있는지 확인하세요. (`sudo usermod -aG docker runner`)
*   **이미지 Pull 실패**: `deploy.yml`의 `docker login` 단계가 성공했는지, 레포지토리의 패키지 권한 설정을 확인하세요.
