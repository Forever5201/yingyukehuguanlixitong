#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析正课和刷单管理是否存在与试听课相同的bug
"""

from app import create_app, db
from app.models import Course, Customer, TaobaoOrder
from sqlalchemy import text

def analyze_formal_course_bug():
    """分析正课管理是否存在删除后重新添加的bug"""
    app = create_app()
    
    with app.app_context():
        print("=== 分析正课管理的删除和重新添加逻辑 ===")
        
        # 1. 检查正课添加逻辑
        print("\n1. 正课添加逻辑分析:")
        print("正课主要通过以下方式添加:")
        print("  - 试听课转正课 (convert_trial_to_course)")
        print("  - 直接添加正课 (需要查看是否有独立的添加API)")
        
        # 2. 检查现有正课记录
        print("\n2. 检查现有正课记录:")
        formal_courses = Course.query.filter_by(is_trial=False).all()
        print(f"当前正课记录总数: {len(formal_courses)}")
        
        for course in formal_courses:
            customer = Customer.query.get(course.customer_id)
            print(f"  - ID: {course.id}, 客户: {customer.name if customer else '未知'}, "
                  f"电话: {customer.phone if customer else '未知'}, "
                  f"类型: {course.course_type}, "
                  f"转化来源: {'试听课转化' if course.converted_from_trial else '直接报名'}")
        
        # 3. 模拟正课删除和重新添加
        print("\n3. 模拟正课删除和重新添加:")
        test_customer_phone = "17844540733"
        test_customer = Customer.query.filter_by(phone=test_customer_phone).first()
        
        if test_customer:
            print(f"找到测试客户: {test_customer.name} ({test_customer.phone})")
            
            # 检查该客户的正课记录
            existing_formal = Course.query.filter_by(customer_id=test_customer.id, is_trial=False).all()
            print(f"该客户当前的正课记录数: {len(existing_formal)}")
            
            for formal in existing_formal:
                print(f"  正课ID: {formal.id}, 类型: {formal.course_type}, 创建时间: {formal.created_at}")
            
            # 检查是否有重复检查逻辑
            print("\n正课添加重复检查分析:")
            print("从代码分析来看，正课添加主要通过试听课转化，没有独立的重复检查逻辑")
            print("因此正课管理不太可能存在与试听课相同的bug")

def analyze_shuadan_bug():
    """分析刷单管理是否存在删除后重新添加的bug"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 分析刷单管理的删除和重新添加逻辑 ===")
        
        # 1. 检查刷单添加逻辑
        print("\n1. 刷单添加逻辑分析:")
        print("刷单记录通过 manage_taobao_orders API 添加")
        print("添加逻辑基于 order_id 参数判断是新增还是编辑")
        print("没有基于客户信息的重复检查逻辑")
        
        # 2. 检查现有刷单记录
        print("\n2. 检查现有刷单记录:")
        shuadan_orders = TaobaoOrder.query.all()
        print(f"当前刷单记录总数: {len(shuadan_orders)}")
        
        for order in shuadan_orders:
            print(f"  - ID: {order.id}, 姓名: {order.name}, "
                  f"金额: {order.amount}, "
                  f"创建时间: {order.created_at}")
        
        # 3. 模拟刷单删除和重新添加
        print("\n3. 模拟刷单删除和重新添加:")
        
        # 创建测试刷单记录
        test_name = "测试刷单客户"
        test_amount = 100.0
        
        # 清理可能存在的测试数据
        existing_order = TaobaoOrder.query.filter_by(name=test_name).first()
        if existing_order:
            db.session.delete(existing_order)
            db.session.commit()
            print("清理了已存在的测试数据")
        
        # 创建新刷单记录
        print("\n步骤1: 创建新刷单记录")
        new_order = TaobaoOrder(
            name=test_name,
            level='V1',
            amount=test_amount,
            commission=5.0,
            taobao_fee=0.6,
            evaluated=False
        )
        db.session.add(new_order)
        db.session.commit()
        print(f"创建成功 - 刷单记录ID: {new_order.id}")
        
        # 验证记录存在
        print("\n步骤2: 验证记录存在")
        check_order = TaobaoOrder.query.filter_by(name=test_name).first()
        print(f"验证结果: {'存在' if check_order else '不存在'}")
        
        # 模拟删除操作
        print("\n步骤3: 模拟删除操作")
        if check_order:
            db.session.delete(check_order)
            db.session.commit()
            print("删除操作完成")
        
        # 验证删除结果
        print("\n步骤4: 验证删除结果")
        check_after_delete = TaobaoOrder.query.filter_by(name=test_name).first()
        print(f"删除后验证结果: {'仍然存在' if check_after_delete else '已删除'}")
        
        # 模拟重新添加
        print("\n步骤5: 模拟重新添加")
        duplicate_check = TaobaoOrder.query.filter_by(name=test_name).first()
        if duplicate_check:
            print(f"❌ 发现重复记录 ID={duplicate_check.id}")
        else:
            print("✅ 没有重复记录，可以重新添加")
            new_order_2 = TaobaoOrder(
                name=test_name,
                level='V1',
                amount=test_amount,
                commission=5.0,
                taobao_fee=0.6,
                evaluated=False
            )
            db.session.add(new_order_2)
            db.session.commit()
            print(f"重新添加成功 - 新刷单记录ID: {new_order_2.id}")
            
            # 清理测试数据
            db.session.delete(new_order_2)
            db.session.commit()
            print("测试数据清理完成")

def analyze_trial_course_bug_root_cause():
    """深入分析试听课bug的根本原因"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 试听课bug根本原因分析 ===")
        
        print("\n1. 试听课添加逻辑分析:")
        print("试听课添加API: /trial-courses (POST)")
        print("重复检查逻辑位于 routes.py 第417行:")
        print("existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()")
        print("这个检查是在 db.session.flush() 之后进行的")
        
        print("\n2. 问题分析:")
        print("根据用户反馈和代码分析，可能的原因包括:")
        print("  a) 数据库事务隔离级别问题")
        print("  b) SQLAlchemy会话缓存问题") 
        print("  c) 删除操作未正确提交")
        print("  d) 并发访问导致的数据不一致")
        
        print("\n3. 验证数据库事务状态:")
        # 检查当前事务状态
        result = db.session.execute(text("PRAGMA journal_mode"))
        journal_mode = result.fetchone()
        print(f"数据库日志模式: {journal_mode}")
        
        result = db.session.execute(text("PRAGMA synchronous"))
        sync_mode = result.fetchone()
        print(f"同步模式: {sync_mode}")
        
        result = db.session.execute(text("PRAGMA cache_size"))
        cache_size = result.fetchone()
        print(f"缓存大小: {cache_size}")
        
        print("\n4. 建议的修复方案:")
        print("  a) 在删除操作后添加 db.session.commit() 确保事务提交")
        print("  b) 在重复检查前添加 db.session.refresh() 刷新会话")
        print("  c) 使用数据库级别的唯一约束防止重复")
        print("  d) 添加更详细的日志记录来追踪问题")

if __name__ == '__main__':
    analyze_formal_course_bug()
    analyze_shuadan_bug()
    analyze_trial_course_bug_root_cause()