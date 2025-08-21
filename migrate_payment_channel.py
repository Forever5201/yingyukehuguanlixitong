#!/usr/bin/env python3
"""
数据库迁移脚本：为Course表添加payment_channel字段
"""

import sqlite3
import os

def migrate_database():
    """为Course表添加payment_channel字段"""
    db_path = 'instance/database.sqlite'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'payment_channel' not in columns:
            # 添加payment_channel字段
            cursor.execute("""
                ALTER TABLE course 
                ADD COLUMN payment_channel VARCHAR(20) DEFAULT '微信'
            """)
            
            print("✅ 成功添加 payment_channel 字段到 course 表")
        else:
            print("ℹ️  payment_channel 字段已存在")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

if __name__ == '__main__':
    print("开始数据库迁移...")
    success = migrate_database()
    if success:
        print("✅ 数据库迁移完成")
    else:
        print("❌ 数据库迁移失败")