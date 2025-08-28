# Windows Server 部署 Flask 应用指南

## 1. 安装 Python

1. **下载 Python**
   - 打开浏览器访问：https://www.python.org/downloads/
   - 下载 Python 3.9 或更高版本
   - 安装时勾选 "Add Python to PATH"

2. **验证安装**
   ```powershell
   python --version
   pip --version
   ```

## 2. 安装 Git（可选）

从 https://git-scm.com/download/win 下载并安装

## 3. 部署应用

### 方法一：直接复制文件

1. **在服务器上创建项目文件夹**
   ```powershell
   mkdir C:\webapp
   cd C:\webapp
   ```

2. **使用 Windows 远程桌面复制文件**
   - 在本地电脑：Win+R → mstsc
   - 连接时勾选"本地资源" → "详细信息" → 选择本地磁盘
   - 连接后可以直接复制粘贴文件

### 方法二：使用 PowerShell 下载

如果您的代码在 GitHub：
```powershell
git clone 您的仓库地址
```

## 4. 安装依赖

```powershell
cd C:\webapp\your-project
pip install -r requirements.txt
```

## 5. 配置防火墙

```powershell
# 允许 5000 端口
New-NetFirewallRule -DisplayName "Flask App" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 6. 运行应用

```powershell
# 设置环境变量
$env:FLASK_APP = "run.py"

# 运行（需要修改 app.run() 中的 host）
python run.py
```

## 7. 数据库文件传输

### 最简单的方法：远程桌面复制
1. 连接远程桌面时启用驱动器映射
2. 直接从本地磁盘复制 `database.sqlite` 到服务器

### 或使用 PowerShell：
```powershell
# 在服务器上启动简单 HTTP 服务器
python -m http.server 8080

# 然后从本地上传文件
```

## 8. 持久化运行

使用 NSSM（Non-Sucking Service Manager）将 Flask 注册为 Windows 服务：

1. 下载 NSSM：https://nssm.cc/download
2. 解压到 C:\nssm
3. 注册服务：
   ```powershell
   C:\nssm\win64\nssm.exe install FlaskApp
   # 在弹出窗口中设置：
   # Path: C:\Python39\python.exe
   # Arguments: C:\webapp\your-project\run.py
   ```

## 9. 配置 IIS（可选）

如果需要更专业的部署，可以使用 IIS + wfastcgi