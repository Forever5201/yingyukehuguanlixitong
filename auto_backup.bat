@echo off
REM 自动备份批处理文件
REM 用于Windows任务计划程序定时执行

echo [%date% %time%] 开始自动备份...

REM 切换到项目目录
cd /d "f:\3454353"

REM 执行备份脚本
python auto_backup.py

REM 记录备份结果
if %errorlevel% equ 0 (
    echo [%date% %time%] 自动备份成功完成
) else (
    echo [%date% %time%] 自动备份失败，错误代码: %errorlevel%
)

REM 可选：将日志写入文件
echo [%date% %time%] 备份任务执行完成 >> backup_log.txt