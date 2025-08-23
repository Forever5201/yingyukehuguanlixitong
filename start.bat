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

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [%time%] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [%time%] 未检测到虚拟环境，使用系统Python环境
)

echo [%time%] 正在检查项目依赖...

REM 检查所有必要的包
set MISSING_DEPS=0

pip show Flask >nul 2>&1
if %errorlevel% neq 0 set MISSING_DEPS=1

pip show Flask-SQLAlchemy >nul 2>&1
if %errorlevel% neq 0 set MISSING_DEPS=1

pip show Flask-Migrate >nul 2>&1
if %errorlevel% neq 0 set MISSING_DEPS=1

if %MISSING_DEPS% equ 1 (
    echo [%time%] 📦 正在安装项目依赖...
    pip install Flask Flask-SQLAlchemy Flask-Migrate
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败，尝试使用requirements.txt...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo ❌ 依赖安装失败，请检查网络连接
            echo.
            echo 请手动执行以下命令：
            echo   pip install Flask Flask-SQLAlchemy Flask-Migrate
            echo 或
            echo   pip install -r requirements.txt
            pause
            exit /b 1
        )
    )
    echo [%time%] ✅ 依赖安装完成
else
    echo [%time%] ✅ 项目依赖检查通过
)

echo.

REM 检查数据库迁移
echo [%time%] 检查数据库状态...
if not exist "instance\database.sqlite" (
    echo [%time%] 数据库不存在，正在初始化...
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
    echo [%time%] ✅ 数据库初始化完成
) else (
    REM 尝试修复可能的数据库问题
    if exist "quick_migrate.py" (
        echo [%time%] 运行数据库检查...
        python quick_migrate.py >nul 2>&1
    )
)

echo.
echo [%time%] 🚀 正在启动客户管理系统...
echo.
echo 📋 系统信息：
echo    - 访问地址：http://localhost:5000
echo    - 按 Ctrl+C 可停止服务器
echo    - 数据库文件：instance\database.sqlite
echo.
echo ========================================
echo.

REM 启动Flask应用
python run.py

echo.
echo [%time%] 服务器已停止
pause