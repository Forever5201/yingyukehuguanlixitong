#!/bin/bash
# 设置数据库迁移系统

echo "设置数据库迁移系统..."

# 1. 安装依赖
echo "安装 Flask-Migrate..."
pip install Flask-Migrate

# 2. 设置环境变量
export FLASK_APP=run.py

# 3. 初始化迁移
if [ ! -d "migrations" ]; then
    echo "初始化迁移系统..."
    flask db init
else
    echo "迁移系统已初始化"
fi

# 4. 如果有现有数据库，标记当前状态
if [ -f "instance/database.sqlite" ]; then
    echo "检测到现有数据库，标记当前状态..."
    flask db stamp head
fi

# 5. 生成初始迁移
echo "生成迁移文件..."
flask db migrate -m "Initial migration"

# 6. 应用迁移
echo "应用迁移..."
flask db upgrade

echo "✅ 迁移系统设置完成!"