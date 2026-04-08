# 요구사항 정의서

- **프로젝트명**: mcp_kdb_mw
- **작성일**: 2026-04-08
- **버전**: v0.1

---

## 1. 프로젝트 개요

사내 LLM 서비스(AI 플랫폼)가 kdb_mw(미들웨어 관리 시스템)의 기능을 사용할 수 있도록
MCP(Model Context Protocol) Server를 개발한다.

### 시스템 구성

```
[동일 호스트 - 내부망]              [내부망 다른 서버]
사내 LLM 서비스 (MCP Client)
      ↕ stdio
  MCP Server (본 프로젝트)  ──── HTTP REST API ────► kdb_mw
```

---

## 2. 기능 요구사항

### Phase 1 - kdb_mw API 호출 기능 ✅ 완료

| ID | 요구사항 | 우선순위 | 상태 |
|---|---|---|---|
| F-001 | kdb_mw 텍스트/HTML 이메일 발송 (`/email/send`) | 필수 | 완료 |
| F-002 | kdb_mw Smart Email 발송 (`/email/send_markdown`, Markdown 지원) | 필수 | 완료 |
| F-003 | 필수 파라미터 누락 시 오류 처리 | 필수 | 완료 |
| F-004 | JWT 토큰 기반 인증 헤더 자동 추가 | 필수 | 완료 |

### Phase 2 - MCP Server 래핑 ✅ 완료

| ID | 요구사항 | 우선순위 | 상태 |
|---|---|---|---|
| F-010 | send_text_email MCP Tool 제공 (`/api/v1/email/send`) | 필수 | 완료 |
| F-011 | send_email MCP Tool 제공 (`/api/v1/email/send_markdown`) | 필수 | 완료 |
| F-012 | stdio 방식 MCP 통신 (LLM과 동일 호스트) | 필수 | 완료 |

### Phase 3 - 배포 가능한 형태 (예정)

| ID | 요구사항 | 우선순위 | 상태 |
|---|---|---|---|
| F-020 | Docker 이미지 빌드 | 필수 | 예정 |
| F-021 | 환경변수 기반 설정 관리 | 필수 | 예정 |

### Phase 4 - 가상 MCP Client (예정)

| ID | 요구사항 | 우선순위 | 상태 |
|---|---|---|---|
| F-030 | MCP Server 연결 및 Tool 목록 조회 | 필수 | 예정 |
| F-031 | Tool 호출 및 결과 출력 | 필수 | 예정 |

---

## 3. 비기능 요구사항

| 항목 | 내용 |
|---|---|
| 테스트 커버리지 | 90% 이상 유지 |
| 개발 방식 | TDD (테스트 우선 개발) |
| 설계 원칙 | SOLID 원칙 준수 |
| 설정 관리 | 하드코딩 금지, config.py 상수화 |
| 비밀값 관리 | .env 파일 분리 (버전관리 제외) |
