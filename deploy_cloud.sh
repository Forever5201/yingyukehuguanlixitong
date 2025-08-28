#!/bin/bash

echo "========================================"
echo "    客户管理系统 - 云端部署脚本"
echo "========================================"
echo

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始云端部署..."
echo

echo "1. 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3未安装或不在PATH中"
    exit 1
fi
echo "✅ Python环境正常"
echo

echo "2. 安装Python依赖包..."
echo "正在安装Flask及相关依赖..."
pip3 install Flask Flask-SQLAlchemy Flask-Migrate pandas openpyxl XlsxWriter
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    echo "尝试使用requirements.txt..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装完全失败"
        exit 1
    fi
fi
echo "✅ 依赖安装成功"
echo

echo "3. 检查数据库..."
if [ ! -d "instance" ]; then
    echo "创建instance目录..."
    mkdir -p instance
fi
echo "✅ 数据库目录检查完成"
echo

echo "4. 启动应用..."
echo "应用将在 http://0.0.0.0:5000 启动"
echo "按 Ctrl+C 停止服务器"
echo
python3 run.py

echo
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 应用已停止"


