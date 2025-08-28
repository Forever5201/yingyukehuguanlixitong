#!/bin/bash
# Linux 服务器更新脚本
# 使用方法：chmod +x server_update.sh && ./server_update.sh

echo "========================================"
echo "     开始更新 Flask 应用"
echo "========================================"

# 1. 进入项目目录
cd /home/ubuntu/customer-management-system || exit 1

# 2. 保存当前更改（如果有）
echo "[1/5] 检查本地更改..."
if [[ -n $(git status -s) ]]; then
    echo "⚠️  发现本地更改，暂存中..."
    git stash
fi

# 3. 拉取最新代码
echo "[2/5] 拉取最新代码..."
git pull origin master

# 4. 恢复本地更改（如果有）
if git stash list | grep -q 'stash@{0}'; then
    echo "恢复本地更改..."
    git stash pop
fi

# 5. 更新依赖
echo "[3/5] 更新依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
fi

# 6. 备份数据库
echo "[4/5] 备份数据库..."
if [ -f "instance/database.sqlite" ]; then
    mkdir -p backups
    cp instance/database.sqlite "backups/database_$(date +%Y%m%d_%H%M%S).sqlite"
    echo "✅ 数据库已备份"
fi

# 7. 重启应用（如果使用 systemd）
echo "[5/5] 重启应用..."
# sudo systemctl restart flask-app  # 如果配置了服务

echo ""
echo "✅ 更新完成！"
echo "运行以下命令启动应用："
echo "python run.py"