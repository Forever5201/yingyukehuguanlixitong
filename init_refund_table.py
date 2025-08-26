#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化退费表的脚本
"""

import sqlite3
import os
from datetime import datetime

def init_refund_table():
    """创建course_refund表"""
    
    # 数据库路径
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在")
        return False
    
    print(f"连接数据库：{db_path}")
    
    # 创建course_refund表的SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS course_refund (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        refund_sessions INTEGER NOT NULL,
        refund_amount DECIMAL(10,2) NOT NULL,
        refund_reason VARCHAR(200),
        refund_channel VARCHAR(50),
        refund_fee DECIMAL(10,2) DEFAULT 0,
        refund_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'completed',
        operator_name VARCHAR(100),
        remark TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES course(id)
    );
    """
    
    # 创建索引的SQL
    create_index_sql = [
        "CREATE INDEX IF NOT EXISTS idx_course_refund_course_id ON course_refund(course_id);",
        "CREATE INDEX IF NOT EXISTS idx_course_refund_status ON course_refund(status);",
        "CREATE INDEX IF NOT EXISTS idx_course_refund_date ON course_refund(refund_date);"
    ]
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute(create_table_sql)
        print("✓ course_refund表创建成功")
        
        # 创建索引
        for index_sql in create_index_sql:
            cursor.execute(index_sql)
        print("✓ 索引创建成功")
        
        # 提交事务
        conn.commit()
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='course_refund'")
        result = cursor.fetchone()
        
        if result:
            print("✓ 验证成功：course_refund表已存在")
            
            # 显示表结构
            cursor.execute("PRAGMA table_info(course_refund)")
            columns = cursor.fetchall()
            
            print("\n表结构：")
            for col in columns:
                print(f"  - {col[1]} {col[2]}")
        else:
            print("✗ 验证失败：course_refund表未创建")
            return False
        
        # 关闭连接
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 错误：{str(e)}")
        return False

def main():
    """主函数"""
    print("=== 添加课程退费表 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success = init_refund_table()
    
    print("-" * 50)
    if success:
        print("✅ 退费表创建完成！")
    else:
        print("❌ 退费表创建失败！")

if __name__ == "__main__":
    main()