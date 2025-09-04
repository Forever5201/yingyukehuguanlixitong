#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查分红表是否存在的脚本
"""

import sqlite3
import os

def check_dividend_tables():
    """检查分红相关表是否存在"""
    
    # 检查数据库文件
    db_files = ['instance/database.sqlite', 'instance/database.db']
    db_path = None
    
    for db_file in db_files:
        if os.path.exists(db_file):
            db_path = db_file
            break
    
    if not db_path:
        print("❌ 未找到数据库文件")
        return False
    
    print(f"✅ 找到数据库文件: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 数据库中共有 {len(tables)} 个表")
        
        # 检查分红相关表
        dividend_tables = [t for t in tables if 'dividend' in t.lower()]
        
        if dividend_tables:
            print("✅ 找到分红相关表:")
            for table in dividend_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  📋 {table}: {count} 条记录")
                
                # 查看表结构
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"     字段: {[col[1] for col in columns]}")
                
        else:
            print("❌ 未找到分红相关表 (dividend_record, dividend_summary)")
            print("📋 现有表:", [t for t in tables if not t.startswith('sqlite_')])
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
        return False

if __name__ == '__main__':
    print("🔍 检查股东分红表...")
    success = check_dividend_tables()
    
    if not success:
        print("\n💡 如果分红表不存在，需要运行迁移脚本:")
        print("   python migrations/add_dividend_tables.py")