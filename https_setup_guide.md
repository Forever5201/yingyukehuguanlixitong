# HTTPS配置指南

## 🎯 推荐方案：Nginx + Let's Encrypt

### 📋 前置条件
- 云服务器（您的117.72.145.165）
- 域名（可选，但推荐）
- 管理员权限

### 🔧 步骤1：安装Nginx

#### Windows Server
```powershell
# 使用Chocolatey安装
choco install nginx

# 或下载安装包
# https://nginx.org/en/download.html
```

#### Linux (Ubuntu/CentOS)
```bash
# Ubuntu
sudo apt update
sudo apt install nginx

# CentOS
sudo yum install nginx
```

### 🔧 步骤2：配置Nginx反向代理

创建配置文件：`C:\nginx\conf\conf.d\customer-management.conf`

```nginx
server {
    listen 80;
    server_name 117.72.145.165;  # 您的服务器IP
    
    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name 117.72.145.165;  # 您的服务器IP
    
    # SSL证书配置（稍后添加）
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;
    
    # 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 反向代理到Flask应用
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location /static/ {
        proxy_pass http://127.0.0.1:5000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 🔧 步骤3：申请Let's Encrypt证书

#### 方法1：使用Certbot（推荐）

```bash
# 安装Certbot
# Windows: 下载 https://certbot.eff.org/
# Linux: sudo apt install certbot

# 申请证书
certbot certonly --standalone -d 117.72.145.165.nip.io

# 或使用域名（如果有）
certbot certonly --standalone -d yourdomain.com
```

#### 方法2：自签名证书（开发测试）

```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 🔧 步骤4：更新Nginx配置

将证书路径添加到Nginx配置：

```nginx
server {
    listen 443 ssl;
    server_name 117.72.145.165;
    
    # SSL证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 其他配置
}
```

### 🔧 步骤5：启动服务

```powershell
# 启动Nginx
nginx

# 启动Flask应用（修改为只监听本地）
python run.py
```

### 🔧 步骤6：修改Flask应用

修改 `run.py` 只监听本地：

```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
```

## 🚀 快速部署脚本

### Windows部署脚本

```powershell
# install_https.ps1
Write-Host "开始配置HTTPS..." -ForegroundColor Green

# 1. 安装Nginx
Write-Host "1. 安装Nginx..." -ForegroundColor Yellow
choco install nginx -y

# 2. 创建配置目录
Write-Host "2. 创建配置..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "C:\nginx\conf\conf.d"

# 3. 复制配置文件
Write-Host "3. 配置Nginx..." -ForegroundColor Yellow
# 这里需要创建配置文件

# 4. 启动服务
Write-Host "4. 启动服务..." -ForegroundColor Yellow
Start-Service nginx

Write-Host "HTTPS配置完成！" -ForegroundColor Green
Write-Host "访问地址: https://117.72.145.165" -ForegroundColor Cyan
```

## 🔒 安全增强

### 1. 防火墙配置
```powershell
# 开放HTTPS端口
netsh advfirewall firewall add rule name="HTTPS" dir=in action=allow protocol=TCP localport=443
```

### 2. 安全头配置
```nginx
# 添加到Nginx配置
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 📊 成本分析

| 项目 | 成本 | 说明 |
|------|------|------|
| Nginx | 免费 | 开源软件 |
| Let's Encrypt证书 | 免费 | 自动续期 |
| 域名 | 可选 | 约50-100元/年 |
| 服务器 | 已有 | 您的云服务器 |

## ⚡ 性能优化

### 1. SSL优化
```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 2. 静态文件缓存
```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🎯 总结

**推荐方案**：Nginx + Let's Encrypt
- **难度**：⭐⭐⭐（中等）
- **时间**：1-2小时
- **成本**：免费
- **安全性**：生产级别

这个方案既保证了安全性，又不会增加太多复杂性和成本。


