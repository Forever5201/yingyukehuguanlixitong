#!/usr/bin/env python
"""
全面修复数据库问题
添加所有缺失的列
"""
import os
import sys
from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_add_column(table_name, column_name, column_type):
    """检查并添加缺失的列"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查列是否存在
            result = db.session.execute(text(
                f"SELECT COUNT(*) FROM pragma_table_info('{table_name}') WHERE name='{column_name}';"
            ))
            count = result.scalar()
            
            if count == 0:
                logger.info(f"添加缺失的列 {table_name}.{column_name}...")
                db.session.execute(text(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
                ))
                db.session.commit()
                logger.info(f"✅ 列 {column_name} 添加成功!")
                return True
            else:
                logger.info(f"列 {table_name}.{column_name} 已存在")
                return False
                
        except Exception as e:
            logger.error(f"错误: {e}")
            db.session.rollback()
            return False

def list_table_columns(table_name):
    """列出表的所有列"""
    app = create_app()
    
    with app.app_context():
        try:
            result = db.session.execute(text(
                f"PRAGMA table_info({table_name});"
            ))
            columns = result.fetchall()
            logger.info(f"\n表 {table_name} 的列：")
            for col in columns:
                logger.info(f"  - {col[1]} ({col[2]})")
        except Exception as e:
            logger.error(f"无法获取表信息: {e}")

def main():
    logger.info("="*60)
    logger.info("数据库全面修复工具")
    logger.info("="*60)
    
    # 列出当前 course 表的所有列
    list_table_columns('course')
    
    # 添加所有可能缺失的列
    columns_to_add = [
        ('course', 'cost', 'FLOAT'),
        ('course', 'custom_trial_cost', 'FLOAT'),
        ('course', 'other_cost', 'FLOAT DEFAULT 0'),
        ('course', 'snapshot_course_cost', 'FLOAT DEFAULT 0'),
        ('course', 'snapshot_fee_rate', 'FLOAT DEFAULT 0'),
        ('course', 'custom_course_cost', 'FLOAT'),
    ]
    
    added_count = 0
    for table, column, col_type in columns_to_add:
        if check_and_add_column(table, column, col_type):
            added_count += 1
    
    # 再次列出列，确认修复
    logger.info("\n修复后的表结构：")
    list_table_columns('course')
    
    if added_count > 0:
        logger.info(f"\n✅ 成功添加了 {added_count} 个列")
    else:
        logger.info("\n✅ 所有列都已存在，无需修复")

if __name__ == "__main__":
    main()