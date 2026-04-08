"""
[파일 설명]
test_kdb_client.py - KdbClient 클래스를 검증하는 테스트 코드

[TDD(Test-Driven Development)란?]
테스트를 먼저 작성하고, 그 테스트를 통과하도록 실제 코드를 작성하는 개발 방식입니다.
순서: 테스트 작성 → 실패 확인 → 코드 구현 → 테스트 통과 확인

[왜 테스트 코드가 필요한가?]
나중에 코드를 수정했을 때 기존 기능이 망가지지 않았는지 자동으로 확인할 수 있습니다.
"테스트를 통과한다" = "코드가 의도한 대로 동작한다"

[Mock(가짜 객체)이란?]
실제 kdb_mw 서버 없이 테스트하기 위해 사용합니다.
"서버가 이렇게 응답했다고 가정하자"는 상황을 만들어 테스트합니다.
실제 서버에 의존하지 않으므로 서버가 꺼져 있어도 테스트 가능합니다.
"""

# pytest: Python 테스트 실행 도구 (python -m pytest 명령으로 실행)
import pytest

# unittest.mock: Python 내장 Mock(가짜 객체) 도구
# MagicMock: 아무 속성/메서드나 가진 척할 수 있는 만능 가짜 객체
# patch:     특정 코드를 일시적으로 가짜로 교체하는 도구
from unittest.mock import MagicMock, patch

# 테스트 대상 클래스를 가져옵니다.
# 이 줄에서 에러가 나면 → KdbClient가 아직 구현되지 않은 것 (TDD 첫 단계에서 정상)
from src.kdb_client import KdbClient


# ── 테스트 픽스처(Fixture) ─────────────────────────────────────────────────────
#
# @pytest.fixture 란?
# 여러 테스트에서 공통으로 사용하는 객체를 미리 만들어두는 장치입니다.
# 매 테스트 함수에서 client 인자를 받으면, 이 fixture가 자동으로 실행됩니다.
#
# 왜 fixture를 사용하나?
# 모든 테스트 함수마다 KdbClient(...)를 새로 만드는 코드를 반복하지 않아도 됩니다.
@pytest.fixture
def client():
    """매 테스트마다 테스트용 KdbClient 인스턴스를 새로 만들어 제공합니다."""
    return KdbClient(
        base_url="https://test-server.com",  # 테스트용 가짜 서버 주소
        token="test-token-123",              # 테스트용 가짜 토큰
        verify_ssl=False,                    # SSL 검증 안 함
    )


# ── 초기화(생성) 테스트 ────────────────────────────────────────────────────────
#
# class로 테스트를 묶는 이유:
# 관련된 테스트들을 그룹으로 묶어 구조를 정리하고 가독성을 높입니다.
# TestKdbClientInit 클래스 = "KdbClient 초기화에 관한 테스트들의 모음"
class TestKdbClientInit:
    """KdbClient 객체 생성(초기화)에 관한 테스트 모음"""

    def test_초기화_성공(self, client):
        """
        [테스트 목적]
        KdbClient를 만들 때 전달한 값들이 객체 안에 올바르게 저장되는지 확인합니다.

        assert: "이 조건이 참이어야 한다"는 검증 명령입니다.
        조건이 거짓이면 테스트 실패로 표시됩니다.
        """
        assert client.base_url == "https://test-server.com"
        assert client.token == "test-token-123"
        assert client.verify_ssl is False

    def test_토큰_없이_초기화(self):
        """
        [테스트 목적]
        token을 전달하지 않아도 객체가 정상적으로 만들어지는지 확인합니다.
        token의 기본값이 빈 문자열("")인지 검증합니다.
        """
        # token을 전달하지 않고 생성
        client = KdbClient(base_url="https://test-server.com")
        # 기본값이 빈 문자열인지 확인
        assert client.token == ""

    def test_base_url_필수값(self):
        """
        [테스트 목적]
        base_url 없이 KdbClient를 만들려고 하면 에러가 나는지 확인합니다.

        with pytest.raises(TypeError): 블록 안에서 TypeError가 발생해야 테스트 통과
        TypeError가 발생하지 않으면 → 테스트 실패
        """
        with pytest.raises(TypeError):
            KdbClient()  # base_url 없이 호출 → TypeError 발생해야 함


