@echo off
REM 客户管理系统一键启动脚本
REM 自动检查依赖、启动服务器

echo ========================================
echo    客户管理系统 - 一键启动
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

echo [%time%] 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境，请先安装Python 3.x
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [%time%] ✅ Python环境检查通过
echo.

echo [%time%] 正在检查项目依赖...
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [%time%] 📦 正在安装项目依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败，请检查网络连接或手动执行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [%time%] ✅ 依赖安装完成
else
    echo [%time%] ✅ 项目依赖检查通过
endif
echo.

echo [%time%] 🚀 正在启动客户管理系统...
echo.
echo 📋 系统信息：
echo    - 访问地址：http://localhost:5000
echo    - 按 Ctrl+C 可停止服务器
echo    - 数据库文件：instance/database.sqlite
echo.
echo ========================================
echo.

REM 启动Flask应用
python run.py

echo.
echo [%time%] 服务器已停止
pause