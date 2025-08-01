#!/usr/bin/env python3
"""
添加试听课和正课测试数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Customer, Course
from datetime import datetime, timedelta

def add_test_data():
    """添加测试数据"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有客户数据
        existing_customers = Customer.query.count()
        print(f"现有客户数量: {existing_customers}")
        
        # 如果没有客户，先添加一些客户
        if existing_customers == 0:
            customers_data = [
                {'name': '张小明', 'gender': '男', 'grade': '三年级', 'region': '北京', 'phone': '13800138001', 'source': '朋友推荐'},
                {'name': '李小红', 'gender': '女', 'grade': '四年级', 'region': '上海', 'phone': '13800138002', 'source': '网络广告'},
                {'name': '王小华', 'gender': '男', 'grade': '五年级', 'region': '广州', 'phone': '13800138003', 'source': '学校推荐'},
                {'name': '赵小美', 'gender': '女', 'grade': '二年级', 'region': '深圳', 'phone': '13800138004', 'source': '朋友推荐'},
                {'name': '刘小强', 'gender': '男', 'grade': '六年级', 'region': '杭州', 'phone': '13800138005', 'source': '网络广告'},
            ]
            
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.session.add(customer)
            
            db.session.commit()
            print("✓ 添加了5个测试客户")
        
        # 获取客户列表
        customers = Customer.query.all()
        
        # 添加试听课数据
        trial_courses_data = [
            {'customer_id': customers[0].id, 'is_trial': True, 'trial_price': 9.9, 'source': '朋友推荐'},
            {'customer_id': customers[1].id, 'is_trial': True, 'trial_price': 19.9, 'source': '网络广告'},
            {'customer_id': customers[2].id, 'is_trial': True, 'trial_price': 9.9, 'source': '学校推荐'},
            {'customer_id': customers[3].id, 'is_trial': True, 'trial_price': 29.9, 'source': '朋友推荐'},
        ]
        
        for i, trial_data in enumerate(trial_courses_data):
            # 检查是否已存在
            existing = Course.query.filter_by(
                customer_id=trial_data['customer_id'], 
                is_trial=True
            ).first()
            
            if not existing:
                trial_course = Course(
                    name=f"试听课-{customers[trial_data['customer_id']-1].name}",
                    customer_id=trial_data['customer_id'],
                    is_trial=trial_data['is_trial'],
                    trial_price=trial_data['trial_price'],
                    source=trial_data['source'],
                    created_at=datetime.now() - timedelta(days=i*2),
                    updated_at=datetime.now() - timedelta(days=i*2)
                )
                db.session.add(trial_course)
                print(f"✓ 添加试听课: {trial_course.name}")
        
        # 添加正课数据
        formal_courses_data = [
            {
                'customer_id': customers[0].id, 
                'is_trial': False, 
                'course_type': '单词课',
                'sessions': 20, 
                'price': 2000.0, 
                'gift_sessions': 2,
                'other_cost': 50.0
            },
            {
                'customer_id': customers[1].id, 
                'is_trial': False, 
                'course_type': '语法课',
                'sessions': 15, 
                'price': 1800.0, 
                'gift_sessions': 1,
                'other_cost': 30.0
            },
        ]
        
        for i, formal_data in enumerate(formal_courses_data):
            # 检查是否已存在
            existing = Course.query.filter_by(
                customer_id=formal_data['customer_id'], 
                is_trial=False
            ).first()
            
            if not existing:
                # 计算成本（假设每节课成本为50元）
                total_sessions = formal_data['sessions'] + formal_data['gift_sessions']
                session_cost = total_sessions * 50  # 每节课50元成本
                total_cost = session_cost + formal_data['other_cost']
                
                formal_course = Course(
                    name=f"正课-{customers[formal_data['customer_id']-1].name}",
                    customer_id=formal_data['customer_id'],
                    is_trial=formal_data['is_trial'],
                    course_type=formal_data['course_type'],
                    sessions=formal_data['sessions'],
                    price=formal_data['price'],
                    cost=total_cost,
                    gift_sessions=formal_data['gift_sessions'],
                    other_cost=formal_data['other_cost'],
                    created_at=datetime.now() - timedelta(days=i*3),
                    updated_at=datetime.now() - timedelta(days=i*3)
                )
                db.session.add(formal_course)
                print(f"✓ 添加正课: {formal_course.name}")
        
        db.session.commit()
        print("✓ 测试数据添加完成")
        
        # 显示统计信息
        trial_count = Course.query.filter_by(is_trial=True).count()
        formal_count = Course.query.filter_by(is_trial=False).count()
        print(f"试听课数量: {trial_count}")
        print(f"正课数量: {formal_count}")

if __name__ == '__main__':
    add_test_data()