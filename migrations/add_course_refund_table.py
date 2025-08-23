#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加课程退费表的数据库迁移脚本
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_course_refund_table():
    """创建course_refund表"""
    
    print("=== 添加课程退费表 ===")
    
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
    
    app = create_app()
    
    with app.app_context():
        try:
            # 创建表
            db.session.execute(text(create_table_sql))
            print("✓ course_refund表创建成功")
            
            # 创建索引
            for index_sql in create_index_sql:
                db.session.execute(text(index_sql))
            print("✓ 索引创建成功")
            
            # 提交事务
            db.session.commit()
            
            # 验证表是否创建成功
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='course_refund'"
            )).fetchone()
            
            if result:
                print("✓ 验证成功：course_refund表已存在")
                
                # 显示表结构
                columns = db.session.execute(text(
                    "PRAGMA table_info(course_refund)"
                )).fetchall()
                
                print("\n表结构：")
                for col in columns:
                    print(f"  - {col[1]} {col[2]}")
            else:
                print("✗ 验证失败：course_refund表未创建")
                return False
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 错误：{str(e)}")
            return False

def main():
    """主函数"""
    print("开始执行数据库迁移...")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success = add_course_refund_table()
    
    print("-" * 50)
    if success:
        print("✅ 数据库迁移完成！")
    else:
        print("❌ 数据库迁移失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()