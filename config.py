"""
[파일 설명]
config.py - 프로젝트 전체에서 사용하는 설정값과 상수를 한 곳에 모아두는 파일

[왜 이 파일이 필요한가?]
코드 여러 곳에 같은 값을 직접 쓰면 (이를 '하드코딩'이라 함),
나중에 값을 바꿔야 할 때 모든 파일을 다 찾아서 수정해야 합니다.
이 파일 한 곳에만 모아두면 여기서만 고치면 됩니다.

예시)
  하드코딩: client.get("https://mamama.iptime.org:8000/email/send_markdown")  <- 나쁜 예
  상수화:   client.get(config.KDB_BASE_URL + config.ENDPOINT_EMAIL_SEND_MARKDOWN) <- 좋은 예

[비밀값과 일반 설정값의 구분]
  .env 파일  → 토큰, 비밀번호 등 외부에 노출되면 안 되는 값 (버전관리에서 제외)
  config.py  → 타임아웃, API 경로 등 노출되어도 괜찮은 설정값 (버전관리에 포함)
"""

# os: 운영체제(Operating System)와 관련된 기능을 제공하는 Python 내장 도구
# 여기서는 환경변수를 읽어오는 os.getenv() 함수를 사용하기 위해 import 합니다.
import os

# Path: 파일/폴더 경로를 다루는 Python 내장 도구
# 운영체제(Windows/Linux)에 따라 경로 구분자가 달라도 자동으로 처리해줍니다.
from pathlib import Path

# load_dotenv: .env 파일의 내용을 메모리에 불러오는 함수
# 이걸 호출해야 아래에서 os.getenv()로 .env의 값을 읽을 수 있습니다.
from dotenv import load_dotenv

# .env 파일 경로를 이 파일(config.py) 기준으로 고정합니다.
#
# Path(__file__) : 현재 이 파일(config.py)의 전체 경로
#                  예) C:\Users\...\mcp_kdb_mw\config.py
# .parent        : 그 파일이 있는 폴더
#                  예) C:\Users\...\mcp_kdb_mw
# / ".env"       : 그 폴더 안의 .env 파일
#                  예) C:\Users\...\mcp_kdb_mw\.env
#
# [왜 이렇게 하나?]
# load_dotenv()를 인자 없이 쓰면 "현재 실행 위치"에서 .env를 찾습니다.
# VS Code가 MCP 서버를 실행할 때 작업 디렉토리가 달라질 수 있어서
# 이렇게 config.py 위치 기준으로 고정하면 어디서 실행해도 .env를 찾습니다.
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(_ENV_PATH)


# ── kdb_mw 서버 접속 정보 ──────────────────────────────────────────────────────
#
# os.getenv("변수이름", "기본값") 사용법:
#   1. .env 파일에 해당 변수가 있으면 → 그 값을 사용
#   2. .env 파일에 없으면             → 두 번째 인자(기본값)를 사용
#
# 예시) .env 에 KDB_BASE_URL=http://내부망주소 라고 쓰면 그 값이 사용됨
#       .env 에 아무것도 없으면 https://mamama.iptime.org:8000 이 기본값으로 사용됨

# kdb_mw 서버의 기본 주소 (모든 API 경로 앞에 붙는 공통 부분)
KDB_BASE_URL: str = os.getenv("KDB_BASE_URL", "https://mamama.iptime.org:8000")

# kdb_mw 인증에 필요한 JWT 토큰
# JWT(JSON Web Token): 서버가 "이 사람은 인증된 사용자야"를 확인하는 디지털 신분증
# 값이 없으면 빈 문자열("") → 인증 없이 요청 (서버에서 거부될 수 있음)
KDB_TOKEN: str = os.getenv("KDB_TOKEN", "")

# SSL 인증서 검증 여부
# SSL: 인터넷 통신 암호화 기술 (https://... 에서 's'가 SSL을 의미)
# True  → 인증서가 공인된 것인지 검증 (공인 인증서 사용 시)
# False → 검증하지 않음 (사설 인증서 사용 시, 개발/테스트 환경에서 주로 사용)
#
# .lower() == "true" 설명:
#   .env에서 읽어온 값은 항상 문자열(텍스트)입니다.
#   .lower()로 소문자로 변환 후 "true"와 비교하면 True/False 가 됩니다.
#   예: "True" → .lower() → "true" → == "true" → True (파이썬 불리언)
VERIFY_SSL: bool = os.getenv("VERIFY_SSL", "false").lower() == "true"


# ── MCP 서버 설정 ─────────────────────────────────────────────────────────────
#
# MCP(Model Context Protocol): LLM이 외부 도구를 사용할 수 있게 해주는 표준 프로토콜
# LLM이 이 서버에 연결하면, 아래 이름과 설명을 보고 어떤 서버인지 파악합니다.

# MCP 서버 이름 (LLM에게 표시되는 이름)
MCP_SERVER_NAME: str = "kdb_mw"

# MCP 서버 설명 (LLM이 이 서버를 어떻게 활용할지 이해하는 데 사용)
MCP_SERVER_INSTRUCTIONS: str = (
    "리발소(kdb_mw) 미들웨어 관리 시스템과 연동된 MCP 서버입니다. "
    "사내 이메일 발송 기능을 제공합니다."
)


# ── HTTP 요청 설정 ─────────────────────────────────────────────────────────────

# 서버 응답을 기다리는 최대 시간 (초 단위)
# 30.0초 안에 응답이 없으면 "타임아웃" 에러 발생
# float: 소수점이 있는 숫자 타입 (예: 30.0, 10.5)
REQUEST_TIMEOUT: float = 30.0


# ── kdb_mw API 엔드포인트 경로 ────────────────────────────────────────────────
#
# 엔드포인트(Endpoint): API에서 특정 기능에 접근하는 URL 경로
# KDB_BASE_URL + 엔드포인트 = 완전한 URL
#
# 예시) https://mamama.iptime.org:8000  +  /email/send_markdown
#       ↑ KDB_BASE_URL                     ↑ ENDPOINT_EMAIL_SEND_MARKDOWN

# 일반 텍스트/HTML 이메일 발송 API 경로
# /api/v1/ : Flask-AppBuilder가 REST API에 자동으로 붙이는 공통 접두사
ENDPOINT_EMAIL_SEND: str = "/api/v1/email/send"

# Smart Email 발송 API 경로 (Markdown → HTML 이메일 변환 후 발송)
ENDPOINT_EMAIL_SEND_MARKDOWN: str = "/api/v1/email/send_markdown"

# 서버 상태 확인 API 경로 (서버가 살아있는지 확인할 때 사용)
ENDPOINT_HEALTH: str = "/common/health"

# 365일 유효한 JWT 토큰 발급 API 경로
ENDPOINT_GENERATE_TOKEN: str = "/common/generate_long_term_token"
