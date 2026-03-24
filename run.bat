@echo off
REM le-code Windows 启动脚本

REM 检查 Python 版本
python --version

REM 检查并安装依赖
echo Checking dependencies...
pip install -r requirements.txt -q

REM 检查 API Key
if "%ZHIPUAI_API_KEY%"=="" (
    if exist .env (
        REM 从 .env 文件加载环境变量
        for /f "tokens=*" %%a in (.env) do set %%a
        echo Loaded API Key from .env file
    ) else (
        echo Error: ZHIPUAI_API_KEY not set
        echo Please set it with: set ZHIPUAI_API_KEY=your-api-key
        echo Or create a .env file with: ZHIPUAI_API_KEY=your-api-key
        pause
        exit /b 1
    )
)

REM 启动程序
echo.
echo Starting le-code...
python main.py

pause
