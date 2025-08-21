# 客户管理系统一键启动脚本 (PowerShell版本)
# 提供更好的用户体验和错误处理

param(
    [switch]$Debug = $false,  # 是否启用调试模式
    [int]$Port = 5000         # 服务器端口
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    客户管理系统 - 一键启动" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

try {
    # 检查Python环境
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 正在检查Python环境..." -ForegroundColor Yellow
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 错误：未找到Python环境，请先安装Python 3.x" -ForegroundColor Red
        Write-Host "下载地址：https://www.python.org/downloads/" -ForegroundColor Blue
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
    Write-Host ""

    # 检查项目依赖
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 正在检查项目依赖..." -ForegroundColor Yellow
    $flaskCheck = pip show Flask 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 📦 正在安装项目依赖..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 依赖安装失败，请检查网络连接或手动执行：pip install -r requirements.txt" -ForegroundColor Red
            Read-Host "按回车键退出"
            exit 1
        }
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✅ 依赖安装完成" -ForegroundColor Green
    } else {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✅ 项目依赖检查通过" -ForegroundColor Green
    }
    Write-Host ""

    # 检查数据库目录
    if (!(Test-Path "instance")) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 📁 创建数据库目录..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path "instance" -Force | Out-Null
    }

    # 显示启动信息
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 🚀 正在启动客户管理系统..." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 系统信息：" -ForegroundColor Cyan
    Write-Host "    - 访问地址：http://localhost:$Port" -ForegroundColor White
    Write-Host "    - 按 Ctrl+C 可停止服务器" -ForegroundColor White
    Write-Host "    - 数据库文件：instance/database.sqlite" -ForegroundColor White
    if ($Debug) {
        Write-Host "    - 调试模式：已启用" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # 设置环境变量
    if ($Debug) {
        $env:FLASK_DEBUG = "1"
    }
    $env:FLASK_RUN_PORT = $Port.ToString()

    # 启动Flask应用
    python run.py

} catch {
    Write-Host "❌ 启动过程中发生错误：$($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
} finally {
    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 服务器已停止" -ForegroundColor Yellow
    Read-Host "按回车键退出"
}