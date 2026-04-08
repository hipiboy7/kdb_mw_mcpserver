"""
[파일 설명]
mcp_server.py - KdbClient의 기능을 MCP Tool로 노출하는 MCP 서버

[SOLID 원칙 적용]
S (단일 책임): 이 파일은 오직 "MCP Tool 등록 및 실행 위임"만 담당합니다.
               실제 API 호출은 KdbClient가 담당합니다.
D (의존성 역전): Tool 함수들은 KdbClient에 직접 의존하지 않고
                 _get_kdb_client() 함수를 통해 간접적으로 사용합니다.
                 → 테스트 시 _get_kdb_client를 Mock으로 교체하기 쉬워집니다.

[이 파일의 역할]
LLM(사내 AI 서비스)이 "이메일 보내줘"라고 요청하면:
  1. LLM → MCP 프로토콜 → 이 파일의 Tool 함수 호출
  2. Tool 함수 → KdbClient → kdb_mw REST API 호출
  3. kdb_mw 응답 → KdbClient → Tool 함수 → LLM
"""

# FastMCP: MCP 서버를 쉽게 만들 수 있게 해주는 라이브러리
from mcp.server.fastmcp import FastMCP

# KdbClient: kdb_mw API 호출을 담당하는 클래스 (Phase 1에서 구현)
from src.kdb_client import KdbClient

# config: 모든 설정값과 상수를 관리하는 파일 (하드코딩 금지 원칙)
import config


# ── MCP 서버 초기화 ────────────────────────────────────────────────────────────
#
# FastMCP(): MCP 서버 객체를 생성합니다.
# 이 객체에 Tool을 등록하면 LLM이 해당 Tool을 사용할 수 있게 됩니다.
#
# name:         LLM에게 표시되는 서버 이름 (config.py에서 관리)
# instructions: LLM이 이 서버를 어떻게 활용할지 이해하는 설명 (config.py에서 관리)
mcp = FastMCP(
    config.MCP_SERVER_NAME,
    instructions=config.MCP_SERVER_INSTRUCTIONS,
)


def _get_kdb_client() -> KdbClient:
    """
    [이 함수의 역할]
    KdbClient 인스턴스를 생성해서 반환합니다.

    [왜 별도 함수로 분리했나?]
    테스트 코드에서 이 함수만 Mock으로 교체하면
    실제 서버 없이도 MCP Tool을 테스트할 수 있습니다.

    만약 Tool 함수 안에 KdbClient(...)를 직접 작성했다면
    테스트에서 교체하기가 훨씬 복잡해집니다.

    이것이 SOLID의 D(의존성 역전) 원칙입니다.
    "구체적인 구현(KdbClient 생성)에 직접 의존하지 말고,
     중간 함수(_get_kdb_client)를 통해 간접적으로 의존하라"
    """
    return KdbClient(
        base_url=config.KDB_BASE_URL,
        token=config.KDB_TOKEN,
        verify_ssl=config.VERIFY_SSL,
    )


# ── MCP Tool: 텍스트/HTML 이메일 발송 ─────────────────────────────────────────
#
# @mcp.tool() 데코레이터:
# 아래 함수를 MCP Tool로 등록합니다.
# LLM은 이 데코레이터가 붙은 함수들만 도구로 인식하고 사용할 수 있습니다.
@mcp.tool()
def send_text_email(
    sender_name: str,
    receivers: str,
    subject: str,
    content: str,
) -> dict:
    """
    일반 텍스트 또는 HTML 형식의 사내 이메일을 발송합니다.
    content에 HTML 태그를 직접 사용할 수 있습니다.

    Args:
        sender_name: 보내는 사람 이름 (예: "홍길동", "리발소 시스템")
        receivers:   받는 사람 이메일. 여러 명은 쉼표로 구분
                     (예: "kim@company.com,lee@company.com")
        subject:     이메일 제목
        content:     이메일 본문 (텍스트 또는 HTML 태그 사용 가능)
                     (예: "<h1>제목</h1><p>내용</p>")

    Returns:
        dict: 발송 결과 (예: {"message": "Email sent successfully"})
    """
    # _get_kdb_client()로 KdbClient를 생성하고 send_text_email을 호출합니다.
    # Tool 함수는 "어떻게 API를 호출하는지" 알 필요가 없습니다.
    # 그것은 KdbClient가 담당합니다. (단일 책임 원칙)
    client = _get_kdb_client()
    return client.send_text_email(
        sender_name=sender_name,
        receivers=receivers,
        subject=subject,
        content=content,
    )


# ── MCP Tool: Markdown 이메일 발송 ────────────────────────────────────────────

@mcp.tool()
def send_email(
    sender_name: str,
    receivers: str,
    subject: str,
    content: str,
) -> dict:
    """
    Markdown 형식의 사내 이메일을 발송합니다. (Smart Email)
    content를 Markdown으로 작성하면 자동으로 HTML 이메일로 변환됩니다.
    Mermaid 다이어그램 코드 블록도 그림으로 변환되어 발송됩니다.

    Args:
        sender_name: 보내는 사람 이름 (예: "홍길동", "리발소 시스템")
        receivers:   받는 사람 이메일. 여러 명은 쉼표로 구분
        subject:     이메일 제목
        content:     이메일 본문 (Markdown 형식)
                     (예: "# 제목\n## 소제목\n- 항목1\n**굵게**")

    Returns:
        dict: 발송 결과 (예: {"message": "Email sent successfully"})
    """
    client = _get_kdb_client()
    return client.send_email(
        sender_name=sender_name,
        receivers=receivers,
        subject=subject,
        content=content,
    )


# ── 실행 진입점 ────────────────────────────────────────────────────────────────
#
# if __name__ == "__main__": 이 파일을 직접 실행할 때만 아래 코드가 동작합니다.
# 다른 파일에서 import할 때는 실행되지 않습니다. (테스트 코드가 import할 때 등)
if __name__ == "__main__":
    # transport="stdio": LLM(MCP Client)과 동일한 호스트에서 실행됩니다.
    # LLM이 이 스크립트를 자식 프로세스로 직접 실행하며,
    # 표준 입출력(stdin/stdout)으로 통신합니다.
    mcp.run(transport="stdio")  # pragma: no cover
