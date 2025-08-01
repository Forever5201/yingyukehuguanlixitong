#!/usr/bin/env python3
"""
数据库迁移脚本：为Course表添加新字段
"""

import sqlite3
from datetime import datetime

def migrate_course_table():
    """为Course表添加新字段"""
    
    # 连接数据库
    conn = sqlite3.connect('instance/database.sqlite')
    cursor = conn.cursor()
    
    try:
        # 检查表结构
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前Course表字段: {columns}")
        
        # 需要添加的新字段
        new_columns = [
            ('source', 'VARCHAR(100)'),
            ('course_type', 'VARCHAR(50)'),
            ('converted_from_trial', 'INTEGER'),
            ('converted_to_course', 'INTEGER'),
            ('created_at', 'DATETIME'),
            ('updated_at', 'DATETIME')
        ]
        
        # 添加缺失的字段
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    if column_name in ['created_at', 'updated_at']:
                        # 为时间字段设置默认值
                        default_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute(f"ALTER TABLE course ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'")
                    else:
                        cursor.execute(f"ALTER TABLE course ADD COLUMN {column_name} {column_type}")
                    print(f"✓ 添加字段: {column_name} ({column_type})")
                except sqlite3.Error as e:
                    print(f"✗ 添加字段 {column_name} 失败: {e}")
            else:
                print(f"- 字段 {column_name} 已存在")
        
        # 更新现有记录的时间字段
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE course 
            SET created_at = ?, updated_at = ? 
            WHERE created_at IS NULL OR updated_at IS NULL
        """, (current_time, current_time))
        
        # 提交更改
        conn.commit()
        print("✓ 数据库迁移完成")
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(course)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"更新后Course表字段: {updated_columns}")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_course_table()