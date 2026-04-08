"""
[파일 설명]
test_config.py - 배포 환경에서 설정값이 올바른지 검증하는 테스트

[Phase 3에서 왜 이 테스트가 필요한가?]
Docker 컨테이너로 배포할 때, 환경변수가 누락되면 서버가 조용히 오작동할 수 있습니다.
이 테스트는 "배포에 필요한 모든 설정값이 올바른 형태로 존재하는지"를 검증합니다.

배포 전 체크리스트 역할을 합니다.
"""

import pytest
import os
from unittest.mock import patch


class TestConfigValues:
    """config.py의 설정값이 올바른 형태인지 검증하는 테스트"""

    def test_KDB_BASE_URL_형식_확인(self):
        """
        KDB_BASE_URL이 http:// 또는 https:// 로 시작하는지 확인합니다.
        URL 형식이 잘못되면 모든 API 호출이 실패합니다.
        """
        import config
        assert config.KDB_BASE_URL.startswith("http://") or \
               config.KDB_BASE_URL.startswith("https://"), \
               "KDB_BASE_URL은 http:// 또는 https:// 로 시작해야 합니다."

    def test_REQUEST_TIMEOUT_양수_확인(self):
        """
        REQUEST_TIMEOUT이 0보다 큰 양수인지 확인합니다.
        0 이하이면 모든 요청이 즉시 타임아웃됩니다.
        """
        import config
        assert config.REQUEST_TIMEOUT > 0, \
               "REQUEST_TIMEOUT은 0보다 커야 합니다."

    def test_VERIFY_SSL_bool_타입_확인(self):
        """
        VERIFY_SSL이 True 또는 False (bool 타입)인지 확인합니다.
        문자열 "true"/"false"가 그대로 남아있으면 잘못 동작할 수 있습니다.
        """
        import config
        assert isinstance(config.VERIFY_SSL, bool), \
               "VERIFY_SSL은 bool 타입(True/False)이어야 합니다."

    def test_MCP_SERVER_NAME_비어있지_않음(self):
        """
        MCP_SERVER_NAME이 빈 문자열이 아닌지 확인합니다.
        이름이 없으면 LLM이 서버를 식별할 수 없습니다.
        """
        import config
        assert config.MCP_SERVER_NAME, \
               "MCP_SERVER_NAME은 빈 값일 수 없습니다."

    def test_MCP_SERVER_INSTRUCTIONS_비어있지_않음(self):
        """
        MCP_SERVER_INSTRUCTIONS가 빈 문자열이 아닌지 확인합니다.
        설명이 없으면 LLM이 서버를 올바르게 활용하지 못합니다.
        """
        import config
        assert config.MCP_SERVER_INSTRUCTIONS, \
               "MCP_SERVER_INSTRUCTIONS는 빈 값일 수 없습니다."

    def test_이메일_엔드포인트_슬래시로_시작(self):
        """
        API 엔드포인트 경로가 / 로 시작하는지 확인합니다.
        / 없이 경로를 작성하면 URL이 잘못 조합됩니다.
        예) base_url + "api/v1/email/send" → 잘못된 URL
            base_url + "/api/v1/email/send" → 올바른 URL
        """
        import config
        assert config.ENDPOINT_EMAIL_SEND.startswith("/"), \
               "ENDPOINT_EMAIL_SEND는 /로 시작해야 합니다."
        assert config.ENDPOINT_EMAIL_SEND_MARKDOWN.startswith("/"), \
               "ENDPOINT_EMAIL_SEND_MARKDOWN은 /로 시작해야 합니다."

    def test_KDB_BASE_URL_환경변수_없을때_기본값_사용(self):
        """
        KDB_BASE_URL 환경변수가 없을 때 기본값이 설정되는지 확인합니다.
        배포 환경에서 .env 없이도 기본값으로 동작해야 합니다.
        """
        # 환경변수를 비운 상태로 config를 다시 로드해서 테스트
        with patch.dict(os.environ, {}, clear=True):
            # importlib.reload: 모듈을 다시 불러오는 함수
            import importlib
            import config
            importlib.reload(config)
            # 기본값이 설정됐는지 확인 (빈 문자열이 아님)
            assert config.KDB_BASE_URL != ""

    def test_VERIFY_SSL_환경변수_false_문자열_처리(self):
        """
        VERIFY_SSL 환경변수가 "false" 문자열일 때 Python False로 변환되는지 확인합니다.
        환경변수는 항상 문자열이므로 bool 변환이 중요합니다.
        """
        with patch.dict(os.environ, {"VERIFY_SSL": "false"}):
            import importlib
            import config
            importlib.reload(config)
            assert config.VERIFY_SSL is False

    def test_VERIFY_SSL_환경변수_true_문자열_처리(self):
        """
        VERIFY_SSL 환경변수가 "true" 문자열일 때 Python True로 변환되는지 확인합니다.
        """
        with patch.dict(os.environ, {"VERIFY_SSL": "true"}):
            import importlib
            import config
            importlib.reload(config)
            assert config.VERIFY_SSL is True
