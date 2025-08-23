@echo off
echo ============================================================
echo Windows 运行脚本
echo ============================================================

:menu
echo.
echo 请选择要执行的操作：
echo 1. 创建 .env 文件
echo 2. 检查代码质量
echo 3. 修复数据库
echo 4. 运行应用
echo 5. 运行测试
echo 6. 替换 config.py（如果有语法错误）
echo 7. 退出
echo.
set /p choice=请输入选项 (1-7): 

if "%choice%"=="1" goto create_env
if "%choice%"=="2" goto check_quality
if "%choice%"=="3" goto fix_db
if "%choice%"=="4" goto run_app
if "%choice%"=="5" goto run_tests
if "%choice%"=="6" goto fix_config
if "%choice%"=="7" goto end

echo 无效选项，请重试
goto menu

:create_env
echo.
echo 创建 .env 文件...
python create_env.py
if errorlevel 1 (
    echo 执行失败，尝试使用 python3...
    python3 create_env.py
)
pause
goto menu

:check_quality
echo.
echo 检查代码质量...
python code_quality_check.py
if errorlevel 1 (
    echo 执行失败，尝试使用 python3...
    python3 code_quality_check.py
)
pause
goto menu

:fix_db
echo.
echo 修复数据库...
python fix_database_now.py
if errorlevel 1 (
    echo 执行失败，尝试使用 python3...
    python3 fix_database_now.py
)
pause
goto menu

:run_app
echo.
echo 启动应用...
python run.py
if errorlevel 1 (
    echo 执行失败，尝试使用 python3...
    python3 run.py
)
pause
goto menu

:run_tests
echo.
echo 运行测试...
python test_all_fixed.py
if errorlevel 1 (
    echo 执行失败，尝试使用 python3...
    python3 test_all_fixed.py
)
pause
goto menu

:fix_config
echo.
echo 替换 config.py...
copy /Y config_backup.py config.py
echo config.py 已更新
pause
goto menu

:end
echo 退出脚本
exit /b