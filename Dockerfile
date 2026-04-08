# ────────────────────────────────────────────────────────────────────────────
# Dockerfile - mcp_kdb_mw MCP 서버 Docker 이미지 빌드 설정
#
# [Dockerfile이란?]
# Docker 이미지를 만들기 위한 설계도입니다.
# 이 파일의 명령을 순서대로 실행해서 이미지를 만듭니다.
#
# [빌드 명령]
# docker build -t mcp-kdb-mw .
#
# [실행 명령 (Claude Desktop 등 MCP Client에서)]
# docker run --rm -i --env-file .env mcp-kdb-mw
#   --rm  : 컨테이너 종료 시 자동 삭제
#   -i    : stdin(표준입력)을 열어둠 → stdio 통신에 필수
# ────────────────────────────────────────────────────────────────────────────

# ── 1단계: 베이스 이미지 선택 ─────────────────────────────────────────────────
#
# FROM: 이 이미지의 기반이 될 베이스 이미지를 지정합니다.
# python:3.12-slim: Python 3.12가 설치된 경량 Linux 이미지
#   - 3.12: 안정적이고 kdb_mw와 같은 버전대
#   - slim: 불필요한 패키지를 제거한 경량 버전 (이미지 크기 최소화)
FROM python:3.12-slim

# ── 2단계: 작업 디렉토리 설정 ─────────────────────────────────────────────────
#
# WORKDIR: 컨테이너 안에서 명령이 실행될 기본 디렉토리를 설정합니다.
# 이후의 모든 명령(COPY, RUN 등)은 이 디렉토리 기준으로 실행됩니다.
WORKDIR /app

# ── 3단계: 의존성 파일 먼저 복사 및 설치 ──────────────────────────────────────
#
# [왜 소스코드보다 requirements.txt를 먼저 복사하나?]
# Docker는 각 명령을 "레이어(layer)"로 캐싱합니다.
# requirements.txt가 바뀌지 않으면 pip install 결과를 재사용합니다.
# 소스코드만 수정했을 때 패키지를 다시 설치하지 않아도 됩니다. (빌드 속도 향상)
COPY requirements.txt .

# RUN: 이미지 빌드 시 실행할 명령입니다.
# --no-cache-dir: pip 캐시를 저장하지 않음 → 이미지 크기 절약
RUN pip install --no-cache-dir -r requirements.txt

# ── 4단계: 소스코드 복사 ──────────────────────────────────────────────────────
#
# COPY <로컬 경로> <컨테이너 경로>
# . (점): 현재 디렉토리의 모든 파일을 /app 으로 복사합니다.
# .dockerignore 파일에 명시된 항목은 복사에서 제외됩니다.
COPY . .

# ── 5단계: 환경변수 기본값 설정 ───────────────────────────────────────────────
#
# ENV: 컨테이너 실행 시 사용할 환경변수 기본값을 설정합니다.
# docker run --env-file .env 또는 -e KEY=VALUE 로 덮어쓸 수 있습니다.
#
# KDB_BASE_URL, KDB_TOKEN은 실행 시 반드시 외부에서 주입해야 합니다.
# 여기서는 빈 값으로 두고, .env 파일 또는 -e 옵션으로 전달합니다.
ENV KDB_BASE_URL=""
ENV KDB_TOKEN=""
ENV VERIFY_SSL="false"
ENV PYTHONUNBUFFERED="1"
# PYTHONUNBUFFERED=1: Python 출력을 버퍼링하지 않음
# → 로그가 즉시 출력됨 (컨테이너 디버깅 시 중요)

# ── 6단계: 실행 명령 설정 ─────────────────────────────────────────────────────
#
# CMD: 컨테이너 시작 시 실행할 기본 명령입니다.
# docker run 명령 뒤에 다른 명령을 붙이면 이 CMD는 무시됩니다.
#
# -m src.mcp_server: src/mcp_server.py를 모듈로 실행합니다.
# (python src/mcp_server.py 와 동일하지만 Python 경로 처리가 더 안정적입니다.)
CMD ["python", "-m", "src.mcp_server"]
