# mcp_kdb_mw 사용 가이드

- **버전**: v0.3
- **작성일**: 2026-04-08
- **실행 방식**: Python 직접 실행 (로컬 Windows PC)

---

## 1. 개요

이 MCP 서버는 kdb_mw(리발소)의 이메일 API를 LLM이 사용할 수 있도록 래핑합니다.
VS Code 등 MCP를 지원하는 도구에서 "이메일 보내줘"라고 하면
실제 kdb_mw를 통해 사내 이메일이 발송됩니다.

---

## 2. 설치 환경 요구사항

| 항목 | 요구사항 |
|---|---|
| OS | Windows 10/11 또는 Windows Server |
| Python | 3.10 이상 (권장: 3.12) |
| 에디터 | Visual Studio Code |
| 네트워크 | kdb_mw 서버 접근 가능한 환경 |

---

## 3. 설치 방법

### Step 1. 프로젝트 파일 준비

개발 서버에서 로컬 PC로 프로젝트 폴더를 복사합니다.
복사 후 원하는 경로에 저장합니다.

예시 경로:
```
C:\mcp_kdb_mw\
```

### Step 2. Python 패키지 설치

Windows 명령 프롬프트(cmd) 또는 PowerShell을 열고:

```bash
cd C:\mcp_kdb_mw
pip install -r requirements.txt
```

설치 확인:
```bash
python -c "import mcp; print('OK')"
```
`OK` 가 출력되면 정상입니다.

### Step 3. .env 파일 준비

프로젝트 루트(`C:\mcp_kdb_mw\`)에 `.env` 파일을 만들고 아래 내용을 입력합니다:

```
KDB_BASE_URL=http://<kdb_mw_서버_주소>
KDB_TOKEN=<발급받은_JWT_토큰>
VERIFY_SSL=false
```

**JWT 토큰 발급 방법:**
브라우저에서 kdb_mw에 로그인 후 아래 URL 접속:
```
http://<kdb_mw_서버_주소>/api/v1/common/generate_long_term_token
```
응답으로 받은 토큰을 `KDB_TOKEN=` 뒤에 붙여넣습니다. (365일 유효)

### Step 4. 동작 확인

```bash
cd C:\mcp_kdb_mw
python main.py
```

아무 출력 없이 대기 상태가 되면 정상입니다.
(stdio 방식이라 MCP Client가 연결될 때까지 기다립니다)
`Ctrl+C` 로 종료합니다.

---

## 4. VS Code 연동 설정

### 4-1. Claude 확장 프로그램 사용 시 (MCP 설정 파일)

VS Code 에서 사용하는 MCP 설정 파일에 아래 내용을 추가합니다.

**`.vscode/mcp.json`** (프로젝트별 설정):
```json
{
  "servers": {
    "kdb_mw": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\mcp_kdb_mw\\main.py"]
    }
  }
}
```

**주의:** Windows 경로에서 `\` 는 `\\` 로 써야 합니다.

### 4-2. Claude Desktop 사용 시

`claude_desktop_config.json` 파일에 아래 내용 추가:

**파일 위치:**
```
C:\Users\<사용자명>\AppData\Roaming\Claude\claude_desktop_config.json
```

**추가 내용:**
```json
{
  "mcpServers": {
    "kdb_mw": {
      "command": "python",
      "args": ["C:\\mcp_kdb_mw\\main.py"]
    }
  }
}
```

설정 후 Claude Desktop을 **재시작**하면 적용됩니다.

---

## 5. 제공되는 Tool 목록

| Tool 이름 | 설명 |
|---|---|
| `send_text_email` | 텍스트/HTML 형식 이메일 발송 |
| `send_email` | Markdown 형식 이메일 발송 (자동 HTML 변환) |

**공통 파라미터:**

| 파라미터 | 설명 | 예시 |
|---|---|---|
| sender_name | 보내는 사람 이름 | "리발소 시스템" |
| receivers | 받는 사람 이메일 (쉼표로 여러 명 가능) | "kim@co.com,lee@co.com" |
| subject | 이메일 제목 | "[알림] 서버 점검 완료" |
| content | 이메일 본문 | HTML 또는 Markdown |

### 사용 예시

**LLM에게 이렇게 요청:**
> "WAS 장애 현황 정리해서 팀장님한테 메일 보내줘"

**LLM이 자동으로 `send_email` 호출:**
```json
{
  "sender_name": "리발소 시스템",
  "receivers": "manager@company.com",
  "subject": "[긴급] WAS 장애 현황",
  "content": "# WAS 장애 현황\n\n- WAS-01: **다운**\n- 조치: 재시작 진행 중"
}
```

---

## 6. 문제 해결

| 증상 | 원인 | 해결 방법 |
|---|---|---|
| `ModuleNotFoundError: mcp` | 패키지 미설치 | `pip install -r requirements.txt` |
| `401 Unauthorized` | 토큰 만료/누락 | 토큰 재발급 후 `.env` 업데이트 |
| `Connection Error` | KDB_BASE_URL 오류 | `.env`의 URL 확인 |
| `.env` 파일 못 찾음 | 경로 문제 | `main.py`와 같은 폴더에 `.env` 위치 확인 |
| Tool 목록이 보이지 않음 | `args` 경로 오류 | `mcp.json` 의 `main.py` 경로 재확인 |
