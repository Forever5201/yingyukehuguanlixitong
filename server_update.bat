@echo off
REM Windows 服务器更新脚本
REM 使用方法：直接双击或在命令行运行

echo ========================================
echo      开始更新 Flask 应用
echo ========================================

REM 1. 进入项目目录
cd /d C:\webapp\customer-management-system
if %ERRORLEVEL% neq 0 (
    echo [错误] 找不到项目目录！
    pause
    exit /b 1
)

REM 2. 拉取最新代码
echo.
echo [1/4] 拉取最新代码...
git pull origin master
if %ERRORLEVEL% neq 0 (
    echo [错误] 拉取代码失败！
    pause
    exit /b 1
)

REM 3. 更新依赖
echo.
echo [2/4] 更新依赖包...
pip install -r requirements.txt

REM 4. 备份数据库
echo.
echo [3/4] 备份数据库...
if exist "instance\database.sqlite" (
    if not exist "backups" mkdir backups
    copy "instance\database.sqlite" "backups\database_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sqlite" >nul
    echo 数据库已备份
)

REM 5. 完成
echo.
echo [4/4] 更新完成！
echo.
echo 运行以下命令启动应用：
echo python run.py
echo.
pause