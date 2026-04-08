# kdb_mw MCP Server

> **kdb_mw(리발소) 미들웨어를 통해 사내 LLM이 이메일을 발송할 수 있게 해주는 MCP 서버**

---

## 이 프로그램이 무엇인가요?

### 쉽게 설명하면

사내 LLM(AI 채팅 서비스)에게 **"팀장님께 WAS 장애 현황 보고 메일 보내줘"** 라고 말하면,
AI가 직접 사내 메일을 작성하고 발송해주는 기능입니다.

이것을 가능하게 해주는 중간 다리 역할이 바로 이 **MCP 서버**입니다.

```
사용자 → LLM(AI) → [MCP 서버] → kdb_mw → 사내 메일 발송
```

### MCP(Model Context Protocol)란?

LLM(AI)이 외부 도구를 사용할 수 있도록 Anthropic이 만든 표준 통신 규약입니다.
MCP 서버를 통해 LLM이 "도구(Tool)"를 사용할 수 있게 됩니다.

예를 들어, 이 MCP 서버를 연결하면 LLM은 `send_email`이라는 도구를 사용할 수 있게 되고,
사용자가 메일 발송을 요청하면 AI가 자동으로 이 도구를 호출합니다.

---

## 전체 동작 구조

```
┌─────────────────────────────────────────────────────────┐
│                  로컬 Windows PC / 서버                   │
│                                                           │
│   ┌──────────────────┐   stdio 통신    ┌──────────────┐  │
│   │  VS Code + LLM   │ ─────────────→ │  MCP 서버    │  │
│   │  (MCP Client)    │ ←───────────── │  (main.py)   │  │
│   └──────────────────┘                └──────┬───────┘  │
│                                              │           │
└──────────────────────────────────────────────┼───────────┘
                                               │ HTTP REST API
                                               ↓
                                    ┌──────────────────────┐
                                    │  kdb_mw 서버 (사내망)  │
                                    │  POST /api/v1/email  │
                                    └──────────────────────┘
```

**통신 방식 설명:**
- **stdio**: LLM이 이 MCP 서버를 직접 실행하고, 표준 입출력(키보드/화면)으로 통신합니다.
  네트워크 포트를 별도로 열 필요 없이 같은 PC 내에서 동작합니다.
- **HTTP REST API**: MCP 서버가 kdb_mw 서버에 이메일 발송 요청을 보냅니다.

---

## 제공되는 기능 (Tool 목록)

| Tool 이름 | 설명 | 언제 사용? |
|---|---|---|
| `send_text_email` | 텍스트/HTML 형식 이메일 발송 | HTML 태그를 직접 작성할 때 |
| `send_email` | Markdown → HTML 자동 변환 이메일 발송 | 표, 목록, 강조 등 서식이 필요할 때 |

**공통 파라미터:**

| 파라미터 | 설명 | 예시 |
|---|---|---|
| `sender_name` | 보내는 사람 이름 | `"리발소 시스템"` |
| `receivers` | 받는 사람 이메일 (여러 명은 쉼표로 구분) | `"kim@co.com,lee@co.com"` |
| `subject` | 이메일 제목 | `"[긴급] WAS 서버 장애 현황"` |
| `content` | 이메일 본문 (HTML 또는 Markdown) | `"# 제목\n- 항목1"` |

---

## 프로젝트 구조

```
mcp_kdb_mw/
│
├── main.py                  ← VS Code에서 실행하는 진입점 (이 파일을 실행!)
├── config.py                ← 모든 설정값 관리 (URL, 토큰, API 경로 등)
├── requirements.txt         ← 필요한 Python 패키지 목록
├── install_offline.bat      ← 인터넷 없는 환경(폐쇄망)에서 패키지 설치 스크립트
│
├── .env                     ← 비밀값 저장 파일 (직접 만들어야 함, Git에 올라가지 않음)
│
├── src/
│   ├── kdb_client.py        ← kdb_mw API 호출 담당 (HTTP 통신)
│   └── mcp_server.py        ← MCP Tool 등록 담당
│
├── tests/
│   ├── test_config.py       ← 설정값 테스트
│   ├── test_kdb_client.py   ← API 클라이언트 테스트 (커버리지 100%)
│   └── test_mcp_server.py   ← MCP 서버 테스트 (커버리지 100%)
│
├── wheels/                  ← 오프라인 설치용 패키지 파일 38개
│
└── docs/
    ├── guide.md             ← 상세 설치/연동 가이드
    └── requirements.md      ← 기능 요구사항 문서
```

