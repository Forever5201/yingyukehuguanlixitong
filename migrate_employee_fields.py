#!/usr/bin/env python3
"""
数据库迁移脚本：为Employee表添加phone和email字段
"""

import sqlite3
import os

def migrate_employee_fields():
    """为Employee表添加phone和email字段"""
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在，请先运行程序创建数据库")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(employee)")
        columns = [column[1] for column in cursor.fetchall()]
        
        added_columns = []
        
        # 添加phone字段
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE employee ADD COLUMN phone VARCHAR(20)")
            added_columns.append('phone')
            print("✓ 已添加字段: employee.phone")
        
        # 添加email字段
        if 'email' not in columns:
            cursor.execute("ALTER TABLE employee ADD COLUMN email VARCHAR(100)")
            added_columns.append('email')
            print("✓ 已添加字段: employee.email")
        
        if not added_columns:
            print("✓ Employee表结构已是最新")
        
        # 提交更改
        conn.commit()
        print("\n✅ 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始迁移Employee表字段...")
    migrate_employee_fields()

