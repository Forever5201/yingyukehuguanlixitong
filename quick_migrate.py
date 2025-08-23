#!/usr/bin/env python
"""
快速数据库迁移脚本
用于解决当前的数据库列缺失问题
"""
import os
import sys
from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_column():
    """添加缺失的 custom_trial_cost 列"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查列是否存在
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('course') WHERE name='custom_trial_cost';"
            ))
            count = result.scalar()
            
            if count == 0:
                logger.info("添加缺失的列 custom_trial_cost...")
                db.session.execute(text(
                    "ALTER TABLE course ADD COLUMN custom_trial_cost FLOAT;"
                ))
                db.session.commit()
                logger.info("✅ 列添加成功!")
            else:
                logger.info("列 custom_trial_cost 已存在")
                
        except Exception as e:
            logger.error(f"错误: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    if add_missing_column():
        logger.info("数据库修复完成!")
    else:
        logger.error("数据库修复失败!")
        sys.exit(1)