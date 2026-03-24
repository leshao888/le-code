@echo off
chcp 65001 >nul
echo Starting le-code...
echo.
echo ========================================
echo   le-code - AI Assistant
echo   Powered by ZhipuAI GLM-4.7
echo ========================================
echo.
echo Type /help for commands
echo Type /exit to quit
echo.
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Program exited with error code: %ERRORLEVEL%
    echo Please check your API key and internet connection.
)
echo.
echo Press any key to exit...
pause >nul
