#!/usr/bin/env python3
"""
清理运营成本测试数据的脚本
"""

import sqlite3
from datetime import datetime

def cleanup_test_data():
    """清理运营成本测试数据"""
    print("🧹 开始清理运营成本测试数据...")
    print("=" * 50)
    
    try:
        # 连接数据库
        conn = sqlite3.connect('instance/database.sqlite')
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 查看当前数据
        print("\n📊 清理前的数据:")
        cursor.execute("SELECT id, cost_type, cost_name, amount, cost_date FROM operational_cost")
        rows = cursor.fetchall()
        
        if not rows:
            print("   - 没有找到运营成本数据")
            return
        
        for row in rows:
            print(f"   - ID: {row[0]}, 类型: {row[1]}, 名称: {row[2]}, 金额: ¥{row[3]:.2f}, 日期: {row[4]}")
        
        # 确认清理
        print(f"\n⚠️  即将删除 {len(rows)} 条测试数据")
        print("这些数据包括:")
        print("   - 12月房租、水电费、网络费等测试数据")
        print("   - 教学设备维护、广告费等示例数据")
        
        # 删除所有测试数据
        cursor.execute("DELETE FROM operational_cost")
        deleted_count = cursor.rowcount
        
        # 提交更改
        conn.commit()
        
        print(f"\n✅ 清理完成！")
        print(f"   - 删除了 {deleted_count} 条测试数据")
        
        # 验证清理结果
        cursor.execute("SELECT COUNT(*) FROM operational_cost")
        remaining_count = cursor.fetchone()[0]
        print(f"   - 剩余数据: {remaining_count} 条")
        
        if remaining_count == 0:
            print("   - 所有测试数据已清理完毕")
        else:
            print("   - 仍有部分数据保留")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='operational_cost'")
        conn.commit()
        print("   - 自增ID已重置")
        
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("✅ 数据库连接已关闭")
    
    print("\n🎉 测试数据清理完成！")
    print("现在您可以添加真实的运营成本数据了。")
    
    return True

if __name__ == "__main__":
    cleanup_test_data()






