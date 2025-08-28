#!/usr/bin/env python3
"""
运营成本表数据库迁移脚本
用于在现有系统中添加运营成本管理功能
"""

import os
import sys
import sqlite3
from datetime import datetime

def create_operational_cost_table(db_path):
    """创建运营成本表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='operational_cost'
        """)
        
        if cursor.fetchone():
            print("✅ 运营成本表已存在，跳过创建")
            return True
        
        # 创建运营成本表
        cursor.execute("""
            CREATE TABLE operational_cost (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cost_type VARCHAR(50) NOT NULL,
                cost_name VARCHAR(100) NOT NULL,
                amount REAL NOT NULL,
                cost_date DATE NOT NULL,
                billing_period VARCHAR(20),
                allocation_method VARCHAR(20) DEFAULT 'proportional',
                allocated_to_courses BOOLEAN DEFAULT 1,
                description TEXT,
                invoice_number VARCHAR(50),
                supplier VARCHAR(100),
                payment_recipient VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX idx_operational_cost_date 
            ON operational_cost(cost_date)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_operational_cost_type 
            ON operational_cost(cost_type)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_operational_cost_status 
            ON operational_cost(status)
        """)
        
        conn.commit()
        print("✅ 运营成本表创建成功")
        
        # 插入一些示例数据
        insert_sample_data(cursor)
        conn.commit()
        
        return True
        
    except Exception as e:
        print(f"❌ 创建运营成本表失败: {str(e)}")
        return False
        
    finally:
        conn.close()

def insert_sample_data(cursor):
    """插入示例运营成本数据"""
    try:
        sample_data = [
            ('房租', '12月房租', 5000.00, '2024-12-01', 'month', 'proportional', 1, '12月份房租费用', '', '房东', '房东', 'active'),
            ('水电费', '12月水电费', 800.00, '2024-12-01', 'month', 'proportional', 1, '12月份水电费', '', '物业公司', '物业公司', 'active'),
            ('网络费', '12月网络费', 300.00, '2024-12-01', 'month', 'proportional', 1, '12月份网络费', '', '电信公司', '电信公司', 'active'),
            ('设备费', '教学设备维护', 500.00, '2024-12-15', 'one-time', 'proportional', 1, '教学设备维护费用', 'INV001', '设备供应商', '设备供应商', 'active'),
            ('营销费', '12月广告费', 1000.00, '2024-12-01', 'month', 'proportional', 1, '12月份广告投放费用', 'INV002', '广告公司', '广告公司', 'active')
        ]
        
        cursor.executemany("""
            INSERT INTO operational_cost 
            (cost_type, cost_name, amount, cost_date, billing_period, allocation_method, 
             allocated_to_courses, description, invoice_number, supplier, payment_recipient, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        print("✅ 示例数据插入成功")
        
    except Exception as e:
        print(f"⚠️ 插入示例数据失败: {str(e)}")

def verify_migration(db_path):
    """验证迁移是否成功"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(operational_cost)")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'cost_type', 'cost_name', 'amount', 'cost_date', 
            'billing_period', 'allocation_method', 'allocated_to_courses',
            'description', 'invoice_number', 'supplier', 'payment_recipient', 'status',
            'created_at', 'updated_at'
        ]
        
        actual_columns = [col[1] for col in columns]
        
        if set(expected_columns) == set(actual_columns):
            print("✅ 表结构验证成功")
        else:
            print("❌ 表结构验证失败")
            print(f"期望列: {expected_columns}")
            print(f"实际列: {actual_columns}")
            return False
        
        # 检查数据
        cursor.execute("SELECT COUNT(*) FROM operational_cost")
        count = cursor.fetchone()[0]
        print(f"✅ 数据验证成功，共 {count} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False
        
    finally:
        conn.close()

def main():
    """主函数"""
    print("🚀 开始运营成本表数据库迁移...")
    
    # 确定数据库路径
    db_path = "instance/database.sqlite"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请确保在项目根目录下运行此脚本")
        return False
    
    print(f"📁 数据库路径: {db_path}")
    
    # 创建表
    if not create_operational_cost_table(db_path):
        return False
    
    # 验证迁移
    if not verify_migration(db_path):
        return False
    
    print("🎉 运营成本表数据库迁移完成！")
    print("\n📋 迁移内容:")
    print("  - 创建 operational_cost 表")
    print("  - 添加必要的索引")
    print("  - 插入示例数据")
    print("\n🔧 下一步:")
    print("  1. 重启Flask应用")
    print("  2. 访问系统配置页面")
    print("  3. 查看新增的'运营成本'标签页")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
