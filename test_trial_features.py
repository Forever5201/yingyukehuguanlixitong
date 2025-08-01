#!/usr/bin/env python3
"""
测试试听课相关功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Customer, Course, Config
from datetime import datetime

def test_trial_features():
    """测试试听课相关功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 试听课功能测试 ===")
        
        # 1. 测试数据统计
        print("\n1. 数据统计测试:")
        trial_courses = Course.query.filter_by(is_trial=True).all()
        formal_courses = Course.query.filter_by(is_trial=False).all()
        
        print(f"试听课数量: {len(trial_courses)}")
        print(f"正课数量: {len(formal_courses)}")
        
        # 试听课统计
        trial_revenue = sum(course.trial_price for course in trial_courses if course.trial_price)
        print(f"试听课总收入: ¥{trial_revenue:.2f}")
        
        # 正课统计
        formal_revenue = sum(course.price for course in formal_courses if course.price)
        formal_cost = sum(course.cost for course in formal_courses if course.cost)
        formal_profit = formal_revenue - formal_cost
        
        print(f"正课总收入: ¥{formal_revenue:.2f}")
        print(f"正课总成本: ¥{formal_cost:.2f}")
        print(f"正课总利润: ¥{formal_profit:.2f}")
        
        # 2. 测试试听课详情
        print("\n2. 试听课详情:")
        for course in trial_courses:
            customer = Customer.query.get(course.customer_id)
            print(f"- {customer.name}: ¥{course.trial_price:.2f} ({course.source or '未知渠道'})")
        
        # 3. 测试正课详情
        print("\n3. 正课详情:")
        for course in formal_courses:
            customer = Customer.query.get(course.customer_id)
            total_sessions = (course.sessions or 0) + (course.gift_sessions or 0)
            profit = (course.price or 0) - (course.cost or 0)
            print(f"- {customer.name}: {course.course_type} - {course.sessions}+{course.gift_sessions}节 - ¥{course.price:.2f} (利润: ¥{profit:.2f})")
        
        # 4. 测试配置
        print("\n4. 系统配置测试:")
        trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        
        print(f"试听课成本配置: {trial_cost_config.value if trial_cost_config else '未设置'}")
        print(f"正课成本配置: {course_cost_config.value if course_cost_config else '未设置'}")
        
        # 5. 测试转换关系
        print("\n5. 转换关系测试:")
        converted_courses = Course.query.filter(Course.converted_from_trial.isnot(None)).all()
        if converted_courses:
            for course in converted_courses:
                trial_course = Course.query.get(course.converted_from_trial)
                if trial_course:
                    customer = Customer.query.get(course.customer_id)
                    print(f"- {customer.name}: 试听课(¥{trial_course.trial_price:.2f}) → 正课({course.course_type}, ¥{course.price:.2f})")
        else:
            print("- 暂无转换记录")
        
        print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_trial_features()