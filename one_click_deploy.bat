@echo off
REM 一键部署脚本 - Windows 版本
REM 使用方法：双击运行或命令行运行 one_click_deploy.bat "更新说明"

echo ========================================
echo     Flask 应用一键部署脚本
echo ========================================

REM 获取提交信息
set MESSAGE=%~1
if "%MESSAGE%"=="" set MESSAGE=更新代码

REM 1. 提交本地代码
echo.
echo [1/3] 提交本地代码到 Git...
echo ----------------------------------------
git add .
git commit -m "%MESSAGE%"
git push origin master

REM 2. 检查提交是否成功
if %ERRORLEVEL% neq 0 (
    echo [错误] Git 提交失败！
    pause
    exit /b 1
)

REM 3. 通知用户在服务器上执行更新
echo.
echo [2/3] 代码已推送到 Git 仓库
echo ----------------------------------------
echo.
echo [3/3] 请在服务器上执行以下命令：
echo ========================================
echo cd C:\webapp\customer-management
echo git pull
echo python run.py
echo ========================================
echo.
echo 提示：可以使用 PuTTY 或远程桌面连接服务器
echo.
pause