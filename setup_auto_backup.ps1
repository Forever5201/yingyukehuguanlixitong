# 设置自动备份任务计划程序脚本
# 需要以管理员权限运行

param(
    [string]$BackupTime = "02:00",  # 默认凌晨2点备份
    [string]$Frequency = "Daily"    # 默认每天备份
)

Write-Host "🔧 正在设置自动备份任务..." -ForegroundColor Green

# 任务基本信息
$TaskName = "DatabaseAutoBackup"
$TaskDescription = "客户管理系统数据库自动备份"
$ScriptPath = Join-Path $PSScriptRoot "auto_backup.bat"

try {
    # 检查是否已存在同名任务
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "⚠️  发现已存在的备份任务，正在删除..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # 创建任务触发器（每天指定时间）
    $Trigger = New-ScheduledTaskTrigger -Daily -At $BackupTime

    # 创建任务动作
    $Action = New-ScheduledTaskAction -Execute $ScriptPath

    # 创建任务设置
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # 创建任务主体（使用当前用户）
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    # 注册任务
    Register-ScheduledTask -TaskName $TaskName -Description $TaskDescription -Trigger $Trigger -Action $Action -Settings $Settings -Principal $Principal

    Write-Host "✅ 自动备份任务设置成功！" -ForegroundColor Green
    Write-Host "📅 备份时间: 每天 $BackupTime" -ForegroundColor Cyan
    Write-Host "📁 备份位置: $PSScriptRoot\backups\" -ForegroundColor Cyan
    Write-Host "🔍 可在'任务计划程序'中查看和管理任务" -ForegroundColor Cyan

    # 显示任务信息
    $Task = Get-ScheduledTask -TaskName $TaskName
    Write-Host "`n📋 任务详情:" -ForegroundColor Yellow
    Write-Host "   任务名称: $($Task.TaskName)"
    Write-Host "   状态: $($Task.State)"
    Write-Host "   下次运行: $((Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo).NextRunTime)"

} catch {
    Write-Host "❌ 设置自动备份任务失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 请确保以管理员权限运行此脚本" -ForegroundColor Yellow
}

Write-Host "`n🎯 使用说明:" -ForegroundColor Magenta
Write-Host "1. 任务将在每天 $BackupTime 自动执行备份"
Write-Host "2. 备份文件保存在 backups\ 目录"
Write-Host "3. 可通过 '任务计划程序' 修改备份时间"
Write-Host "4. 手动测试: 右键任务 -> '运行'"