---

## 설치 방법

> 💡 **인터넷이 되는 환경**과 **인터넷이 안 되는 폐쇄망 환경** 두 가지 방법을 모두 안내합니다.

### 사전 요구사항

| 항목 | 요구사항 |
|---|---|
| OS | Windows 10/11 또는 Windows Server 2019/2022 |
| Python | 3.10 이상 (권장: 3.12) |
| VS Code | 최신 버전 |
| kdb_mw 접근 | kdb_mw 서버에 네트워크 접근 가능한 환경 |

Python이 설치되어 있는지 확인하려면 명령 프롬프트(cmd)에서:
```
python --version
```
`Python 3.x.x` 처럼 출력되면 OK입니다.

---

### [방법 1] 인터넷이 되는 환경에서 설치

**Step 1. 프로젝트 파일 받기**

GitHub에서 ZIP으로 다운로드하거나, git clone으로 받습니다:
```bash
git clone https://github.com/hipiboy7/kdb_mw_mcpserver.git
cd kdb_mw_mcpserver
```

또는 GitHub 페이지에서 `Code → Download ZIP`으로 다운로드 후 압축 해제

**Step 2. Python 패키지 설치**

명령 프롬프트(cmd) 또는 PowerShell을 열고:
```bash
cd C:\mcp_kdb_mw
pip install -r requirements.txt
```

설치 확인:
```bash
python -c "import mcp; print('설치 완료!')"
```
`설치 완료!` 가 출력되면 OK입니다.

---

### [방법 2] 인터넷이 없는 폐쇄망 환경에서 설치

`wheels/` 폴더 안에 필요한 패키지 파일이 모두 포함되어 있습니다.
인터넷 없이도 설치 가능합니다.

**Step 1. 프로젝트 폴더를 폐쇄망 PC로 복사**

USB 또는 내부 파일 서버를 통해 전체 폴더를 복사합니다.

예시 복사 경로:
```
C:\mcp_kdb_mw\
```

**Step 2. 오프라인 설치 스크립트 실행**

파일 탐색기에서 `install_offline.bat`을 **더블클릭**합니다.

또는 명령 프롬프트에서:
```bash
cd C:\mcp_kdb_mw
install_offline.bat
```

설치가 완료되면 `설치 완료!` 메시지가 표시됩니다.

---

### Step 3. .env 파일 만들기 (필수!)

`.env` 파일은 서버 주소와 인증 토큰을 저장하는 파일입니다.
보안상 중요하므로 **직접 만들어야 합니다** (Git에는 올라가지 않음).

