"""
[파일 설명]
main.py - MCP 서버 실행 진입점 (Entry Point)

[이 파일의 역할]
VS Code 또는 다른 MCP Client가 MCP 서버를 실행할 때 이 파일을 호출합니다.

[VS Code MCP 설정 예시]
{
  "servers": {
    "kdb_mw": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\경로\\mcp_kdb_mw\\main.py"]
    }
  }
}

[왜 src/mcp_server.py 를 직접 호출하지 않고 main.py를 따로 만드나?]
src/mcp_server.py 를 직접 실행하면 Python이 src 폴더 기준으로
모듈을 찾으려 해서 'import config' 같은 구문이 실패할 수 있습니다.
main.py 는 프로젝트 루트에 있어서 모든 모듈을 올바르게 찾을 수 있습니다.
"""

# sys: Python 실행 환경 관련 도구
import sys

# os: 파일/경로 관련 도구
import os

# Path: 파일 경로를 다루는 도구
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 모듈 검색 경로에 추가합니다.
#
# sys.path: Python이 모듈을 찾을 때 뒤지는 폴더 목록
# insert(0, ...): 맨 앞에 추가 → 가장 먼저 검색
#
# Path(__file__).parent: 이 파일(main.py)이 있는 폴더 = 프로젝트 루트
# str(...): Path 객체를 문자열로 변환 (sys.path는 문자열 목록)
#
# 이게 없으면 'from src.mcp_server import mcp' 가 실패합니다.
sys.path.insert(0, str(Path(__file__).parent))

# MCP 서버 객체를 가져옵니다.
# src/mcp_server.py 에 정의된 mcp 인스턴스입니다.
from src.mcp_server import mcp

if __name__ == "__main__":
    # transport="stdio": LLM과 같은 호스트에서 stdin/stdout으로 통신
    # VS Code(또는 다른 MCP Client)가 이 프로세스를 자식으로 실행하고
    # 표준 입출력으로 MCP 프로토콜 메시지를 주고받습니다.
    mcp.run(transport="stdio")
