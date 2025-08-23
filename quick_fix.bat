@echo off
echo ============================================================
echo 快速修复脚本
echo ============================================================

echo.
echo [1] 备份当前文件...
if exist config.py copy config.py config.py.backup
if exist app\routes.py copy app\routes.py app\routes.py.backup
if exist app\models.py copy app\models.py app\models.py.backup

echo.
echo [2] 暂存本地修改...
git stash

echo.
echo [3] 拉取最新代码...
git pull

echo.
echo [4] 应用修复...
echo 正在修复 config.py...

(
echo import os
echo import secrets
echo.
echo class Config:
echo     SECRET_KEY = os.environ.get^('SECRET_KEY'^) or secrets.token_hex^(32^)
echo     SQLALCHEMY_DATABASE_URI = os.environ.get^('DATABASE_URL'^) or \
echo         'sqlite:///' + os.path.join^(os.path.abspath^(os.path.dirname^(__file__^)^), 'instance/database.sqlite'^)
echo     SQLALCHEMY_TRACK_MODIFICATIONS = False
echo.    
echo     # Database performance optimization
echo     SQLALCHEMY_ENGINE_OPTIONS = {
echo         'pool_size': 10,
echo         'pool_recycle': 3600,
echo         'pool_pre_ping': True,
echo         'max_overflow': 20,
echo         'pool_timeout': 30
echo     }
echo.    
echo     # Session security configuration
echo     SESSION_COOKIE_SECURE = os.environ.get^('FLASK_ENV'^) == 'production'
echo     SESSION_COOKIE_HTTPONLY = True
echo     SESSION_COOKIE_SAMESITE = 'Lax'
echo.    
echo     # Upload size limit
echo     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
echo.    
echo     # Cache configuration
echo     SEND_FILE_MAX_AGE_DEFAULT = 3600
) > config.py

echo.
echo [5] 创建 .env.template...

(
echo # Flask配置
echo FLASK_ENV=development
echo SECRET_KEY=your-secret-key-here-use-secrets.token_hex^(32^)
echo.
echo # 数据库配置
echo DATABASE_URL=sqlite:///instance/database.sqlite
echo.
echo # 日志级别
echo LOG_LEVEL=INFO
echo.
echo # Redis URL ^(用于缓存和限流^)
echo # REDIS_URL=redis://localhost:6379/0
) > .env.template

echo.
echo ============================================================
echo 修复完成！
echo ============================================================
echo.
echo 现在请运行以下命令：
echo 1. python fix_database_now.py
echo 2. python run.py
echo.
pause