"""
[파일 설명]
kdb_client.py - kdb_mw 서버와 HTTP 통신을 담당하는 클라이언트 모듈

[SOLID 원칙 중 S - 단일 책임 원칙 적용]
이 파일은 오직 "kdb_mw API를 호출하는 것" 만 담당합니다.
MCP 프로토콜, 설정 관리 등 다른 일은 하지 않습니다.
한 파일이 하나의 일만 하면 나중에 문제가 생겼을 때 찾기 쉽습니다.

[이 파일의 역할]
MCP Server나 테스트 코드가 kdb_mw API를 호출하고 싶을 때
이 파일의 KdbClient 클래스를 사용합니다.
실제 HTTP 통신의 복잡한 부분(헤더 설정, 인증 등)을 여기서 처리합니다.
"""

# httpx: Python에서 HTTP 요청을 보내는 도구
# HTTP 요청: 웹 서버에 데이터를 요청하거나 전송하는 방법
# (브라우저가 웹사이트를 열 때 하는 것과 같은 동작을 코드에서 수행)
import httpx

# config.py에서 설정값을 가져옵니다.
# "import config"를 하면 config.py의 모든 값을 config.변수명 으로 사용 가능
import config


class KdbClient:
    """
    [클래스란?]
    클래스는 관련된 데이터와 기능을 하나로 묶은 '설계도'입니다.
    이 설계도로 실제 객체(인스턴스)를 만들어 사용합니다.

    예시) KdbClient 설계도로 client 객체를 만들어서 사용:
        client = KdbClient(base_url="https://...", token="abc123")
        client.send_email(...)

    [이 클래스의 역할]
    kdb_mw 서버와의 HTTP 통신을 담당합니다.
    kdb_mw API를 호출하는 모든 기능이 이 클래스 안에 모여있습니다.
    """

    def __init__(
        self,
        base_url: str,                         # 필수값: 서버 주소
        token: str = "",                        # 선택값: JWT 토큰 (없으면 빈 문자열)
        verify_ssl: bool = False,               # 선택값: SSL 검증 여부
        timeout: float = config.REQUEST_TIMEOUT, # 선택값: 타임아웃 (config 기본값 사용)
    ):
        """
        [__init__ 메서드란?]
        클래스로 객체를 만들 때 자동으로 실행되는 '초기화 함수'입니다.
        객체가 사용할 데이터를 저장하는 역할을 합니다.

        예시) client = KdbClient(base_url="https://...", token="abc")
              → __init__이 자동 실행되어 base_url, token 등을 저장

        [파라미터 설명]
        self:       이 객체 자신을 가리키는 특별한 인자 (Python의 관례)
        base_url:   kdb_mw 서버 주소 (예: https://mamama.iptime.org:8000)
        token:      JWT 인증 토큰. 기본값은 빈 문자열("")
        verify_ssl: SSL 인증서 검증 여부. 기본값은 False (사설 인증서 허용)
        timeout:    응답 대기 시간(초). 기본값은 config.py의 REQUEST_TIMEOUT

        [타입 힌트란? (예: base_url: str)]
        변수가 어떤 종류의 값을 담아야 하는지 알려주는 표시입니다.
        str  = 문자열 (텍스트), bool = 참/거짓, float = 소수점 숫자
        실행에는 영향을 주지 않지만, 코드를 읽는 사람에게 도움이 됩니다.
        """

        # self.변수명 = 값 → 이 객체 안에 값을 저장합니다.
        # 나중에 다른 메서드에서 self.base_url 로 꺼내 쓸 수 있습니다.
        self.base_url = base_url
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    def _get_headers(self) -> dict:
        """
        [메서드란?]
        클래스 안에 정의된 함수를 메서드라고 합니다.

        [이 메서드의 역할]
        HTTP 요청 시 함께 보낼 헤더(Header)를 만들어 반환합니다.
        헤더는 편지의 봉투 정보 같은 것입니다. (보낸 사람, 인증 정보 등)

        [메서드 이름 앞의 _ 표시]
        _get_headers 처럼 이름 앞에 _가 붙으면 "이 클래스 내부에서만 쓰는 메서드"
        라는 약속입니다. 외부에서 직접 호출하지 않습니다.

        Returns:
            dict: 헤더 정보를 담은 딕셔너리
                  토큰이 있으면 → {"Authorization": "Bearer abc123..."}
                  토큰이 없으면 → {}  (빈 딕셔너리)
        """

        # dict(딕셔너리): 키-값 쌍을 저장하는 자료구조
        # {} 는 빈 딕셔너리를 만듭니다. (텅 빈 서랍장)
        headers = {}

        # if self.token: 은 "token에 값이 있으면" 이라는 조건입니다.
        # 빈 문자열("")은 조건에서 False로 취급됩니다.
        if self.token:
            # f"Bearer {self.token}" 은 f-string 문법입니다.
            # {} 안의 변수 값이 문자열에 삽입됩니다.
            # 예: self.token = "abc123" → "Bearer abc123"
            #
            # "Authorization: Bearer 토큰" 은 HTTP 인증의 표준 방식입니다.
            # kdb_mw 서버는 이 헤더를 보고 "인증된 요청이다" 라고 판단합니다.
            headers["Authorization"] = f"Bearer {self.token}"

        # 만들어진 헤더 딕셔너리를 반환합니다.
        return headers

    def _get_http_client(self) -> httpx.Client:
        """
        [이 메서드의 역할]
        kdb_mw 서버에 요청을 보낼 HTTP 클라이언트 객체를 만들어 반환합니다.
        브라우저처럼 웹 서버에 요청을 보낼 수 있는 도구를 준비합니다.

        Returns:
            httpx.Client: HTTP 요청을 보낼 수 있는 클라이언트 객체
        """

        return httpx.Client(
            # base_url: 모든 요청 앞에 자동으로 붙는 기본 주소
            # 예: base_url="https://서버" 이고 client.get("/health") 하면
            #     실제로는 https://서버/health 로 요청됩니다.
            base_url=self.base_url,

            # headers: 모든 요청에 자동으로 포함될 헤더 (인증 토큰 등)
            headers=self._get_headers(),

            # verify: SSL 인증서 검증 여부
            verify=self.verify_ssl,

            # timeout: 응답을 기다리는 최대 시간 (초)
            timeout=self.timeout,
        )

    def send_text_email(
        self,
        sender_name: str,
        receivers: str,
        subject: str,
        content: str,
    ) -> dict:
        """
        [이 메서드의 역할]
        kdb_mw의 일반 이메일 API를 호출하여 텍스트/HTML 형식의 이메일을 발송합니다.
        content에 HTML 태그를 직접 사용할 수 있습니다.

        [send_text_email vs send_email 차이]
        send_text_email : content를 그대로 발송 (텍스트 또는 HTML)
        send_email      : content를 Markdown → HTML로 자동 변환 후 발송

        Args:
            sender_name: 보내는 사람 이름 (예: "홍길동")
            receivers:   받는 사람 이메일. 여러 명은 쉼표로 구분
            subject:     이메일 제목
            content:     이메일 본문 (텍스트 또는 HTML 태그 직접 사용 가능)

        Returns:
            dict: kdb_mw 서버의 응답
                  성공 예시: {"message": "Email sent successfully"}

        Raises:
            ValueError: 필수 파라미터가 빈 값인 경우
            Exception:  서버 오류 발생 시
        """
        # 입력값 검증 (빈 값 허용 안 함)
        if not sender_name:
            raise ValueError("sender_name은 필수값입니다.")
        if not receivers:
            raise ValueError("receivers는 필수값입니다.")
        if not subject:
            raise ValueError("subject는 필수값입니다.")

        with self._get_http_client() as client:
            response = client.post(
                # 일반 텍스트/HTML 이메일 엔드포인트 (config.py에서 가져옴)
                config.ENDPOINT_EMAIL_SEND,
                json={
                    "sender_name": sender_name,
                    "receivers":   receivers,
                    "subject":     subject,
                    "content":     content,
                },
            )
            response.raise_for_status()
            return response.json()

    def send_email(
        self,
        sender_name: str,
        receivers: str,
        subject: str,
        content: str,
    ) -> dict:
        """
        [이 메서드의 역할]
        kdb_mw의 Smart Email API를 호출하여 사내 이메일을 발송합니다.
        content를 Markdown 형식으로 작성하면 kdb_mw가 자동으로
        예쁜 HTML 이메일로 변환해서 발송해줍니다.

        [Markdown이란?]
        # 제목, **굵게**, - 목록 등 간단한 기호로 서식을 표현하는 문서 형식입니다.
        예: "# 장애 보고" → 이메일에서 큰 제목으로 표시됨

        Args (인자 설명):
            self:        이 객체 자신 (Python이 자동으로 전달, 직접 입력 불필요)
            sender_name: 보내는 사람 이름 (예: "홍길동")
            receivers:   받는 사람 이메일. 여러 명은 쉼표로 구분
                         (예: "kim@co.com,lee@co.com")
            subject:     이메일 제목 (예: "일일 WAS 현황 보고")
            content:     이메일 본문, Markdown 형식으로 작성

        Returns (반환값):
            dict: kdb_mw 서버의 응답
                  성공 예시: {"return_code": 0, "message": "success"}
                  실패 예시: {"return_code": 1, "message": "오류 내용"}

        Raises (발생 가능한 에러):
            ValueError: sender_name, receivers, subject 중 하나가 빈 값일 때
            Exception:  kdb_mw 서버가 오류 응답(4xx, 5xx)을 반환할 때
        """

        # ── 입력값 검증 (빈 값 체크) ──────────────────────────────────────────
        # 필수 파라미터가 빈 문자열이면 ValueError를 발생시킵니다.
        # raise: 에러를 강제로 발생시키는 키워드
        # ValueError: "값이 잘못됐다"는 의미의 Python 내장 에러 종류
        #
        # 이렇게 미리 검증하면 잘못된 값이 서버까지 전달되는 것을 막을 수 있습니다.
        if not sender_name:
            raise ValueError("sender_name은 필수값입니다.")
        if not receivers:
            raise ValueError("receivers는 필수값입니다.")
        if not subject:
            raise ValueError("subject는 필수값입니다.")

        # ── HTTP POST 요청으로 이메일 발송 ────────────────────────────────────
        # with ... as client: 문법 (컨텍스트 매니저)
        # 블록이 시작될 때 HTTP 연결을 열고, 블록이 끝나면 자동으로 닫습니다.
        # 직접 닫지 않아도 되므로 실수로 연결을 열어두는 문제를 방지합니다.
        with self._get_http_client() as client:

            # client.post(): HTTP POST 방식으로 서버에 데이터를 전송합니다.
            # GET  요청: 데이터를 조회할 때 (브라우저 주소창에서 페이지 열기)
            # POST 요청: 데이터를 서버로 전송할 때 (로그인, 메일 발송 등)
            response = client.post(
                # 요청을 보낼 API 경로 (config.py에서 가져옴 - 하드코딩 금지)
                config.ENDPOINT_EMAIL_SEND_MARKDOWN,

                # json=: 전송할 데이터를 JSON 형식으로 담습니다.
                # JSON: 데이터를 키-값 형태로 표현하는 표준 형식
                # 예: {"sender_name": "홍길동", "receivers": "kim@co.com", ...}
                json={
                    "sender_name": sender_name,
                    "receivers":   receivers,
                    "subject":     subject,
                    "content":     content,
                },
            )

            # raise_for_status(): 서버가 오류 응답(예: 401 인증실패, 500 서버오류)을
            # 보냈다면 자동으로 예외(Exception)를 발생시킵니다.
            # 이 줄이 없으면 오류가 발생해도 그냥 넘어갈 수 있습니다.
            response.raise_for_status()

            # response.json(): 서버 응답 본문을 Python 딕셔너리로 변환합니다.
            # 서버는 JSON 문자열로 응답 → Python dict로 변환해서 반환
            # 예: '{"return_code": 0, "message": "success"}' → {"return_code": 0, ...}
            return response.json()
