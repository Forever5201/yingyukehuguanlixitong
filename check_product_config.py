#!/usr/bin/env python3
"""
检查数据库中的商品配置
"""

import sqlite3
import json
import os

def check_product_config():
    """检查数据库中的商品配置"""
    print("🔍 检查数据库中的商品配置...")
    
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查config表中的商品配置
        cursor.execute("SELECT key, value FROM config WHERE key = 'shuadan_products'")
        result = cursor.fetchone()
        
        if result:
            key, value = result
            print(f"✓ 找到商品配置: {key}")
            print(f"  值: {value}")
            
            # 尝试解析JSON
            try:
                products = json.loads(value)
                print(f"  解析为JSON: {products}")
                print(f"  商品数量: {len(products)}")
            except json.JSONDecodeError:
                print(f"  ❌ JSON解析失败，原始值: {value}")
        else:
            print("❌ 未找到商品配置记录")
        
        # 检查所有配置
        print("\n📋 所有配置记录:")
        cursor.execute("SELECT key, value FROM config ORDER BY key")
        configs = cursor.fetchall()
        
        for key, value in configs:
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_product_config()

