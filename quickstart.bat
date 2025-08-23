@echo off
REM 快速启动脚本 - 确保所有依赖已安装

echo ========================================
echo    客户管理系统 - 快速启动
echo ========================================
echo.

echo [%time%] 安装/更新所有依赖...
pip install Flask Flask-SQLAlchemy Flask-Migrate

echo.
echo [%time%] 启动应用...
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.

python run.py

pause