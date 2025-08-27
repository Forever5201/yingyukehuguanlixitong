#!/usr/bin/env python3
"""
为运营成本表添加payment_recipient字段的迁移脚本
"""

import sqlite3

def add_payment_recipient_field():
    """为运营成本表添加payment_recipient字段"""
    print("🔧 开始为运营成本表添加payment_recipient字段...")
    print("=" * 60)
    
    try:
        # 连接数据库
        conn = sqlite3.connect('instance/database.sqlite')
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(operational_cost)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'payment_recipient' in column_names:
            print("✅ payment_recipient字段已存在，无需添加")
            return True
        
        print("📊 当前表结构:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # 添加新字段
        print("\n➕ 添加payment_recipient字段...")
        cursor.execute("""
            ALTER TABLE operational_cost 
            ADD COLUMN payment_recipient VARCHAR(100)
        """)
        
        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(operational_cost)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        if 'payment_recipient' in new_column_names:
            print("✅ payment_recipient字段添加成功")
        else:
            print("❌ payment_recipient字段添加失败")
            return False
        
        # 更新现有数据，将supplier的值复制到payment_recipient
        print("\n🔄 更新现有数据...")
        cursor.execute("""
            UPDATE operational_cost 
            SET payment_recipient = supplier 
            WHERE payment_recipient IS NULL OR payment_recipient = ''
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ 更新了 {updated_count} 条记录")
        
        # 显示更新后的表结构
        print("\n📊 更新后的表结构:")
        cursor.execute("PRAGMA table_info(operational_cost)")
        final_columns = cursor.fetchall()
        for col in final_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # 验证数据
        print("\n🔍 验证数据...")
        cursor.execute("SELECT COUNT(*) FROM operational_cost")
        total_count = cursor.fetchone()[0]
        print(f"   - 总记录数: {total_count}")
        
        cursor.execute("SELECT COUNT(*) FROM operational_cost WHERE payment_recipient IS NOT NULL AND payment_recipient != ''")
        filled_count = cursor.fetchone()[0]
        print(f"   - 已填充payment_recipient的记录数: {filled_count}")
        
        if filled_count == total_count:
            print("✅ 所有记录的payment_recipient字段都已正确填充")
        else:
            print(f"⚠️  还有 {total_count - filled_count} 条记录的payment_recipient字段为空")
        
        conn.commit()
        print("\n🎉 字段添加和数据迁移完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    add_payment_recipient_field()
