"""
[파일 설명]
test_mcp_server.py - MCP Server가 올바르게 동작하는지 검증하는 테스트 코드

[Phase 2에서 검증할 것]
1. MCP 서버에 Tool이 올바르게 등록되어 있는가?
2. Tool 실행 시 KdbClient의 올바른 메서드가 호출되는가?
3. KdbClient에서 발생한 에러가 Tool 밖으로 전달되는가?

[왜 KdbClient를 Mock으로 대체하나?]
mcp_server.py는 "MCP 프로토콜로 Tool을 노출하는 것"이 책임입니다.
실제 kdb_mw 서버 호출은 KdbClient가 담당합니다.
따라서 mcp_server 테스트에서는 KdbClient를 가짜로 교체하고
"MCP 서버가 KdbClient를 올바르게 사용하는가"만 검증합니다.
"""

import pytest
from unittest.mock import MagicMock, patch

# 아직 만들지 않은 모듈을 import (TDD 방식 - 먼저 실패를 확인)
from src.mcp_server import mcp, send_text_email, send_email
from src.kdb_client import KdbClient


# ── Tool 등록 테스트 ───────────────────────────────────────────────────────────

class TestMcpToolRegistration:
    """MCP 서버에 Tool이 올바르게 등록되어 있는지 확인하는 테스트"""

    def test_mcp_서버_이름_확인(self):
        """
        MCP 서버 이름이 config에 설정한 값과 일치하는지 확인합니다.
        LLM은 이 이름으로 서버를 구별합니다.
        """
        import config
        assert mcp.name == config.MCP_SERVER_NAME

    def test_send_text_email_tool_등록_확인(self):
        """
        send_text_email Tool이 MCP 서버에 등록되어 있는지 확인합니다.
        등록되지 않으면 LLM이 이 기능을 사용할 수 없습니다.
        """
        # mcp._tool_manager.list_tools(): 등록된 모든 Tool 목록을 반환
        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "send_text_email" in tool_names

    def test_send_email_tool_등록_확인(self):
        """
        send_email(Markdown) Tool이 MCP 서버에 등록되어 있는지 확인합니다.
        """
        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "send_email" in tool_names

    def test_등록된_tool_개수_확인(self):
        """
        현재 등록된 Tool이 정확히 2개인지 확인합니다.
        예상치 못한 Tool이 추가되거나 누락되는 것을 방지합니다.
        """
        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert len(tool_names) == 2

    def test_get_kdb_client_반환값_확인(self):
        """
        _get_kdb_client()가 올바른 설정값으로 KdbClient를 생성하는지 확인합니다.
        config.py의 값이 KdbClient에 정확히 전달되어야 합니다.
        """
        from src.mcp_server import _get_kdb_client
        import config

        client = _get_kdb_client()

        # 반환값이 KdbClient 인스턴스인지 확인
        assert isinstance(client, KdbClient)
        # config 값이 올바르게 전달됐는지 확인
        assert client.base_url == config.KDB_BASE_URL
        assert client.token == config.KDB_TOKEN
        assert client.verify_ssl == config.VERIFY_SSL


# ── send_text_email Tool 실행 테스트 ──────────────────────────────────────────

class TestSendTextEmailTool:
    """send_text_email MCP Tool의 동작을 검증하는 테스트"""

    def test_send_text_email_tool_성공(self):
        """
        send_text_email Tool 호출 시 KdbClient.send_text_email이 실행되고
        그 결과를 그대로 반환하는지 확인합니다.
        """
        # 가짜 KdbClient 준비
        mock_client = MagicMock()
        mock_client.send_text_email.return_value = {"message": "Email sent successfully"}

        # src.mcp_server 안의 _get_kdb_client 함수를 가짜로 교체
        # → Tool이 실행될 때 실제 KdbClient 대신 mock_client를 사용하게 됩니다.
        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            result = send_text_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="테스트 제목",
                content="<h1>HTML 본문</h1>",
            )

        # KdbClient.send_text_email이 정확히 1번 호출됐는지 확인
        mock_client.send_text_email.assert_called_once()
        # 반환값이 KdbClient의 응답과 같은지 확인
        assert result == {"message": "Email sent successfully"}

    def test_send_text_email_tool_파라미터_전달_확인(self):
        """
        Tool에 전달된 파라미터가 KdbClient에 그대로 전달되는지 확인합니다.
        파라미터가 중간에 바뀌거나 누락되면 안 됩니다.
        """
        mock_client = MagicMock()
        mock_client.send_text_email.return_value = {"message": "Email sent successfully"}

        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            send_text_email(
                sender_name="홍길동",
                receivers="a@co.com,b@co.com",
                subject="제목",
                content="본문",
            )

        # assert_called_once_with(): 정확히 이 인자로 1번 호출됐는지 검증
        mock_client.send_text_email.assert_called_once_with(
            sender_name="홍길동",
            receivers="a@co.com,b@co.com",
            subject="제목",
            content="본문",
        )

    def test_send_text_email_tool_에러_전파(self):
        """
        KdbClient에서 에러가 발생하면 Tool 밖으로 전달되는지 확인합니다.
        에러를 조용히 무시하면 LLM이 실패를 알 수 없습니다.
        """
        mock_client = MagicMock()
        # KdbClient.send_text_email 호출 시 예외 발생하도록 설정
        mock_client.send_text_email.side_effect = Exception("서버 오류")

        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            with pytest.raises(Exception, match="서버 오류"):
                send_text_email(
                    sender_name="홍길동",
                    receivers="test@company.com",
                    subject="제목",
                    content="본문",
                )


# ── send_email(Markdown) Tool 실행 테스트 ─────────────────────────────────────

class TestSendEmailTool:
    """send_email(Markdown) MCP Tool의 동작을 검증하는 테스트"""

    def test_send_email_tool_성공(self):
        """
        send_email Tool 호출 시 KdbClient.send_email이 실행되고
        그 결과를 반환하는지 확인합니다.
        """
        mock_client = MagicMock()
        mock_client.send_email.return_value = {"message": "Email sent successfully"}

        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            result = send_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="테스트 제목",
                content="# Markdown 본문",
            )

        mock_client.send_email.assert_called_once()
        assert result == {"message": "Email sent successfully"}

    def test_send_email_tool_파라미터_전달_확인(self):
        """
        Tool에 전달된 파라미터가 KdbClient.send_email에 그대로 전달되는지 확인합니다.
        """
        mock_client = MagicMock()
        mock_client.send_email.return_value = {"message": "Email sent successfully"}

        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            send_email(
                sender_name="홍길동",
                receivers="a@co.com",
                subject="Markdown 제목",
                content="# 내용",
            )

        mock_client.send_email.assert_called_once_with(
            sender_name="홍길동",
            receivers="a@co.com",
            subject="Markdown 제목",
            content="# 내용",
        )

    def test_send_email_tool_에러_전파(self):
        """
        KdbClient에서 에러 발생 시 Tool 밖으로 전달되는지 확인합니다.
        """
        mock_client = MagicMock()
        mock_client.send_email.side_effect = Exception("서버 오류")

        with patch("src.mcp_server._get_kdb_client", return_value=mock_client):
            with pytest.raises(Exception, match="서버 오류"):
                send_email(
                    sender_name="홍길동",
                    receivers="test@company.com",
                    subject="제목",
                    content="# 본문",
                )
