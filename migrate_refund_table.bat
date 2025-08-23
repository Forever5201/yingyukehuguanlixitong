@echo off
echo === 退费功能数据库迁移 ===
echo.

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 设置Flask应用
set FLASK_APP=run.py

echo 1. 尝试使用 Flask-Migrate...
flask db migrate -m "Add CourseRefund table" 2>nul
if %errorlevel% neq 0 (
    echo Flask-Migrate 迁移失败，使用备选方案...
    echo.
    echo 2. 运行直接初始化脚本...
    python init_refund_table.py
    if %errorlevel% neq 0 (
        echo 初始化脚本也失败了，尝试直接运行应用...
        echo.
        echo 3. 直接运行应用（会自动创建表）...
        python run.py
    )
) else (
    echo 迁移文件生成成功！
    echo.
    echo 应用迁移到数据库...
    flask db upgrade
    echo.
    echo ✅ 迁移完成！
)

echo.
echo 按任意键退出...
pause >nul