프로젝트 루트 폴더(`C:\mcp_kdb_mw\`)에 `.env` 파일을 만들고 아래 내용을 입력:

```
KDB_BASE_URL=http://kdb_mw서버주소:포트
KDB_TOKEN=여기에JWT토큰입력
VERIFY_SSL=false
```

**예시:**
```
KDB_BASE_URL=http://192.168.1.100:8000
KDB_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VERIFY_SSL=false
```

> **⚠️ 주의:** `.env` 파일명 앞에 점(`.`)이 있습니다. 메모장에서 저장할 때 파일명을 `.env`로 입력하고, 파일 형식을 `모든 파일(*.*)`로 선택해야 합니다.

**JWT 토큰 발급 방법:**

브라우저에서 kdb_mw에 로그인 후 아래 URL 접속:
```
http://kdb_mw서버주소/common/generate_long_term_token
```
응답으로 받은 토큰 값을 `KDB_TOKEN=` 뒤에 붙여넣습니다. (365일 유효)

---

### Step 4. 동작 확인

명령 프롬프트에서:
```bash
cd C:\mcp_kdb_mw
python main.py
```

아무 출력 없이 **대기 상태**가 되면 정상입니다.
(LLM이 연결할 때까지 기다리는 상태입니다)

`Ctrl+C`로 종료합니다.

---

## VS Code 연동 설정

MCP 서버를 VS Code의 LLM 서비스와 연결하는 방법입니다.

### Claude 확장 프로그램 사용 시

VS Code 프로젝트 폴더 안에 `.vscode/mcp.json` 파일을 만들고 아래 내용을 입력합니다:

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

> **⚠️ 주의:** Windows 경로에서 `\`(역슬래시)는 `\\`(두 번)으로 써야 합니다.
> 예: `C:\mcp_kdb_mw` → `C:\\mcp_kdb_mw`

설정 파일을 저장하면 VS Code가 자동으로 MCP 서버를 인식합니다.

### Claude Desktop 사용 시

아래 파일을 텍스트 편집기로 열어 내용을 추가합니다.

**파일 위치:**
```
C:\Users\사용자이름\AppData\Roaming\Claude\claude_desktop_config.json
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

설정 후 Claude Desktop을 **완전히 종료 후 재시작**하면 적용됩니다.

---

## 사용 방법 (LLM에게 이렇게 요청하세요)

MCP 서버가 연결되면 LLM에게 자연어로 요청하면 됩니다.

### 예시 1 - 장애 보고 메일

```
WAS 서버 장애가 발생했어. 팀장님(manager@company.com)께
장애 현황을 Markdown으로 정리해서 보고 메일 보내줘.
보내는 사람은 "리발소 시스템"으로 해줘.
```

→ LLM이 자동으로 `send_email` 도구를 호출합니다.

### 예시 2 - 정기 보고

```
오늘 일일 미들웨어 현황 보고서를 
team@company.com으로 발송해줘.
제목은 "[일일보고] JEUS/WEBTOB 현황"으로 해줘.
```

### 예시 3 - 여러 명에게 발송

```
아래 사람들에게 메일 보내줘:
받는 사람: hong@company.com, kim@company.com
제목: 서버 점검 완료 안내
내용: 오늘 오전 2시 예정된 서버 점검이 완료되었습니다.
```

---

## 테스트 실행 방법

개발자나 담당자가 코드가 정상 동작하는지 확인할 때 사용합니다.

```bash
cd C:\mcp_kdb_mw

# 전체 테스트 실행
python -m pytest tests/ -v

# 커버리지(테스트 커버율) 포함 실행
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

**테스트 커버리지: 100%** (모든 코드가 테스트로 검증되었습니다)

---

## 문제 해결

| 증상 | 원인 | 해결 방법 |
|---|---|---|
| `ModuleNotFoundError: mcp` | 패키지 미설치 | `pip install -r requirements.txt` 실행 |
| `401 Unauthorized` | 토큰 만료 또는 누락 | `.env`의 `KDB_TOKEN` 재발급 후 업데이트 |
| `Connection refused` or `Connection Error` | 서버 주소 오류 | `.env`의 `KDB_BASE_URL` 확인 |
| `.env` 파일을 못 찾음 | 파일 위치 오류 | `main.py`와 같은 폴더에 `.env` 위치 확인 |
| VS Code에서 Tool이 보이지 않음 | `mcp.json` 경로 오류 | `args`의 `main.py` 전체 경로 재확인 |
| `python` 명령어를 찾을 수 없음 | Python 미설치 or PATH 미등록 | Python 설치 후 환경변수 PATH에 추가 |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| 언어 | Python 3.10+ |
| MCP SDK | [FastMCP](https://github.com/jlowin/fastmcp) (`mcp[cli]` >= 1.27.0) |
| HTTP 클라이언트 | httpx >= 0.28.0 |
| 환경변수 관리 | python-dotenv >= 1.0.0 |
| 테스트 | pytest + pytest-cov |
| 설계 원칙 | SOLID (단일 책임, 의존성 역전) |

---

## 개발 이력

| 버전 | 내용 |
|---|---|
| v1.0 | Phase 1: kdb_mw API 클라이언트 구현 (`send_text_email`, `send_email`) |
| v2.0 | Phase 2: MCP Tool 등록 및 stdio 통신 방식 구현 |
| v3.0 | Phase 3: 폐쇄망 오프라인 설치 지원 (wheels/ 포함), VS Code 연동 가이드 추가 |

---

## 관련 링크

- [kdb_mw 원본 레포지토리](https://github.com/tanminkwan/kdb_mw)
- [MCP 공식 문서](https://modelcontextprotocol.io)
