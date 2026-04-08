# Lessons Learned - MCP Server 개발

## 2026-04-08 | MCP Client와 Server의 위치 관계

### 배경
MCP Server를 SSE/HTTP 네트워크 방식으로 개발했다가,
상사의 피드백으로 잘못된 구조임을 확인하고 수정함.

---

### 잘못 이해했던 구조

```
[이 PC]                          [상사 서버]
사내 LLM ──── SSE/네트워크 ────► MCP Server ──── API ────► kdb_mw
(MCP Client)                    (우리가 만든것)
```

- MCP Client(LLM)와 MCP Server가 네트워크로 연결된 다른 서버에 있는 구조
- server.py에서 `mcp.run(transport="sse")` 사용
- `host=0.0.0.0` 으로 모든 IP에서 접속 허용

---

### 올바른 구조

```
[동일 호스트 - 내부망 서버 1대]          [내부망 다른 서버]
┌──────────────────────────────┐
│  사내 LLM                    │
│  (MCP Client)                │
│       ↕  stdio               │ ──── HTTP REST API ────► kdb_mw
│  MCP Server                  │
│  (우리가 개발)                │
└──────────────────────────────┘
```

- MCP Client(LLM)와 MCP Server는 **반드시 같은 호스트(컴퓨터)**에 있어야 함
- MCP Server가 외부의 kdb_mw와 HTTP API로 통신
- server.py에서 `mcp.run(transport="stdio")` 사용

---

### 핵심 개념: MCP 통신 방식 두 가지

| 방식 | 동작 원리 | 위치 조건 | 사용 시기 |
|---|---|---|---|
| **stdio** | LLM이 MCP Server를 자식 프로세스로 직접 실행. 입출력 파이프로 직접 연결 | 반드시 같은 컴퓨터 | 로컬 실행, 사내 LLM과 함께 배포 |
| **SSE/HTTP** | LLM이 MCP Server에 네트워크로 접속 | 다른 컴퓨터도 가능 | 원격 MCP 서버가 필요한 경우 |

---

### 비유로 이해하기

MCP를 통역사 시스템에 비유:

```
외국인 손님        통역사           현지 서비스
(LLM)        (MCP Server)         (kdb_mw)

"이메일 보내줘" → 요청 변환 → API 요청 전송
              ← "발송 완료" ← API 응답 수신
```

- 통역사(MCP Server)는 손님(LLM) 바로 옆에 붙어 있어야 함
- 통역사가 다른 건물에 있으면 비효율적이고 복잡해짐
- 통역사가 현지 서비스(kdb_mw)에 연락하는 것은 네트워크(전화)로 해도 됨

---

### stdio 방식의 동작 순서

```
1. 사내 LLM 서비스 시작
      ↓
2. LLM이 "python server.py"를 자식 프로세스로 실행
      ↓
3. LLM ↔ MCP Server가 입출력 파이프(stdio)로 직접 연결
      ↓
4. LLM이 "이메일 보내줘" 요청 → MCP Server의 send_email tool 호출
      ↓
5. MCP Server가 kdb_mw에 HTTP REST API 요청
      ↓
6. kdb_mw 응답 → MCP Server → LLM
```

---

### 코드 변경 내용

**Before (잘못된 방식):**
```python
mcp = FastMCP(
    "kdb_mw",
    instructions="...",
    host=MCP_HOST,   # 불필요
    port=MCP_PORT,   # 불필요
)
mcp.run(transport="sse")   # 네트워크 대기
```

**After (올바른 방식):**
```python
mcp = FastMCP(
    "kdb_mw",
    instructions="...",
    # host, port 제거 - stdio는 네트워크 포트 불필요
)
mcp.run(transport="stdio")  # 같은 호스트, 직접 연결
```

---

### 결론

- MCP Client + MCP Server = **같은 호스트에 묶음으로 배포**
- MCP Server + kdb_mw = **HTTP API로 네트워크 통신**
- Docker 배포 시에도 LLM 서비스 컨테이너 안에 MCP Server를 함께 포함시키거나,
  같은 호스트에서 실행되도록 구성해야 함