# ── 텍스트 이메일 발송 테스트 ─────────────────────────────────────────────────
class TestSendTextEmail:
    """send_text_email 메서드에 관한 테스트 모음 (일반 텍스트/HTML 이메일)"""

    def test_텍스트_이메일_발송_성공(self, client):
        """정상 파라미터로 텍스트 이메일 발송 시 성공 응답을 반환하는지 확인"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Email sent successfully"}
        mock_response.raise_for_status = MagicMock()

        with patch("src.kdb_client.httpx.Client") as mock_http:
            mock_http.return_value.__enter__.return_value.post.return_value = mock_response

            result = client.send_text_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="텍스트 이메일 제목",
                content="<h1>HTML 본문</h1>",
            )

        assert result["message"] == "Email sent successfully"

    def test_텍스트_이메일_발송_시_올바른_엔드포인트_호출(self, client):
        """/email/send 경로로 요청을 보내는지 확인"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Email sent successfully"}
        mock_response.raise_for_status = MagicMock()

        with patch("src.kdb_client.httpx.Client") as mock_http:
            mock_post = mock_http.return_value.__enter__.return_value.post
            mock_post.return_value = mock_response

            client.send_text_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="제목",
                content="본문",
            )

            call_args = mock_post.call_args
            assert call_args[0][0] == "/api/v1/email/send"

    def test_텍스트_이메일_sender_name_빈값_예외(self, client):
        """sender_name이 빈 문자열이면 ValueError가 발생하는지 확인"""
        with pytest.raises(ValueError):
            client.send_text_email(
                sender_name="",
                receivers="test@company.com",
                subject="제목",
                content="본문",
            )

    def test_텍스트_이메일_receivers_빈값_예외(self, client):
        """receivers가 빈 문자열이면 ValueError가 발생하는지 확인"""
        with pytest.raises(ValueError):
            client.send_text_email(
                sender_name="홍길동",
                receivers="",
                subject="제목",
                content="본문",
            )

    def test_텍스트_이메일_subject_빈값_예외(self, client):
        """subject가 빈 문자열이면 ValueError가 발생하는지 확인"""
        with pytest.raises(ValueError):
            client.send_text_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="",
                content="본문",
            )


