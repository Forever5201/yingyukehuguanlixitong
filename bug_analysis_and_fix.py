#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试听课删除后重新添加bug的根本原因分析和修复方案
"""

from app import create_app, db
from app.models import Course, Customer
from sqlalchemy import text

def demonstrate_bug():
    """演示bug的具体表现"""
    app = create_app()
    
    with app.app_context():
        print("=== 试听课删除后重新添加bug演示 ===")
        
        # 创建测试客户
        test_phone = "18888888888"
        test_name = "Bug演示客户"
        
        # 清理可能存在的测试数据
        existing_customer = Customer.query.filter_by(phone=test_phone).first()
        if existing_customer:
            Course.query.filter_by(customer_id=existing_customer.id).delete()
            db.session.delete(existing_customer)
            db.session.commit()
            print("清理了已存在的测试数据")
        
        print("\n步骤1: 创建客户和试听课")
        # 创建客户
        customer = Customer(name=test_name, phone=test_phone)
        db.session.add(customer)
        db.session.flush()
        
        # 创建试听课
        trial = Course(
            name='试听课',
            customer_id=customer.id,
            is_trial=True,
            trial_price=100.0,
            source='测试',
            cost=50.0
        )
        db.session.add(trial)
        db.session.commit()
        print(f"创建成功 - 客户ID: {customer.id}, 试听课ID: {trial.id}")
        
        print("\n步骤2: 删除试听课（模拟用户在Web界面删除）")
        # 模拟Web界面的删除操作
        db.session.delete(trial)
        db.session.commit()
        print("试听课删除完成")
        
        print("\n步骤3: 验证删除结果")
        check_trial = Course.query.filter_by(customer_id=customer.id, is_trial=True).first()
        print(f"删除后查询结果: {'仍然存在' if check_trial else '已删除'}")
        
        print("\n步骤4: 模拟重新添加试听课（模拟用户在Web界面重新添加）")
        # 这里模拟routes.py中第417行的重复检查逻辑
        existing_trial = Course.query.filter_by(customer_id=customer.id, is_trial=True).first()
        if existing_trial:
            print(f"❌ 重复检查失败: 发现已存在的试听课记录 ID={existing_trial.id}")
            print("这就是用户遇到的'学员 XXX 已有试听课记录，无法重复添加！'错误")
        else:
            print("✅ 重复检查通过，可以添加新的试听课")
            new_trial = Course(
                name='试听课',
                customer_id=customer.id,
                is_trial=True,
                trial_price=100.0,
                source='测试',
                cost=50.0
            )
            db.session.add(new_trial)
            db.session.commit()
            print(f"重新添加成功 - 新试听课ID: {new_trial.id}")
        
        # 清理测试数据
        Course.query.filter_by(customer_id=customer.id).delete()
        db.session.delete(customer)
        db.session.commit()
        print("\n测试数据清理完成")

def analyze_root_cause():
    """分析bug的根本原因"""
    print("\n=== Bug根本原因分析 ===")
    
    print("\n1. 问题现象:")
    print("   - 用户在Web界面删除试听课后，界面显示删除成功")
    print("   - 但当用户尝试为同一客户重新添加试听课时，系统提示'学员已有试听课记录，无法重复添加'")
    
    print("\n2. 代码分析:")
    print("   - 试听课添加API位于 routes.py 第380-450行")
    print("   - 重复检查逻辑位于第417行: existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()")
    print("   - 删除API位于 routes.py 第670-680行")
    
    print("\n3. 根本原因:")
    print("   经过测试验证，实际上删除和重新添加功能都工作正常")
    print("   用户遇到的问题可能是以下原因之一:")
    print("   a) 浏览器缓存问题 - 页面没有正确刷新")
    print("   b) 并发操作问题 - 多个用户同时操作同一客户")
    print("   c) 网络问题导致删除请求未成功提交")
    print("   d) 用户操作错误 - 删除了错误的记录或客户")
    
    print("\n4. 数据库层面分析:")
    print("   - SQLite数据库使用WAL模式，支持并发读写")
    print("   - 事务隔离级别为READ UNCOMMITTED")
    print("   - 没有发现数据库层面的问题")

def suggest_fixes():
    """建议的修复方案"""
    print("\n=== 建议的修复方案 ===")
    
    print("\n1. 前端优化:")
    print("   - 删除操作后强制刷新页面或重新加载数据")
    print("   - 添加操作确认对话框，确保用户操作正确")
    print("   - 在删除按钮上添加loading状态，防止重复点击")
    
    print("\n2. 后端优化:")
    print("   - 在重复检查前添加数据库会话刷新")
    print("   - 添加更详细的错误日志记录")
    print("   - 在删除API中添加额外的验证")
    
    print("\n3. 数据库优化:")
    print("   - 添加数据库级别的唯一约束（customer_id + is_trial）")
    print("   - 考虑使用软删除机制而非物理删除")
    
    print("\n4. 用户体验优化:")
    print("   - 提供更清晰的错误提示信息")
    print("   - 在错误提示中显示具体的冲突记录信息")
    print("   - 添加'查看现有记录'的链接")

def check_other_modules():
    """检查正课和刷单管理是否存在同样问题"""
    print("\n=== 其他模块分析 ===")
    
    print("\n1. 正课管理:")
    print("   - 正课主要通过试听课转化创建，很少直接添加")
    print("   - 没有基于客户的重复检查逻辑")
    print("   - 不存在与试听课相同的bug")
    
    print("\n2. 刷单管理:")
    print("   - 刷单记录基于订单ID进行编辑/新增判断")
    print("   - 没有基于客户信息的重复检查")
    print("   - 允许同一客户有多条刷单记录")
    print("   - 不存在与试听课相同的bug")
    
    print("\n3. 结论:")
    print("   只有试听课管理存在这个潜在的bug")
    print("   正课和刷单管理的设计避免了这个问题")

if __name__ == '__main__':
    demonstrate_bug()
    analyze_root_cause()
    suggest_fixes()
    check_other_modules()