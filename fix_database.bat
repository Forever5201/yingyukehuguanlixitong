@echo off
REM 快速修复数据库问题的批处理脚本 (Windows)

echo ======================================
echo 数据库快速修复工具 (Windows)
echo ======================================

REM 检查是否有虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate

REM 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt

REM 运行快速修复
echo 运行数据库修复...
python quick_migrate.py

REM 检查是否成功
if %ERRORLEVEL% NEQ 0 (
    echo 快速修复失败，尝试完整迁移...
    set FLASK_APP=run.py
    
    REM 初始化迁移系统
    if not exist "migrations" (
        flask db init
    )
    
    REM 标记当前数据库状态
    flask db stamp head
    
    REM 生成并应用迁移
    flask db migrate -m "Fix missing columns"
    flask db upgrade
)

echo ======================================
echo 数据库修复完成!
echo ======================================
echo.
echo 请保持虚拟环境激活状态运行应用
echo 运行应用: python run.py
pause