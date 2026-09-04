@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" goto NO_SETUP
if not exist ".env" goto NO_ENV

echo.
echo ============================================================
echo   제조AX서비스1팀 AI 챌린지
echo ============================================================
echo.
echo   주소 : http://localhost:8021
echo.
echo   잠시 후 브라우저가 자동으로 열립니다.
echo   서버를 끄려면 이 창에서 Ctrl + C 를 누르세요.
echo   (이 창을 닫아도 서버가 꺼집니다)
echo.
echo ============================================================
echo.

start "" /min cmd /c "timeout /t 5 > nul && start http://localhost:8021"
".venv\Scripts\python.exe" run.py

echo.
echo 서버가 종료되었습니다.
pause
exit /b 0


:NO_SETUP
echo.
echo   [안내] 아직 설치가 끝나지 않았습니다.
echo          setup.bat 을 먼저 더블클릭해주세요.
echo.
pause
exit /b 1

:NO_ENV
echo.
echo   [안내] .env 파일이 없습니다.
echo          setup.bat 을 먼저 더블클릭해주세요.
echo.
pause
exit /b 1
