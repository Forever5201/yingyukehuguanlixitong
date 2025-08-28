@echo off
chcp 65001 >nul
echo ========================================
echo    客户管理系统 - 云端部署脚本
echo ========================================
echo.

echo [%date% %time%] 开始云端部署...
echo.

echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo 2. 安装Python依赖包...
echo 正在安装Flask及相关依赖...
pip install Flask Flask-SQLAlchemy Flask-Migrate pandas openpyxl XlsxWriter
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    echo 尝试使用requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装完全失败
        pause
        exit /b 1
    )
)
echo ✅ 依赖安装成功
echo.

echo 3. 检查数据库...
if not exist "instance" (
    echo 创建instance目录...
    mkdir instance
)
echo ✅ 数据库目录检查完成
echo.

echo 4. 启动应用...
echo 应用将在 http://0.0.0.0:5000 启动
echo 按 Ctrl+C 停止服务器
echo.
python run.py

echo.
echo [%date% %time%] 应用已停止
pause


