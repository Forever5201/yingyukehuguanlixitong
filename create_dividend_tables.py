#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接创建股东分红记录管理表的脚本
"""

import sqlite3
import os
from datetime import datetime

def create_dividend_tables():
    """创建分红记录相关表"""
    
    # 找到数据库文件
    db_files = ['instance/database.sqlite', 'instance/database.db']
    db_path = None
    
    for db_file in db_files:
        if os.path.exists(db_file):
            db_path = db_file
            break
    
    if not db_path:
        print("❌ 未找到数据库文件")
        return False
    
    print(f"📂 使用数据库文件: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('dividend_record', 'dividend_summary')")
        existing_tables = cursor.fetchall()
        
        if existing_tables:
            print(f"⚠️  以下表已存在: {[t[0] for t in existing_tables]}")
            response = input("是否要删除现有表并重新创建？(y/N): ")
            if response.lower() != 'y':
                print("❌ 取消操作")
                return False
            
            # 删除现有表
            for table in existing_tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                print(f"🗑️  删除表: {table[0]}")
        
        # 创建股东分红记录表
        print("📋 创建 dividend_record 表...")
        cursor.execute("""
            CREATE TABLE dividend_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- 基本信息
                shareholder_name VARCHAR(100) NOT NULL,
                period_year INTEGER NOT NULL,
                period_month INTEGER NOT NULL,
                
                -- 分红金额信息
                calculated_profit FLOAT NOT NULL,
                actual_dividend FLOAT NOT NULL,
                dividend_date DATE NOT NULL,
                
                -- 分红状态
                status VARCHAR(20) DEFAULT 'pending',
                payment_method VARCHAR(50),
                
                -- 备注信息
                remarks TEXT,
                operator_name VARCHAR(100),
                
                -- 快照信息
                snapshot_total_profit FLOAT,
                snapshot_profit_ratio FLOAT,
                
                -- 时间戳
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建分红汇总表
        print("📋 创建 dividend_summary 表...")
        cursor.execute("""
            CREATE TABLE dividend_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- 股东信息
                shareholder_name VARCHAR(100) NOT NULL UNIQUE,
                
                -- 汇总信息
                total_calculated FLOAT DEFAULT 0,
                total_paid FLOAT DEFAULT 0,
                total_pending FLOAT DEFAULT 0,
                
                -- 统计信息
                record_count INTEGER DEFAULT 0,
                last_dividend_date DATE,
                
                -- 时间戳
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        print("🔍 创建索引...")
        indices = [
            ("idx_dividend_date", "dividend_record", "dividend_date"),
            ("idx_dividend_period", "dividend_record", "period_year, period_month"),
            ("idx_dividend_shareholder", "dividend_record", "shareholder_name"),
            ("idx_dividend_status", "dividend_record", "status")
        ]
        
        for idx_name, table_name, columns in indices:
            cursor.execute(f"CREATE INDEX {idx_name} ON {table_name}({columns})")
            print(f"  ✅ {idx_name}")
        
        # 创建唯一约束
        print("🛡️  创建唯一约束...")
        cursor.execute("""
            CREATE UNIQUE INDEX uq_dividend_record 
            ON dividend_record(shareholder_name, period_year, period_month, dividend_date)
        """)
        
        # 初始化股东汇总记录
        print("👥 初始化股东数据...")
        cursor.execute("""
            INSERT INTO dividend_summary (shareholder_name) 
            VALUES ('股东A'), ('股东B')
        """)
        
        # 提交事务
        conn.commit()
        print("✅ 所有表创建成功！")
        
        # 验证创建结果
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%dividend%'")
        tables = cursor.fetchall()
        print(f"🎉 已创建的分红表: {[t[0] for t in tables]}")
        
        # 检查初始数据
        cursor.execute("SELECT shareholder_name FROM dividend_summary")
        shareholders = cursor.fetchall()
        print(f"👥 初始股东: {[s[0] for s in shareholders]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建表时出错: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("🚀 开始创建股东分红记录管理表...")
    success = create_dividend_tables()
    
    if success:
        print("\n🎉 分红功能已准备就绪！")
        print("现在您可以:")
        print("1. 访问报表中心页面 (http://localhost:5000/profit-distribution)")
        print("2. 点击股东卡片查看分红详情")
        print("3. 添加和管理分红记录")
    else:
        print("\n❌ 创建失败，请检查错误信息")