@echo off
REM le-code Windows 启动脚本

REM 检查 Python 版本
python --version
echo.

REM 检查并安装依赖
echo Checking dependencies...
pip install -r requirements.txt -q
echo.

REM 检查配置文件
if not exist "config\config.json" (
    echo [WARNING] config\config.json not found!
    echo Please copy config\config.example.json to config\config.json and fill in your API key
    echo.
    if exist "config\config.example.json" (
        copy config\config.example.json config\config.json
        echo [INFO] Created config\config.json from example
        echo Please edit config\config.json and fill in your API key
        pause
        exit /b 1
    )
)

REM 检查 API Key (支持环境变量 MINIMAX_API_KEY)
if "%MINIMAX_API_KEY%"=="" (
    echo [INFO] MINIMAX_API_KEY not set, checking config.json...
)

REM 启动程序
echo.
echo Starting le-code...
python main.py

pause