# ── 마크다운 이메일 발송 테스트 ────────────────────────────────────────────────
class TestSendEmail:
    """send_email 메서드에 관한 테스트 모음"""

    def test_이메일_발송_성공(self, client):
        """
        [테스트 목적]
        정상적인 파라미터로 send_email 호출 시 서버 응답을 올바르게 반환하는지 확인합니다.

        [Mock 사용 설명]
        patch("src.kdb_client.httpx.Client"): kdb_client.py 안의 httpx.Client를
        가짜(Mock)로 교체합니다. 실제 HTTP 요청 대신 가짜 응답을 돌려줍니다.

        as mock_http: 교체된 가짜 객체를 mock_http라는 이름으로 사용합니다.
        """
        # 가짜 응답 객체 준비
        # MagicMock(): 어떤 속성이나 메서드에 접근해도 에러 없이 동작하는 가짜 객체
        mock_response = MagicMock()
        # .json() 호출 시 이 값을 반환하도록 설정
        mock_response.json.return_value = {"message": "Email sent successfully"}
        # .raise_for_status() 는 아무것도 하지 않도록 설정 (오류 없음을 의미)
        mock_response.raise_for_status = MagicMock()

        # with patch(...): 이 블록 안에서만 httpx.Client를 가짜로 교체
        with patch("src.kdb_client.httpx.Client") as mock_http:
            # "with 구문으로 사용할 때 .post()의 반환값 = mock_response" 설정
            mock_http.return_value.__enter__.return_value.post.return_value = mock_response

            # 실제 테스트 실행
            result = client.send_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="테스트 제목",
                content="테스트 본문",
            )

        # 반환된 결과가 기대값과 같은지 검증
        assert result["message"] == "Email sent successfully"

    def test_이메일_발송_시_올바른_엔드포인트_호출(self, client):
        """
        [테스트 목적]
        send_email이 "/email/send_markdown" 경로로 요청을 보내는지 확인합니다.
        엔드포인트 경로가 잘못되면 API 호출이 실패하기 때문에 중요합니다.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Email sent successfully"}
        mock_response.raise_for_status = MagicMock()

        with patch("src.kdb_client.httpx.Client") as mock_http:
            # mock_post: .post() 메서드를 별도 변수에 담아 나중에 검사
            mock_post = mock_http.return_value.__enter__.return_value.post
            mock_post.return_value = mock_response

            client.send_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="테스트 제목",
                content="테스트 본문",
            )

            # call_args: mock이 마지막으로 호출된 인자 정보를 담고 있습니다.
            # call_args[0][0]: 첫 번째 위치 인자 = API 경로
            call_args = mock_post.call_args
            assert call_args[0][0] == "/api/v1/email/send_markdown"

    def test_이메일_발송_시_올바른_데이터_전송(self, client):
        """
        [테스트 목적]
        요청 본문(json)에 올바른 데이터가 담겨서 전송되는지 확인합니다.
        파라미터 이름이 kdb_mw가 기대하는 것과 다르면 발송이 실패하기 때문에 중요합니다.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Email sent successfully"}
        mock_response.raise_for_status = MagicMock()

        with patch("src.kdb_client.httpx.Client") as mock_http:
            mock_post = mock_http.return_value.__enter__.return_value.post
            mock_post.return_value = mock_response

            client.send_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="테스트 제목",
                content="# 마크다운 본문",
            )

            # call_args[1]: 키워드 인자 정보 (json=... 으로 전달된 것들)
            call_kwargs = mock_post.call_args[1]
            # json 딕셔너리 안의 각 키 값이 올바른지 확인
            assert call_kwargs["json"]["sender_name"] == "홍길동"
            assert call_kwargs["json"]["receivers"] == "test@company.com"
            assert call_kwargs["json"]["subject"] == "테스트 제목"
            assert call_kwargs["json"]["content"] == "# 마크다운 본문"

    def test_sender_name_빈값_예외(self, client):
        """
        [테스트 목적]
        sender_name이 빈 문자열("")이면 ValueError가 발생하는지 확인합니다.
        빈 이름으로 메일을 보내는 상황을 사전에 차단합니다.
        """
        with pytest.raises(ValueError):
            client.send_email(
                sender_name="",   # 빈 문자열 → ValueError 발생해야 함
                receivers="test@company.com",
                subject="제목",
                content="본문",
            )

    def test_receivers_빈값_예외(self, client):
        """
        [테스트 목적]
        receivers가 빈 문자열("")이면 ValueError가 발생하는지 확인합니다.
        받는 사람 없이 메일을 발송하는 상황을 차단합니다.
        """
        with pytest.raises(ValueError):
            client.send_email(
                sender_name="홍길동",
                receivers="",     # 빈 문자열 → ValueError 발생해야 함
                subject="제목",
                content="본문",
            )

    def test_subject_빈값_예외(self, client):
        """
        [테스트 목적]
        subject(제목)가 빈 문자열("")이면 ValueError가 발생하는지 확인합니다.
        """
        with pytest.raises(ValueError):
            client.send_email(
                sender_name="홍길동",
                receivers="test@company.com",
                subject="",       # 빈 문자열 → ValueError 발생해야 함
                content="본문",
            )

    def test_서버_오류_시_예외_전파(self, client):
        """
        [테스트 목적]
        kdb_mw 서버가 오류를 반환했을 때 예외가 호출자에게 전달되는지 확인합니다.
        서버 오류를 조용히 무시하지 않고 밖으로 알려야 합니다.

        side_effect: Mock이 호출될 때 값을 반환하는 대신 예외를 발생시키도록 설정
        """
        mock_response = MagicMock()
        # raise_for_status()가 호출되면 Exception("서버 오류")을 발생시키도록 설정
        mock_response.raise_for_status.side_effect = Exception("서버 오류")

        with patch("src.kdb_client.httpx.Client") as mock_http:
            mock_http.return_value.__enter__.return_value.post.return_value = mock_response

            # 예외가 밖으로 전달되는지 확인
            with pytest.raises(Exception):
                client.send_email(
                    sender_name="홍길동",
                    receivers="test@company.com",
                    subject="제목",
                    content="본문",
                )
