#!/usr/bin/env python
"""
数据库迁移辅助脚本
用于自动初始化、生成和应用数据库迁移
"""
import os
import sys
import subprocess
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate as _migrate, upgrade, stamp
from app import create_app, db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd):
    """执行命令并返回结果"""
    logger.info(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e}")
        if e.stderr:
            logger.error(f"错误输出: {e.stderr}")
        return False

def is_migration_initialized():
    """检查迁移是否已初始化"""
    migrations_dir = Path("migrations")
    return migrations_dir.exists() and migrations_dir.is_dir()

def is_database_empty():
    """检查数据库是否为空（没有 alembic_version 表）"""
    app = create_app()
    with app.app_context():
        try:
            # 使用新的 SQLAlchemy 语法
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';"))
            return result.fetchone() is None
        except:
            return True

def has_pending_migrations():
    """检查是否有待应用的迁移"""
    if not is_migration_initialized():
        return False
    
    # 使用 flask db show 命令检查当前版本
    result = subprocess.run("flask db show", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return True  # 如果命令失败，假设有待应用的迁移
    
    # 检查是否有新的模型更改
    result = subprocess.run("flask db check", shell=True, capture_output=True, text=True)
    return result.returncode != 0

def auto_migrate():
    """自动执行数据库迁移"""
    logger.info("开始自动数据库迁移...")
    
    app = create_app()
    
    # 1. 检查并初始化迁移
    if not is_migration_initialized():
        logger.info("初始化数据库迁移...")
        with app.app_context():
            init()
        logger.info("迁移初始化完成")
    
    # 2. 如果数据库存在但没有迁移历史，标记当前状态
    with app.app_context():
        if is_database_empty():
            logger.info("检测到现有数据库但没有迁移历史，标记当前状态...")
            stamp()
            logger.info("数据库状态标记完成")
    
    # 3. 检查模型更改并生成迁移
    logger.info("检查数据库模型更改...")
    result = subprocess.run("flask db check", shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.info("检测到模型更改，生成新的迁移...")
        # 生成迁移
        migrate_result = subprocess.run(
            'flask db migrate -m "Auto migration"', 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if migrate_result.returncode == 0:
            logger.info("迁移文件生成成功")
        else:
            logger.error(f"迁移文件生成失败: {migrate_result.stderr}")
            return False
    else:
        logger.info("没有检测到模型更改")
    
    # 4. 应用所有待处理的迁移
    logger.info("应用数据库迁移...")
    with app.app_context():
        upgrade()
    logger.info("数据库迁移完成")
    
    return True

def main():
    """主函数"""
    logger.info("="*60)
    logger.info("数据库自动迁移工具")
    logger.info("="*60)
    
    try:
        # 设置 Flask 应用环境变量
        os.environ['FLASK_APP'] = 'run.py'
        
        # 执行自动迁移
        if auto_migrate():
            logger.info("✅ 数据库迁移成功完成!")
            return 0
        else:
            logger.error("❌ 数据库迁移失败!")
            return 1
            
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())