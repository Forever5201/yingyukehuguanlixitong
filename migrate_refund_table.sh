#!/bin/bash

echo "=== 退费功能数据库迁移 ==="
echo

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "警告：未找到虚拟环境"
fi

# 设置Flask应用
export FLASK_APP=run.py

echo "1. 尝试使用 Flask-Migrate..."
if flask db migrate -m "Add CourseRefund table" 2>/dev/null; then
    echo "迁移文件生成成功！"
    echo
    echo "应用迁移到数据库..."
    flask db upgrade
    echo
    echo "✅ 迁移完成！"
else
    echo "Flask-Migrate 迁移失败，使用备选方案..."
    echo
    echo "2. 运行直接初始化脚本..."
    if python3 init_refund_table.py; then
        echo "✅ 初始化成功！"
    else
        echo "初始化脚本也失败了，尝试直接运行应用..."
        echo
        echo "3. 直接运行应用（会自动创建表）..."
        python3 run.py
    fi
fi