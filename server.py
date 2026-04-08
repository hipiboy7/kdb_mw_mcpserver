"""
MCP Server for kdb_mw (미들웨어 관리 시스템)
kdb_mw REST API를 Claude/LLM이 사용할 수 있는 MCP Tool로 래핑
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# ── 설정 (환경변수로 관리 → 외부망/내부망 전환 용이) ──────────────────────────
KDB_BASE_URL = os.getenv("KDB_BASE_URL", "https://mamama.iptime.org:8000")
KDB_TOKEN    = os.getenv("KDB_TOKEN", "")
VERIFY_SSL   = os.getenv("VERIFY_SSL", "false").lower() == "true"

# ── MCP 서버 초기화 ────────────────────────────────────────────────────────────
# stdio 방식: LLM(MCP Client)과 동일 호스트에서 실행, 네트워크 포트 불필요
mcp = FastMCP(
    "kdb_mw",
    instructions="JEUS/WebToB 미들웨어 관리 시스템. 이메일 발송 등 kdb_mw 기능을 제공합니다.",
)


def get_client() -> httpx.Client:
    """kdb_mw API 호출용 HTTP 클라이언트 생성"""
    headers = {}
    if KDB_TOKEN:
        headers["Authorization"] = f"Bearer {KDB_TOKEN}"
    return httpx.Client(
        base_url=KDB_BASE_URL,
        headers=headers,
        verify=VERIFY_SSL,
        timeout=30.0,
    )


# ── Tool: 이메일 발송 ──────────────────────────────────────────────────────────

@mcp.tool()
def send_email(
    sender_name: str,
    receivers: str,
    subject: str,
    content: str,
) -> dict:
    """
    kdb_mw를 통해 사내 이메일을 발송합니다. (Smart Email - Markdown 지원)

    content는 Markdown 형식으로 작성하면 자동으로 HTML 이메일로 변환됩니다.
    Mermaid 다이어그램 코드 블록도 그림으로 변환되어 발송됩니다.

    Args:
        sender_name: 보내는 사람 이름 (예: "홍길동")
        receivers:   받는 사람 이메일 주소. 여러 명은 쉼표로 구분 (예: "a@company.com,b@company.com")
        subject:     이메일 제목
        content:     이메일 본문 (Markdown 형식)
    """
    with get_client() as client:
        response = client.post(
            "/email/send_markdown",
            json={
                "sender_name": sender_name,
                "receivers": receivers,
                "subject": subject,
                "content": content,
            },
        )
        response.raise_for_status()
        return response.json()


# ── 실행 ──────────────────────────────────────────────────────────────────────
# stdio 방식: LLM이 이 스크립트를 자식 프로세스로 실행하면서 직접 통신
if __name__ == "__main__":
    mcp.run(transport="stdio")
