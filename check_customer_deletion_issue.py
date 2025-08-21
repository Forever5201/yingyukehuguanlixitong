#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查客户删除后首页仍显示的问题
"""

from app import create_app, db
from app.models import Customer, Course, TaobaoOrder
from datetime import datetime

def check_database_status():
    """检查数据库中的实际数据状态"""
    app = create_app()
    
    with app.app_context():
        print("=== 数据库实际状态检查 ===")
        
        # 检查客户表
        total_customers = Customer.query.count()
        print(f"客户表中实际客户数量: {total_customers}")
        
        if total_customers > 0:
            print("\n现有客户列表:")
            customers = Customer.query.all()
            for customer in customers:
                print(f"  ID: {customer.id}, 姓名: {customer.name}, 手机: {customer.phone}, 创建时间: {customer.created_at}")
        
        # 检查试听课表
        total_trials = Course.query.filter_by(is_trial=True).count()
        print(f"\n试听课记录数量: {total_trials}")
        
        if total_trials > 0:
            print("\n现有试听课记录:")
            trials = Course.query.filter_by(is_trial=True).all()
            for trial in trials:
                customer = Customer.query.get(trial.customer_id)
                customer_name = customer.name if customer else "客户已删除"
                print(f"  试听课ID: {trial.id}, 客户ID: {trial.customer_id}, 客户姓名: {customer_name}")
        
        # 检查正课表
        total_formal = Course.query.filter_by(is_trial=False).count()
        print(f"\n正课记录数量: {total_formal}")
        
        # 检查刷单表
        total_orders = TaobaoOrder.query.count()
        print(f"刷单记录数量: {total_orders}")

def simulate_homepage_query():
    """模拟首页的数据查询逻辑"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 模拟首页数据查询 ===")
        
        # 模拟首页的客户统计查询
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        from sqlalchemy import case
        
        # 客户统计（与routes.py中的逻辑完全一致）
        customer_stats = db.session.query(
            db.func.count(Customer.id).label('total_customers'),
            db.func.sum(case((Customer.created_at >= current_month_start, 1), else_=0)).label('new_customers')
        ).first()
        
        print(f"首页查询结果 - 总客户数: {customer_stats.total_customers}")
        print(f"首页查询结果 - 本月新客户: {customer_stats.new_customers}")
        
        # 获取最近客户
        recent_customers = Customer.query.with_entities(
            Customer.name, Customer.created_at
        ).order_by(Customer.created_at.desc()).limit(5).all()
        
        print(f"\n最近客户列表 (显示在首页):")
        for customer in recent_customers:
            print(f"  姓名: {customer.name}, 创建时间: {customer.created_at}")

def check_foreign_key_constraints():
    """检查外键约束和孤儿记录"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 检查数据完整性 ===")
        
        # 检查是否有孤儿试听课记录（客户已删除但试听课还在）
        orphan_trials = db.session.query(Course).filter(
            Course.is_trial == True,
            ~Course.customer_id.in_(db.session.query(Customer.id))
        ).all()
        
        if orphan_trials:
            print(f"发现 {len(orphan_trials)} 条孤儿试听课记录:")
            for trial in orphan_trials:
                print(f"  试听课ID: {trial.id}, 客户ID: {trial.customer_id} (客户已删除)")
        else:
            print("没有发现孤儿试听课记录")
        
        # 检查是否有孤儿正课记录
        orphan_formal = db.session.query(Course).filter(
            Course.is_trial == False,
            ~Course.customer_id.in_(db.session.query(Customer.id))
        ).all()
        
        if orphan_formal:
            print(f"发现 {len(orphan_formal)} 条孤儿正课记录:")
            for course in orphan_formal:
                print(f"  正课ID: {course.id}, 客户ID: {course.customer_id} (客户已删除)")
        else:
            print("没有发现孤儿正课记录")

def test_customer_deletion():
    """测试客户删除功能"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试客户删除功能 ===")
        
        # 创建测试客户
        test_customer = Customer(
            name="测试删除客户",
            phone="19999999999",
            gender="男",
            grade="高一",
            region="测试区域"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        customer_id = test_customer.id
        print(f"创建测试客户，ID: {customer_id}")
        
        # 创建关联的试听课
        test_trial = Course(
            name="试听课",
            customer_id=customer_id,
            is_trial=True,
            trial_price=100.0,
            source="测试",
            cost=50.0
        )
        db.session.add(test_trial)
        db.session.commit()
        print(f"创建关联试听课，ID: {test_trial.id}")
        
        # 检查删除前的状态
        print("\n删除前状态:")
        print(f"  客户总数: {Customer.query.count()}")
        print(f"  试听课总数: {Course.query.filter_by(is_trial=True).count()}")
        
        # 模拟删除客户（不删除关联记录）
        print("\n执行客户删除...")
        db.session.delete(test_customer)
        db.session.commit()
        
        # 检查删除后的状态
        print("\n删除后状态:")
        print(f"  客户总数: {Customer.query.count()}")
        print(f"  试听课总数: {Course.query.filter_by(is_trial=True).count()}")
        
        # 检查是否产生了孤儿记录
        orphan_check = Course.query.filter_by(customer_id=customer_id).first()
        if orphan_check:
            print(f"  ⚠️ 发现孤儿记录: 试听课ID {orphan_check.id} 的客户ID {customer_id} 已不存在")
            # 清理孤儿记录
            db.session.delete(orphan_check)
            db.session.commit()
            print("  已清理孤儿记录")
        else:
            print("  ✅ 没有产生孤儿记录")

def suggest_fix():
    """建议修复方案"""
    print("\n=== 问题分析和修复建议 ===")
    
    print("\n可能的问题原因:")
    print("1. 客户删除时没有同时删除关联的课程记录，产生孤儿数据")
    print("2. 首页统计查询可能包含了已删除客户的关联数据")
    print("3. 数据库外键约束设置不当，允许孤儿记录存在")
    print("4. 浏览器缓存问题，显示的是缓存的数据")
    
    print("\n修复方案:")
    print("1. 修改客户删除API，添加级联删除逻辑")
    print("2. 清理现有的孤儿记录")
    print("3. 在数据库模型中添加外键约束")
    print("4. 在首页添加强制刷新机制")

if __name__ == '__main__':
    check_database_status()
    simulate_homepage_query()
    check_foreign_key_constraints()
    test_customer_deletion()
    suggest_fix()