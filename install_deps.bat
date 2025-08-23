@echo off
REM 安装所有项目依赖

echo ========================================
echo    安装项目依赖
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.x
    pause
    exit /b 1
)

echo 正在安装依赖...
echo.

REM 升级 pip
echo [1/5] 升级 pip...
python -m pip install --upgrade pip

REM 安装 Flask
echo [2/5] 安装 Flask...
pip install Flask

REM 安装 SQLAlchemy
echo [3/5] 安装 SQLAlchemy...
pip install SQLAlchemy

REM 安装 Flask-SQLAlchemy
echo [4/5] 安装 Flask-SQLAlchemy...
pip install Flask-SQLAlchemy

REM 安装 Flask-Migrate
echo [5/5] 安装 Flask-Migrate...
pip install Flask-Migrate

echo.
echo ========================================
echo    依赖安装完成！
echo ========================================
echo.
echo 现在你可以运行 start.bat 启动应用
echo.
pause