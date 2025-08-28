# 配置 SSH 免密登录（可选）

## Windows 本地配置 SSH

### 1. 生成 SSH 密钥
```powershell
# 在 PowerShell 中
ssh-keygen -t rsa -b 4096
# 一路回车（不设置密码）
```

### 2. 查看公钥
```powershell
type C:\Users\您的用户名\.ssh\id_rsa.pub
```

### 3. 添加到服务器

#### Linux 服务器：
```bash
# 在服务器上
mkdir -p ~/.ssh
echo "您的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### Windows 服务器：
```powershell
# 比较复杂，建议使用密码登录
```

### 4. 测试连接
```powershell
ssh ubuntu@服务器IP
# 应该无需密码直接登录
```

## 配置后的一键部署脚本

创建 `full_deploy.bat`：
```batch
@echo off
REM 完整的一键部署（需要配置 SSH）

echo [1/2] 提交代码...
git add .
git commit -m "%~1"
git push

echo [2/2] 远程更新...
ssh ubuntu@服务器IP "cd /path/to/project && git pull && python run.py"

echo 部署完成！
pause
```