# 服务器端自动更新脚本 - PowerShell 版本
# 放在服务器上，定时任务或手动执行

$projectPath = "C:\webapp\customer-management"
$logFile = "C:\webapp\logs\update_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -Append $logFile
    Write-Host "$timestamp - $Message" -ForegroundColor Green
}

Write-Log "开始更新应用..."

# 1. 进入项目目录
Set-Location $projectPath

# 2. 拉取最新代码
Write-Log "拉取最新代码..."
$gitOutput = git pull 2>&1
Write-Log "Git输出: $gitOutput"

# 3. 检查是否有更新
if ($gitOutput -match "Already up to date") {
    Write-Log "代码已是最新，无需更新"
    exit 0
}

# 4. 安装/更新依赖
Write-Log "检查依赖..."
pip install -r requirements.txt --quiet

# 5. 备份数据库
$backupDir = "C:\webapp\backups"
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}

$dbFile = "$projectPath\instance\database.sqlite"
if (Test-Path $dbFile) {
    $backupFile = "$backupDir\database_$(Get-Date -Format 'yyyyMMdd_HHmmss').sqlite"
    Copy-Item $dbFile $backupFile
    Write-Log "数据库已备份到: $backupFile"
}

# 6. 重启应用（如果使用了服务）
# Stop-Service -Name "FlaskApp" -ErrorAction SilentlyContinue
# Start-Service -Name "FlaskApp"

Write-Log "更新完成！"

# 7. 清理旧备份（保留最近7个）
Get-ChildItem $backupDir -Filter "*.sqlite" | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 7 | 
    Remove-Item -Force