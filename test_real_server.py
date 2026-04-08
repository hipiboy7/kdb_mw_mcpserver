"""
[파일 설명]
test_real_server.py - 실제 kdb_mw 서버에 직접 요청을 보내는 수동 테스트 스크립트

[주의]
이 파일은 pytest 자동 테스트가 아닙니다.
실제 서버가 켜져 있고, .env에 KDB_TOKEN이 설정된 상태에서
python test_real_server.py 로 직접 실행합니다.

[실행 방법]
1. .env 파일에 KDB_TOKEN 값을 설정합니다.
2. 터미널에서: python test_real_server.py
"""

# sys: 프로그램 실행과 관련된 기능 제공 (종료, 경로 등)
import sys

# Windows 터미널에서 한글이 깨지지 않도록 출력 인코딩을 UTF-8로 설정합니다.
sys.stdout.reconfigure(encoding='utf-8')

# src 폴더를 Python이 찾을 수 있도록 경로에 추가합니다.
# 이 줄이 없으면 "from src.kdb_client import KdbClient" 가 실패합니다.
sys.path.insert(0, ".")

import config
from src.kdb_client import KdbClient


def print_separator(title: str):
    """구분선 출력 함수 - 테스트 결과를 보기 좋게 나눕니다."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def test_텍스트_이메일_발송(client: KdbClient, my_email: str):
    """
    /api/v1/email/send 실제 호출 테스트
    일반 HTML 이메일이 발송되는지 확인합니다.
    """
    print_separator("테스트 1: 텍스트/HTML 이메일 발송")

    try:
        result = client.send_text_email(
            sender_name="MCP 테스트",
            receivers=my_email,
            subject="[MCP 테스트] 텍스트 이메일 발송 확인",
            content="<h1>테스트 성공</h1><p>KdbClient.send_text_email() 정상 동작 확인</p>",
        )
        # 응답 결과 출력
        print(f"결과: {result}")
        print(">>> 성공! 이메일을 확인해보세요.")

    except Exception as e:
        # 에러 발생 시 원인 출력
        print(f">>> 실패: {e}")


def test_마크다운_이메일_발송(client: KdbClient, my_email: str):
    """
    /api/v1/email/send_markdown 실제 호출 테스트
    Markdown이 HTML로 변환되어 발송되는지 확인합니다.
    """
    print_separator("테스트 2: Markdown 이메일 발송")

    # Markdown 본문 예시 (# = 제목, ** = 굵게, - = 목록)
    markdown_content = """# MCP 테스트 보고

## 테스트 항목
- KdbClient 초기화: **정상**
- 실제 서버 연결: **정상**
- Markdown 변환: **확인 중**

## 결론
MCP Server 개발 Phase 1 완료
"""

    try:
        result = client.send_email(
            sender_name="MCP 테스트",
            receivers=my_email,
            subject="[MCP 테스트] Markdown 이메일 발송 확인",
            content=markdown_content,
        )
        print(f"결과: {result}")
        print(">>> 성공! 이메일을 확인해보세요.")

    except Exception as e:
        print(f">>> 실패: {e}")


def main():
    """
    메인 함수 - 테스트 순서대로 실행합니다.
    Python에서 main() 함수는 프로그램의 시작점 역할을 합니다.
    """

    print_separator("실제 서버 연결 테스트 시작")
    print(f"서버 주소: {config.KDB_BASE_URL}")

    # 토큰 확인
    if not config.KDB_TOKEN:
        print("\n[오류] .env 파일에 KDB_TOKEN이 설정되지 않았습니다.")
        print("  1. 브라우저에서 로그인 후 아래 URL 접속:")
        print(f"     {config.KDB_BASE_URL}/api/v1/common/generate_long_term_token")
        print("  2. 응답받은 토큰을 .env 파일의 KDB_TOKEN= 에 붙여넣으세요.")
        sys.exit(1)  # 프로그램 종료 (1 = 오류로 종료)

    print("토큰: 설정됨 (앞 10자리:", config.KDB_TOKEN[:10], "...)")

    # KdbClient 생성
    client = KdbClient(
        base_url=config.KDB_BASE_URL,
        token=config.KDB_TOKEN,
        verify_ssl=config.VERIFY_SSL,
    )

    # 테스트 받을 이메일 주소 입력 받기
    # input(): 사용자에게 키보드 입력을 받는 함수
    my_email = input("\n테스트 이메일을 받을 주소를 입력하세요: ").strip()
    if not my_email:
        print("이메일 주소를 입력해야 합니다.")
        sys.exit(1)

    # 테스트 실행
    test_텍스트_이메일_발송(client, my_email)
    test_마크다운_이메일_발송(client, my_email)

    print_separator("테스트 완료")


# 이 파일을 직접 실행할 때만 main()을 호출합니다.
# (다른 파일에서 import할 때는 실행되지 않음)
if __name__ == "__main__":
    main()
