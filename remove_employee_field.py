#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除Course表中的assigned_employee_id字段
"""

import sqlite3
import os
import sys

def remove_employee_field():
    """删除Course表中的assigned_employee_id字段"""
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_employee_id' not in columns:
            print("assigned_employee_id字段不存在，无需删除")
            return True
        
        print("开始删除assigned_employee_id字段...")
        
        # SQLite不支持直接删除列，需要重建表
        # 1. 创建新表（不包含assigned_employee_id字段）
        cursor.execute('''
            CREATE TABLE course_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                customer_id INTEGER NOT NULL,
                is_trial BOOLEAN DEFAULT 0,
                trial_price FLOAT,
                source VARCHAR(50),
                trial_status VARCHAR(20) DEFAULT 'registered',
                refund_amount FLOAT DEFAULT 0,
                refund_fee FLOAT DEFAULT 0,
                course_type VARCHAR(50),
                sessions INTEGER,
                price FLOAT,
                cost FLOAT,
                gift_sessions INTEGER DEFAULT 0,
                other_cost FLOAT DEFAULT 0,
                payment_channel VARCHAR(50),
                converted_from_trial INTEGER,
                converted_to_course INTEGER,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (customer_id) REFERENCES customer (id),
                FOREIGN KEY (converted_from_trial) REFERENCES course (id),
                FOREIGN KEY (converted_to_course) REFERENCES course (id)
            )
        ''')
        
        # 2. 复制数据（排除assigned_employee_id字段）
        cursor.execute('''
            INSERT INTO course_new (
                id, name, customer_id, is_trial, trial_price, source, trial_status,
                refund_amount, refund_fee, course_type, sessions, price, cost,
                gift_sessions, other_cost, payment_channel, converted_from_trial,
                converted_to_course, created_at, updated_at
            )
            SELECT 
                id, name, customer_id, is_trial, trial_price, source, trial_status,
                refund_amount, refund_fee, course_type, sessions, price, cost,
                gift_sessions, other_cost, payment_channel, converted_from_trial,
                converted_to_course, created_at, updated_at
            FROM course
        ''')
        
        # 3. 删除旧表
        cursor.execute('DROP TABLE course')
        
        # 4. 重命名新表
        cursor.execute('ALTER TABLE course_new RENAME TO course')
        
        # 提交事务
        conn.commit()
        print("✓ 成功删除assigned_employee_id字段")
        
        return True
        
    except Exception as e:
        print(f"删除字段失败: {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = remove_employee_field()
    if success:
        print("迁移完成！")
        sys.exit(0)
    else:
        print("迁移失败！")
        sys.exit(1)