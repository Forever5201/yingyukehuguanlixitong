# PowerShell脚本 - 自动拉取并迁移
# 使用方法：在PowerShell中运行 .\pull_and_migrate.ps1

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "🔄 自动拉取并迁移工具" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# 1. 拉取最新代码
Write-Host "`n[1/2] 正在拉取最新代码..." -ForegroundColor Yellow
$gitOutput = git pull 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Git拉取失败！" -ForegroundColor Red
    Write-Host $gitOutput
    Read-Host "按任意键退出"
    exit 1
}

Write-Host $gitOutput -ForegroundColor Green

# 2. 检查是否有数据库相关更新
$changes = git diff HEAD@{1} --name-only 2>$null
$dbChanged = $false

if ($changes -match "(schema\.sql|models\.py)") {
    $dbChanged = $true
    Write-Host "`n📊 检测到数据库结构变更" -ForegroundColor Yellow
}

# 3. 运行迁移
Write-Host "`n[2/2] 检查并迁移数据库..." -ForegroundColor Yellow

# 检测Python命令
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } 
              elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" }
              else { $null }

if (-not $pythonCmd) {
    Write-Host "[错误] 未找到Python！" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 运行迁移脚本
& $pythonCmd auto_migrate.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[错误] 数据库迁移失败！" -ForegroundColor Red
    Write-Host "请手动运行: $pythonCmd auto_migrate.py" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "`n=======================================" -ForegroundColor Green
Write-Host "✅ 完成！代码已更新，数据库已同步" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# 显示更新摘要
if ($dbChanged) {
    Write-Host "`n📋 数据库更新摘要：" -ForegroundColor Cyan
    Write-Host "- 已自动备份原数据库" -ForegroundColor White
    Write-Host "- 已应用最新表结构" -ForegroundColor White
    Write-Host "- 您的数据完全保留" -ForegroundColor White
}

Read-Host "`n按任意键退出"