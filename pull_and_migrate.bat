@echo off
REM Windows批处理脚本 - 拉取代码并自动迁移数据库
REM 使用方法：双击运行或在命令行中执行

echo ========================================
echo 自动拉取并迁移工具
echo ========================================

REM 拉取最新代码
echo [1/2] 正在拉取最新代码...
git pull

IF %ERRORLEVEL% NEQ 0 (
    echo [错误] Git拉取失败！
    pause
    exit /b 1
)

echo [2/2] 检查并迁移数据库...
python auto_migrate.py

IF %ERRORLEVEL% NEQ 0 (
    echo [错误] 数据库迁移失败！
    echo 请手动运行: python auto_migrate.py
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 完成！代码已更新，数据库已同步
echo ========================================
pause