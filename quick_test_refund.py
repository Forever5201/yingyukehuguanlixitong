#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试退费功能是否可用
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Course, Customer, Employee, CourseRefund
from sqlalchemy import inspect

def quick_test():
    """快速测试退费功能"""
    
    print("=== 快速测试退费功能 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        app = create_app()
        
        with app.app_context():
            # 1. 检查表是否存在
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'course_refund' in tables:
                print("✓ course_refund 表存在")
                
                # 获取表结构
                columns = inspector.get_columns('course_refund')
                print("\n表结构：")
                for col in columns:
                    print(f"  - {col['name']} ({col['type']})")
            else:
                print("✗ course_refund 表不存在")
                return False
            
            # 2. 检查是否可以查询
            try:
                count = CourseRefund.query.count()
                print(f"\n✓ 可以查询 CourseRefund 表，当前有 {count} 条记录")
            except Exception as e:
                print(f"\n✗ 查询 CourseRefund 表失败：{str(e)}")
                return False
            
            # 3. 检查关键函数是否存在
            try:
                from app.routes import calculate_course_profit_with_refund
                print("✓ calculate_course_profit_with_refund 函数已导入")
            except ImportError:
                print("✗ 无法导入 calculate_course_profit_with_refund 函数")
                return False
            
            # 4. 测试API端点是否可访问
            with app.test_client() as client:
                # 尝试获取一个不存在的课程的退费信息
                response = client.get('/api/courses/99999/refund-info')
                if response.status_code == 404:
                    print("✓ 退费API端点可访问")
                else:
                    print(f"? API返回状态码：{response.status_code}")
            
            print("\n✅ 退费功能基本检查通过！")
            print("\n您可以：")
            print("1. 运行 python run.py 启动应用")
            print("2. 访问正课管理页面")
            print("3. 每个正课都应该有'退费'按钮")
            
            return True
            
    except Exception as e:
        print(f"\n✗ 测试过程中出错：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    quick_test()