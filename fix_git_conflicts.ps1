# PowerShell脚本 - 处理Git冲突并应用修复

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Git冲突处理和代码修复脚本" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. 保存当前修改
Write-Host "`n[1] 保存当前修改..." -ForegroundColor Yellow
git stash save "Local changes before pull"

# 2. 移除冲突文件
Write-Host "`n[2] 移除冲突文件..." -ForegroundColor Yellow
if (Test-Path ".env.template") {
    Move-Item -Path ".env.template" -Destination ".env.template.local" -Force
    Write-Host "  - 移动 .env.template 到 .env.template.local" -ForegroundColor Green
}

# 3. 拉取最新代码
Write-Host "`n[3] 拉取最新代码..." -ForegroundColor Yellow
git pull

# 4. 应用安全修复
Write-Host "`n[4] 应用安全修复..." -ForegroundColor Yellow

# 修复 config.py
$configContent = @'
import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库性能优化
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'pool_timeout': 30
    }
    
    # 会话安全配置
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 上传大小限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 缓存配置
    SEND_FILE_MAX_AGE_DEFAULT = 3600
'@

Set-Content -Path "config.py" -Value $configContent -Encoding UTF8
Write-Host "  ✓ config.py 已修复" -ForegroundColor Green

# 5. 创建 .env.template
$envTemplate = @'
# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-use-secrets.token_hex(32)

# 数据库配置
DATABASE_URL=sqlite:///instance/database.sqlite

# 日志级别
LOG_LEVEL=INFO

# Redis URL (用于缓存和限流)
# REDIS_URL=redis://localhost:6379/0
'@

Set-Content -Path ".env.template" -Value $envTemplate -Encoding UTF8
Write-Host "  ✓ .env.template 已创建" -ForegroundColor Green

# 6. 创建 .env 文件
Write-Host "`n[5] 创建 .env 文件..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    $secretKey = [System.Web.Security.Membership]::GeneratePassword(64, 0)
    $envContent = @"
# Flask配置
FLASK_ENV=development
SECRET_KEY=$secretKey

# 数据库配置
DATABASE_URL=sqlite:///instance/database.sqlite

# 日志级别
LOG_LEVEL=INFO
"@
    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
    Write-Host "  ✓ .env 文件已创建" -ForegroundColor Green
} else {
    Write-Host "  - .env 文件已存在" -ForegroundColor Yellow
}

# 7. 更新 .gitignore
Write-Host "`n[6] 更新 .gitignore..." -ForegroundColor Yellow
$gitignoreContent = Get-Content ".gitignore" -Raw -ErrorAction SilentlyContinue
if ($gitignoreContent -notmatch "\.env") {
    Add-Content -Path ".gitignore" -Value "`n# 环境变量`n.env`n.env.local`n"
    Write-Host "  ✓ .gitignore 已更新" -ForegroundColor Green
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "修复完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n后续步骤：" -ForegroundColor Yellow
Write-Host "1. 运行数据库修复: python fix_database_now.py" -ForegroundColor White
Write-Host "2. 启动应用: python run.py" -ForegroundColor White
Write-Host "3. 运行测试: python test_all_fixed.py" -ForegroundColor White