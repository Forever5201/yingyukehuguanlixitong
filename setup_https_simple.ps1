# 简化HTTPS配置脚本
param(
    [string]$ServerIP = "117.72.145.165",
    [string]$FlaskPort = "5000"
)

Write-Host "HTTPS配置脚本开始..." -ForegroundColor Green

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "请以管理员身份运行此脚本！" -ForegroundColor Red
    exit 1
}

Write-Host "管理员权限检查通过" -ForegroundColor Green

# 安装Nginx
Write-Host "正在安装Nginx..." -ForegroundColor Yellow
try {
    choco install nginx -y --force
    Write-Host "Nginx安装成功" -ForegroundColor Green
} catch {
    Write-Host "Nginx安装失败，请手动安装" -ForegroundColor Red
    exit 1
}

# 创建配置目录
$nginxConfDir = "C:\nginx\conf\conf.d"
New-Item -ItemType Directory -Force -Path $nginxConfDir | Out-Null

# 创建SSL目录
$certDir = "C:\nginx\ssl"
New-Item -ItemType Directory -Force -Path $certDir | Out-Null

# 生成自签名证书
$certPath = "$certDir\cert.pem"
$keyPath = "$certDir\key.pem"

if (!(Test-Path $certPath)) {
    Write-Host "正在生成SSL证书..." -ForegroundColor Yellow
    openssl req -x509 -newkey rsa:4096 -keyout $keyPath -out $certPath -days 365 -nodes -subj "/CN=$ServerIP"
    Write-Host "SSL证书生成成功" -ForegroundColor Green
}

# 创建Nginx配置
$configFile = "$nginxConfDir\customer-management.conf"
$configContent = @"
server {
    listen 80;
    server_name $ServerIP;
    return 301 https://`$server_name`$request_uri;
}

server {
    listen 443 ssl;
    server_name $ServerIP;
    
    ssl_certificate $certPath;
    ssl_certificate_key $keyPath;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    location / {
        proxy_pass http://127.0.0.1:$FlaskPort;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}
"@

$configContent | Out-File -FilePath $configFile -Encoding UTF8
Write-Host "Nginx配置文件创建成功" -ForegroundColor Green

# 配置防火墙
netsh advfirewall firewall add rule name="HTTPS" dir=in action=allow protocol=TCP localport=443
netsh advfirewall firewall add rule name="HTTP" dir=in action=allow protocol=TCP localport=80
Write-Host "防火墙配置完成" -ForegroundColor Green

# 启动Nginx
Get-Process -Name "nginx" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Process -FilePath "nginx" -NoNewWindow
Write-Host "Nginx启动成功" -ForegroundColor Green

Write-Host ""
Write-Host "HTTPS配置完成！" -ForegroundColor Green
Write-Host "访问地址: https://$ServerIP" -ForegroundColor Cyan
Write-Host "注意: 使用自签名证书，浏览器会显示安全警告" -ForegroundColor Yellow


