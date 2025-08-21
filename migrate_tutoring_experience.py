#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为Customer表添加has_tutoring_experience字段
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """为Customer表添加has_tutoring_experience字段"""
    
    # 数据库文件路径
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'has_tutoring_experience' in columns:
            print("字段 has_tutoring_experience 已存在，无需迁移")
            return True
        
        # 添加新字段
        print("正在添加 has_tutoring_experience 字段...")
        cursor.execute("""
            ALTER TABLE customer 
            ADD COLUMN has_tutoring_experience VARCHAR(10)
        """)
        
        # 提交更改
        conn.commit()
        print("✅ 成功添加 has_tutoring_experience 字段")
        
        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'has_tutoring_experience' in columns:
            print("✅ 字段验证成功")
            return True
        else:
            print("❌ 字段验证失败")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def backup_database():
    """备份数据库"""
    db_path = os.path.join('instance', 'database.sqlite')
    if os.path.exists(db_path):
        backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
        backup_dir = 'backups'
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backup_full_path = os.path.join(backup_dir, backup_path)
        
        import shutil
        shutil.copy2(db_path, backup_full_path)
        print(f"✅ 数据库已备份到: {backup_full_path}")
        return True
    return False

if __name__ == '__main__':
    print("开始数据库迁移...")
    print("=" * 50)
    
    # 备份数据库
    print("1. 备份数据库...")
    backup_database()
    
    # 执行迁移
    print("\n2. 执行迁移...")
    success = migrate_database()
    
    if success:
        print("\n🎉 数据库迁移完成！")
    else:
        print("\n❌ 数据库迁移失败！")
    
    print("=" * 50)