#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为Course表添加员工分配字段
"""

import sqlite3
import os
from datetime import datetime

def migrate_employee_assignment():
    """为Course表添加assigned_employee_id字段"""
    
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
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_employee_id' in columns:
            print("assigned_employee_id字段已存在，跳过迁移")
            return True
        
        print("开始迁移：为Course表添加assigned_employee_id字段...")
        
        # 添加assigned_employee_id字段
        cursor.execute("""
            ALTER TABLE course 
            ADD COLUMN assigned_employee_id INTEGER 
            REFERENCES employee(id)
        """)
        
        # 提交更改
        conn.commit()
        print("✓ 成功添加assigned_employee_id字段")
        
        # 验证迁移结果
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_employee_id' in columns:
            print("✓ 迁移验证成功")
            return True
        else:
            print("✗ 迁移验证失败")
            return False
            
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("员工分配功能数据库迁移")
    print("=" * 50)
    
    success = migrate_employee_assignment()
    
    if success:
        print("\n✓ 数据库迁移完成！")
    else:
        print("\n✗ 数据库迁移失败！")
    
    print("=" * 50)