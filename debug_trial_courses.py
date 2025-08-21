#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析试听课删除后重新添加的bug
"""

from app import create_app, db
from app.models import Course, Customer
from sqlalchemy import text

def analyze_trial_course_bug():
    """深入分析试听课删除后重新添加的bug"""
    app = create_app()
    
    with app.app_context():
        print("=== 深入分析试听课删除后重新添加的bug ===")
        
        # 1. 检查数据库中的所有试听课记录（包括可能的软删除记录）
        print("\n1. 检查数据库中的所有试听课记录:")
        trial_courses = Course.query.filter_by(is_trial=True).all()
        print(f"当前试听课记录总数: {len(trial_courses)}")
        
        for course in trial_courses:
            customer = Customer.query.get(course.customer_id)
            print(f"  - ID: {course.id}, 客户: {customer.name if customer else '未知'}, "
                  f"电话: {customer.phone if customer else '未知'}, "
                  f"状态: {course.trial_status}, "
                  f"创建时间: {course.created_at}")
        
        # 2. 直接查询数据库表，检查是否有隐藏的记录
        print("\n2. 直接查询Course表中的所有is_trial=True记录:")
        result = db.session.execute(text("SELECT id, customer_id, is_trial, trial_status, created_at FROM course WHERE is_trial = 1"))
        raw_records = result.fetchall()
        print(f"原始SQL查询结果数量: {len(raw_records)}")
        
        for record in raw_records:
            print(f"  - ID: {record[0]}, customer_id: {record[1]}, is_trial: {record[2]}, "
                  f"trial_status: {record[3]}, created_at: {record[4]}")
        
        # 3. 检查所有客户及其关联的课程记录
        print("\n3. 检查所有客户及其关联的课程记录:")
        customers = Customer.query.all()
        for customer in customers:
            # 查询该客户的所有课程记录
            all_courses = Course.query.filter_by(customer_id=customer.id).all()
            trial_courses = [c for c in all_courses if c.is_trial]
            formal_courses = [c for c in all_courses if not c.is_trial]
            
            if all_courses:
                print(f"  客户: {customer.name} ({customer.phone})")
                print(f"    - 试听课: {len(trial_courses)} 个")
                print(f"    - 正课: {len(formal_courses)} 个")
                
                for trial in trial_courses:
                    print(f"      试听课ID: {trial.id}, 状态: {trial.trial_status}")
                for formal in formal_courses:
                    print(f"      正课ID: {formal.id}, 类型: {formal.course_type}")
        
        # 4. 检查数据库事务隔离级别和自动提交设置
        print("\n4. 检查数据库配置:")
        isolation_result = db.session.execute(text("PRAGMA read_uncommitted"))
        isolation_level = isolation_result.fetchone()
        print(f"数据库隔离级别: {isolation_level}")
        
        # 5. 模拟删除和重新添加的过程
        print("\n5. 模拟删除和重新添加的过程:")
        test_customer_phone = "17844540733"
        test_customer = Customer.query.filter_by(phone=test_customer_phone).first()
        
        if test_customer:
            print(f"找到测试客户: {test_customer.name} ({test_customer.phone})")
            
            # 检查该客户的试听课记录
            existing_trials = Course.query.filter_by(customer_id=test_customer.id, is_trial=True).all()
            print(f"该客户当前的试听课记录数: {len(existing_trials)}")
            
            for trial in existing_trials:
                print(f"  试听课ID: {trial.id}, 状态: {trial.trial_status}, 创建时间: {trial.created_at}")
            
            # 模拟重复检查逻辑
            duplicate_check = Course.query.filter_by(customer_id=test_customer.id, is_trial=True).first()
            if duplicate_check:
                print(f"❌ 重复检查失败: 发现已存在的试听课记录 ID={duplicate_check.id}")
                print("这就是导致'客户已存在'错误的原因！")
            else:
                print("✅ 重复检查通过: 没有发现已存在的试听课记录")
        
        # 6. 检查数据库连接池和缓存
        print("\n6. 检查数据库连接和缓存状态:")
        print(f"SQLAlchemy连接池状态: {db.engine.pool.status()}")
        
        # 7. 检查是否有外键约束或触发器影响删除
        print("\n7. 检查数据库表结构和约束:")
        schema_result = db.session.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='course'"))
        schema = schema_result.fetchone()
        if schema:
            print(f"Course表结构: {schema[0]}")

def test_delete_and_readd():
    """测试删除和重新添加的完整流程"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试删除和重新添加的完整流程 ===")
        
        # 创建一个测试客户和试听课
        test_phone = "19999999999"
        test_name = "删除测试客户"
        
        # 清理可能存在的测试数据
        existing_customer = Customer.query.filter_by(phone=test_phone).first()
        if existing_customer:
            # 删除该客户的所有课程记录
            Course.query.filter_by(customer_id=existing_customer.id).delete()
            # 删除客户记录
            db.session.delete(existing_customer)
            db.session.commit()
            print("清理了已存在的测试数据")
        
        # 1. 创建新客户和试听课
        print("\n步骤1: 创建新客户和试听课")
        new_customer = Customer(name=test_name, phone=test_phone)
        db.session.add(new_customer)
        db.session.flush()
        
        new_trial = Course(
            name='试听课',
            customer_id=new_customer.id,
            is_trial=True,
            trial_price=100.0,
            source='测试',
            cost=50.0
        )
        db.session.add(new_trial)
        db.session.commit()
        print(f"创建成功 - 客户ID: {new_customer.id}, 试听课ID: {new_trial.id}")
        
        # 2. 验证记录存在
        print("\n步骤2: 验证记录存在")
        check_trial = Course.query.filter_by(customer_id=new_customer.id, is_trial=True).first()
        print(f"验证结果: {'存在' if check_trial else '不存在'}")
        
        # 3. 模拟删除操作
        print("\n步骤3: 模拟删除操作")
        if check_trial:
            db.session.delete(check_trial)
            db.session.commit()
            print("删除操作完成")
        
        # 4. 验证删除结果
        print("\n步骤4: 验证删除结果")
        check_after_delete = Course.query.filter_by(customer_id=new_customer.id, is_trial=True).first()
        print(f"删除后验证结果: {'仍然存在' if check_after_delete else '已删除'}")
        
        # 5. 模拟重新添加
        print("\n步骤5: 模拟重新添加")
        duplicate_check = Course.query.filter_by(customer_id=new_customer.id, is_trial=True).first()
        if duplicate_check:
            print(f"❌ 重复检查失败: 发现已存在记录 ID={duplicate_check.id}")
        else:
            print("✅ 重复检查通过，可以添加新记录")
            new_trial_2 = Course(
                name='试听课',
                customer_id=new_customer.id,
                is_trial=True,
                trial_price=100.0,
                source='测试',
                cost=50.0
            )
            db.session.add(new_trial_2)
            db.session.commit()
            print(f"重新添加成功 - 新试听课ID: {new_trial_2.id}")
        
        # 清理测试数据
        Course.query.filter_by(customer_id=new_customer.id).delete()
        db.session.delete(new_customer)
        db.session.commit()
        print("\n测试数据清理完成")

if __name__ == '__main__':
    analyze_trial_course_bug()
    test_delete_and_readd()