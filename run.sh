#!/bin/bash

# le-code 启动脚本

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# 检查是否安装了依赖
echo "Checking dependencies..."
pip install -r requirements.txt -q
echo ""

# 检查配置文件
if [ ! -f "config/config.json" ]; then
    echo "[WARNING] config/config.json not found!"
    echo "Please copy config/config.example.json to config/config.json and fill in your API key"
    echo ""
    if [ -f "config/config.example.json" ]; then
        cp config/config.example.json config/config.json
        echo "[INFO] Created config/config.json from example"
        echo "Please edit config/config.json and fill in your API key"
        exit 1
    fi
fi

# 启动程序
echo ""
echo "Starting le-code..."
python main.py
