#!/usr/bin/env python3
"""
数据库迁移脚本
用于自动检查和更新数据库结构，确保与模型定义一致
"""

import sqlite3
import os
from app import create_app, db
from app.models import TaobaoOrder, Customer, Config

def check_and_migrate_database():
    """检查并迁移数据库结构"""
    app = create_app()
    
    with app.app_context():
        # 检查数据库文件是否存在
        db_path = 'instance/database.sqlite'
        if not os.path.exists(db_path):
            print("数据库文件不存在，创建新数据库...")
            db.create_all()
            print("数据库创建完成！")
            return
        
        # 连接数据库检查表结构
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 检查 taobao_order 表结构
            cursor.execute("PRAGMA table_info(taobao_order)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}
            
            # 需要的字段列表
            required_fields = {
                'id': 'INTEGER',
                'name': 'VARCHAR(100)',
                'level': 'VARCHAR(50)',
                'amount': 'FLOAT',
                'commission': 'FLOAT',
                'taobao_fee': 'FLOAT',  # 新增字段
                'evaluated': 'BOOLEAN',
                'order_time': 'DATETIME',
                'created_at': 'DATETIME',
                'settled': 'BOOLEAN',
                'settled_at': 'DATETIME'
            }
            
            # 检查缺失的字段
            missing_fields = []
            for field, field_type in required_fields.items():
                if field not in columns:
                    missing_fields.append((field, field_type))
            
            # 添加缺失的字段
            if missing_fields:
                print(f"发现缺失字段: {[f[0] for f in missing_fields]}")
                for field, field_type in missing_fields:
                    try:
                        default_value = "DEFAULT 0" if field_type == 'FLOAT' else ""
                        cursor.execute(f"ALTER TABLE taobao_order ADD COLUMN {field} {field_type} {default_value}")
                        print(f"成功添加字段: {field}")
                    except sqlite3.OperationalError as e:
                        if 'duplicate column name' not in str(e):
                            print(f"添加字段 {field} 失败: {e}")
                
                conn.commit()
                print("数据库结构更新完成！")
            else:
                print("数据库结构已是最新版本")
                
        except Exception as e:
            print(f"迁移过程中出现错误: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    check_and_migrate_database()