@echo off
:: ============================================================
:: install_offline.bat - 인터넷 없이 패키지를 설치하는 스크립트
::
:: [사용 방법]
:: 1. 이 파일을 더블클릭 하거나
:: 2. 명령 프롬프트에서: install_offline.bat
::
:: [동작 원리]
:: wheels/ 폴더에 저장된 .whl 파일들을 사용해서
:: 인터넷 없이 pip 패키지를 설치합니다.
:: ============================================================

echo.
echo ====================================================
echo  mcp_kdb_mw 오프라인 패키지 설치
echo ====================================================
echo.

:: Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.10 이상을 먼저 설치해주세요.
    echo 다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [확인] Python 버전:
python --version
echo.

:: wheels 폴더 확인
if not exist "wheels\" (
    echo [오류] wheels 폴더가 없습니다.
    echo 프로젝트 폴더 안에 wheels 폴더가 있어야 합니다.
    pause
    exit /b 1
)

echo [설치 시작] wheels 폴더의 패키지를 설치합니다...
echo.

:: --no-index      : PyPI(인터넷) 사용 안 함
:: --find-links    : 이 폴더에서 패키지 파일 찾기
:: -r requirements : requirements.txt 에 명시된 패키지 설치
pip install --no-index --find-links=./wheels -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [오류] 설치 중 문제가 발생했습니다.
    echo Python 버전이 맞지 않을 수 있습니다. (권장: Python 3.12)
    pause
    exit /b 1
)

echo.
echo ====================================================
echo  설치 완료!
echo  다음 단계: .env 파일을 설정하고 main.py 를 실행하세요.
echo ====================================================
echo.
pause
