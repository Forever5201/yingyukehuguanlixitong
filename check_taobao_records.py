#!/usr/bin/env python3
"""
检查现有的刷单记录
"""

import sqlite3
import os
from datetime import datetime

def check_taobao_records():
    """检查现有的刷单记录"""
    print("🔍 检查现有的刷单记录...")
    
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查taobao_order表中的记录
        cursor.execute("""
            SELECT id, name, level, product_name, amount, commission, 
                   evaluated, order_time, created_at 
            FROM taobao_order 
            ORDER BY order_time DESC 
            LIMIT 10
        """)
        
        records = cursor.fetchall()
        
        if records:
            print(f"✓ 找到 {len(records)} 条刷单记录")
            print("\n📋 最近的刷单记录:")
            print("-" * 80)
            
            for record in records:
                (id, name, level, product_name, amount, commission, 
                 evaluated, order_time, created_at) = record
                
                print(f"ID: {id}")
                print(f"客户姓名: {name}")
                print(f"等级: {level}")
                print(f"商品名称: {product_name}")
                print(f"金额: ¥{amount}")
                print(f"佣金: ¥{commission}")
                print(f"已评价: {'是' if evaluated else '否'}")
                print(f"订单时间: {order_time}")
                print(f"创建时间: {created_at}")
                print("-" * 80)
        else:
            print("❌ 没有找到刷单记录")
            
        # 统计商品使用情况
        print("\n📊 商品使用统计:")
        cursor.execute("""
            SELECT product_name, COUNT(*) as count 
            FROM taobao_order 
            WHERE product_name IS NOT NULL AND product_name != ''
            GROUP BY product_name 
            ORDER BY count DESC
        """)
        
        product_stats = cursor.fetchall()
        
        if product_stats:
            for product, count in product_stats:
                print(f"  {product}: {count} 次")
        else:
            print("  暂无商品使用记录")
            
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_taobao_records()

