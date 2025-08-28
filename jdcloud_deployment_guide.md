# 京东云 Flask 应用部署指南

## 1. 确认服务器类型

首先确认您的京东云服务器类型：
- **Linux 服务器**：Ubuntu/CentOS
- **Windows Server**

## 2. 京东云文件传输方法

### 方法一：使用京东云控制台的 VNC

1. 登录京东云控制台
2. 找到您的云主机
3. 点击"远程连接" → "VNC连接"
4. 可以通过网页操作服务器

### 方法二：配置安全组（重要！）

在京东云控制台：
1. 进入"云主机"
2. 点击"安全组"
3. 添加入站规则：
   - SSH (22端口) - Linux
   - RDP (3389端口) - Windows
   - Flask (5000端口)

### 方法三：使用京东云 CLI 工具

```bash
# 安装京东云 CLI
pip install jdcloud-cli

# 配置
jdc configure

# 上传文件示例
jdc oss cp local_file oss://bucket/path
```

## 3. 持续部署方案

### 使用 GitHub + Webhook

1. **在服务器上创建更新脚本**
```bash
#!/bin/bash
# update.sh
cd /path/to/your/app
git pull
pip install -r requirements.txt
# 重启服务
sudo systemctl restart flask-app
```

2. **设置 Webhook 自动更新**
- GitHub 仓库 → Settings → Webhooks
- 添加服务器地址
- 每次 push 自动触发更新

### 使用京东云 DevOps

京东云提供 DevOps 服务：
1. 代码托管
2. 自动构建
3. 自动部署

## 4. 数据库同步策略

### 开发和生产分离
```python
# config.py
import os

class Config:
    if os.environ.get('FLASK_ENV') == 'production':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///prod_database.sqlite'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_database.sqlite'
```

### 数据库备份
```bash
# 定时备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp instance/database.sqlite backups/database_$DATE.sqlite
# 保留最近7天
find backups -name "*.sqlite" -mtime +7 -delete
```

## 5. 推荐的目录结构

```
C:\webapp\ (Windows) 或 /home/ubuntu/webapp/ (Linux)
├── customer-management-system/    # 应用代码（Git管理）
│   ├── app/
│   ├── instance/
│   │   └── database.sqlite       # 生产数据库（不进Git）
│   ├── requirements.txt
│   └── run.py
├── backups/                      # 数据库备份
├── logs/                         # 日志文件
└── scripts/                      # 部署脚本
    ├── update.sh
    └── backup.sh
```

## 6. 自动化部署脚本

创建 `deploy.ps1` (Windows) 或 `deploy.sh` (Linux)：

**Windows PowerShell:**
```powershell
# deploy.ps1
param($message="Update")

# 本地操作
Write-Host "1. 提交代码到 Git..." -ForegroundColor Green
git add .
git commit -m $message
git push

# 远程操作
Write-Host "2. 连接服务器更新..." -ForegroundColor Green
ssh user@服务器IP "cd /webapp && git pull && pm2 restart flask-app"

Write-Host "✅ 部署完成!" -ForegroundColor Green
```

**Linux Bash:**
```bash
#!/bin/bash
# deploy.sh
MESSAGE=${1:-"Update"}

echo "1. 提交代码..."
git add .
git commit -m "$MESSAGE"
git push

echo "2. 部署到服务器..."
ssh user@服务器IP << EOF
cd /home/ubuntu/webapp/customer-management-system
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flask-app
EOF

echo "✅ 部署完成!"
```

使用方法：
```bash
# Windows
./deploy.ps1 "添加新功能"

# Linux/Mac
./deploy.sh "添加新功能"
```