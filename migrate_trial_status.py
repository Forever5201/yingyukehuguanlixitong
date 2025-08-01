#!/usr/bin/env python3
"""
数据库迁移脚本：添加试听课状态字段
"""

import sqlite3
import os

def migrate_trial_status():
    """添加试听课状态相关字段"""
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，跳过迁移")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加 trial_status 字段
        if 'trial_status' not in columns:
            cursor.execute("ALTER TABLE course ADD COLUMN trial_status VARCHAR(20) DEFAULT 'registered'")
            print("✓ 添加 trial_status 字段")
        else:
            print("- trial_status 字段已存在")
        
        # 添加 refund_amount 字段
        if 'refund_amount' not in columns:
            cursor.execute("ALTER TABLE course ADD COLUMN refund_amount FLOAT DEFAULT 0")
            print("✓ 添加 refund_amount 字段")
        else:
            print("- refund_amount 字段已存在")
        
        # 添加 refund_fee 字段
        if 'refund_fee' not in columns:
            cursor.execute("ALTER TABLE course ADD COLUMN refund_fee FLOAT DEFAULT 0")
            print("✓ 添加 refund_fee 字段")
        else:
            print("- refund_fee 字段已存在")
        
        # 更新现有试听课记录的状态
        # 如果已转化为正课，状态设为 'converted'
        cursor.execute("""
            UPDATE course 
            SET trial_status = 'converted' 
            WHERE is_trial = 1 AND converted_to_course IS NOT NULL
        """)
        converted_count = cursor.rowcount
        
        # 其他试听课默认为 'registered'
        cursor.execute("""
            UPDATE course 
            SET trial_status = 'registered' 
            WHERE is_trial = 1 AND trial_status IS NULL
        """)
        registered_count = cursor.rowcount
        
        conn.commit()
        print(f"✓ 更新了 {converted_count} 条已转化试听课状态")
        print(f"✓ 更新了 {registered_count} 条试听课状态为已报名")
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_trial_status()