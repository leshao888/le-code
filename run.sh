#!/bin/bash

# le-code 启动脚本

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# 检查是否安装了依赖
echo "Checking dependencies..."
pip install -r requirements.txt -q

# 检查 API Key
if [ -z "$ZHIPUAI_API_KEY" ]; then
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        echo "Loaded API Key from .env file"
    else
        echo "Error: ZHIPUAI_API_KEY not set"
        echo "Please set it with: export ZHIPUAI_API_KEY=your-api-key"
        echo "Or create a .env file with: ZHIPUAI_API_KEY=your-api-key"
        exit 1
    fi
fi

# 启动程序
echo ""
echo "Starting le-code..."
python main.py
