#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Flask-Migrate迁移状态
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask_migrate import stamp

def fix_migration_state():
    """将当前数据库状态标记为最新"""
    
    print("=== 修复迁移状态 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        app = create_app()
        
        with app.app_context():
            # 标记当前数据库为最新状态
            stamp()
            print("✓ 已将当前数据库状态标记为最新")
            
            # 验证表存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n当前数据库中的表：")
            for table in sorted(tables):
                print(f"  - {table}")
            
            if 'course_refund' in tables:
                print("\n✅ course_refund 表已存在！")
            else:
                print("\n❌ course_refund 表不存在！")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误：{str(e)}")
        return False

if __name__ == "__main__":
    fix_migration_state()