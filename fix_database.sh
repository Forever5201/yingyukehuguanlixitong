#!/bin/bash
# 快速修复数据库问题的脚本

echo "======================================"
echo "数据库快速修复工具"
echo "======================================"

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 运行快速修复
echo "运行数据库修复..."
python quick_migrate.py

# 如果快速修复失败，尝试完整迁移
if [ $? -ne 0 ]; then
    echo "快速修复失败，尝试完整迁移..."
    export FLASK_APP=run.py
    
    # 初始化迁移系统
    if [ ! -d "migrations" ]; then
        flask db init
    fi
    
    # 标记当前数据库状态
    flask db stamp head
    
    # 生成并应用迁移
    flask db migrate -m "Fix missing columns"
    flask db upgrade
fi

echo "======================================"
echo "✅ 数据库修复完成!"
echo "======================================"
echo ""
echo "提示：在 Windows 上激活虚拟环境："
echo "  venv\\Scripts\\activate"
echo ""
echo "在 Linux/Mac 上激活虚拟环境："
echo "  source venv/bin/activate"