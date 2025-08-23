@echo off
REM 完整安装所有项目依赖

echo ========================================
echo    完整安装项目依赖
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.x
    pause
    exit /b 1
)

echo 正在安装所有依赖...
echo.

REM 使用 requirements.txt 安装所有依赖
echo 安装项目依赖...
pip install -r requirements.txt

REM 单独确保关键依赖已安装
echo.
echo 确保关键依赖...
pip install Flask Flask-SQLAlchemy Flask-Migrate pandas openpyxl XlsxWriter

echo.
echo ========================================
echo    依赖安装完成！
echo ========================================
echo.
echo 已安装的包：
pip list | findstr /i "flask pandas sqlalchemy openpyxl xlsxwriter"
echo.
echo 现在你可以运行 start.bat 启动应用
echo.
pause