@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   제조AX서비스1팀 AI 챌린지 - 개발 환경 설치
echo ============================================================
echo.
echo 처음 한 번만 실행하면 됩니다. 3~5분 걸립니다.
echo.

REM ---------------------------------------------------------- 1
echo [1/5] 파이썬 확인 중...
python --version > nul 2>&1
if errorlevel 1 goto NO_PYTHON
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo       파이썬 !PYVER! 확인
echo.

REM ---------------------------------------------------------- 2
echo [2/5] Node.js 확인 중...
node --version > nul 2>&1
if errorlevel 1 goto NO_NODE
for /f %%v in ('node --version') do set NODEVER=%%v
echo       Node.js !NODEVER! 확인
echo.

REM ---------------------------------------------------------- 3
echo [3/5] 파이썬 패키지 설치 중... (2~3분, 화면이 멈춘 것처럼 보여도 기다려주세요)
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto FAIL_VENV
)
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 goto FAIL_PIP
echo       완료
echo.

REM ---------------------------------------------------------- 4
echo [4/5] 접속 정보 파일(.env) 준비 중...
if exist ".env" (
    echo       .env 파일이 이미 있습니다. 그대로 둡니다.
) else (
    copy ".env.example" ".env" > nul
    if errorlevel 1 goto FAIL_ENV
    echo       .env 파일을 만들었습니다.
)
echo.

REM ---------------------------------------------------------- 5
echo [5/5] 화면 패키지 설치 중... (1~2분)
cd frontend
call npm install --silent
if errorlevel 1 goto FAIL_NPM
cd ..
echo       완료
echo.

echo ============================================================
echo   설치가 끝났습니다
echo ============================================================
echo.
echo 이제 두 가지만 하시면 됩니다.
echo.
echo   1. 아무 키나 누르면 .env 파일이 메모장으로 열립니다.
echo      아래 세 줄에 값을 채우고 저장(Ctrl+S)한 뒤 창을 닫으세요.
echo.
echo         LLM_BASE_URL=
echo         LLM_API_KEY=
echo         LLM_MODEL=
echo.
echo      값은 리드에게 받으시면 됩니다.
echo.
echo   2. cmd 창을 두 개 열고 아래를 하나씩 실행하세요.
echo.
echo         .venv\Scripts\python.exe run.py
echo.
echo         cd frontend
echo         npm run dev
echo.
echo      그다음 브라우저에서 http://localhost:5173 을 여세요.
echo.
pause
start "" notepad .env
echo.
echo 준비가 끝났습니다. run.py 와 npm run dev 로 화면을 띄우세요.
echo.
pause
exit /b 0


REM ================= 오류 안내 =================

:NO_PYTHON
echo.
echo   [실패] 파이썬을 찾을 수 없습니다.
echo.
echo   해결 방법
echo     1. https://www.python.org/downloads/ 에서 3.11 이상을 받아 설치하세요.
echo     2. 설치 첫 화면 맨 아래 "Add python.exe to PATH" 를 반드시 체크하세요.
echo        (이걸 빠뜨리는 경우가 가장 많습니다)
echo     3. 설치가 끝나면 이 창을 닫고 setup.bat 을 다시 실행하세요.
echo.
goto FAIL

:NO_NODE
echo.
echo   [실패] Node.js 를 찾을 수 없습니다.
echo.
echo   해결 방법
echo     1. https://nodejs.org/ 에서 LTS 버전을 받아 설치하세요.
echo     2. 설치가 끝나면 이 창을 닫고 setup.bat 을 다시 실행하세요.
echo.
goto FAIL

:FAIL_VENV
echo.
echo   [실패] 가상환경(.venv)을 만들지 못했습니다.
echo.
echo   해결 방법
echo     - 이 폴더가 OneDrive 나 바탕화면 안에 있다면 C:\work 같은 짧은 경로로 옮겨보세요.
echo     - 폴더 경로에 한글이나 공백이 많으면 문제가 생길 수 있습니다.
echo     - 그래도 안 되면 .venv 폴더를 지우고 다시 실행해보세요.
echo.
goto FAIL

:FAIL_PIP
echo.
echo   [실패] 파이썬 패키지 설치에 실패했습니다.
echo.
echo   해결 방법
echo     - 인터넷 연결을 확인하세요.
echo     - 위에 빨간 글씨로 나온 오류 메시지를 그대로 캡처해 리드에게 보내주세요.
echo.
goto FAIL

:FAIL_ENV
echo.
echo   [실패] .env 파일을 만들지 못했습니다.
echo.
echo   해결 방법
echo     - .env.example 파일이 이 폴더에 있는지 확인하세요.
echo     - 저장소를 제대로 클론했는지 확인하세요.
echo.
goto FAIL

:FAIL_NPM
cd /d "%~dp0"
echo.
echo   [실패] 화면 패키지 설치에 실패했습니다.
echo.
echo   해결 방법
echo     - 인터넷 연결을 확인하세요.
echo     - frontend\node_modules 폴더를 지우고 setup.bat 을 다시 실행해보세요.
echo     - 위에 나온 오류 메시지를 그대로 캡처해 리드에게 보내주세요.
echo.
goto FAIL

:FAIL
echo ============================================================
echo   설치를 끝내지 못했습니다. 위 안내를 따라주세요.
echo ============================================================
echo.
pause
exit /b 1
