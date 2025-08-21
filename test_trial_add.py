#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试试听课添加逻辑 - 测试用户反馈的具体场景
"""

from app import create_app, db
from app.models import Course, Customer

def test_existing_customer_trial():
    """测试为已存在客户添加试听课"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试为已存在客户添加试听课 ===")
        
        # 测试用户反馈的手机号
        test_phone = "17844540733"
        
        # 1. 检查是否已有该手机号的客户
        existing_customer = Customer.query.filter_by(phone=test_phone).first()
        if existing_customer:
            print(f"发现已存在客户: {existing_customer.name}, 电话: {existing_customer.phone}")
            customer_id = existing_customer.id
            
            # 2. 检查该客户是否已有试听课记录
            existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()
            if existing_trial:
                print(f"发现已存在的试听课记录: ID={existing_trial.id}")
                print("这就是导致错误的原因！")
                print(f"试听课状态: {existing_trial.trial_status}")
                print(f"试听课创建时间: {existing_trial.created_at}")
            else:
                print("没有找到已存在的试听课记录，可以添加新的试听课")
        else:
            print("没有找到该手机号的客户")

def test_all_customers_trials():
    """检查所有客户的试听课情况"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 检查所有客户的试听课情况 ===")
        
        customers = Customer.query.all()
        for customer in customers:
            trials = Course.query.filter_by(customer_id=customer.id, is_trial=True).all()
            if trials:
                print(f"客户: {customer.name} ({customer.phone}) 有 {len(trials)} 个试听课记录:")
                for trial in trials:
                    print(f"  - ID: {trial.id}, 状态: {trial.trial_status}, 创建时间: {trial.created_at}")

if __name__ == '__main__':
    test_existing_customer_trial()
    test_all_customers_trials()