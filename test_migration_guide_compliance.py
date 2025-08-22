#!/usr/bin/env python3
"""
测试试听课逻辑是否符合 MIGRATION_GUIDE.md 的要求
"""

from app import create_app, db
from app.models import Course, Customer, Config
from app.services.course_service import CourseService

def test_migration_guide_compliance():
    """测试试听课逻辑是否符合迁移指南要求"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试试听课逻辑是否符合 MIGRATION_GUIDE.md 要求 ===\n")
        
        # 1. 测试状态过滤逻辑
        print("1. 测试状态过滤逻辑...")
        test_status_filtering()
        
        # 2. 测试退款手续费计算
        print("\n2. 测试退款手续费计算...")
        test_refund_fee_calculation()
        
        # 3. 测试业绩计算
        print("\n3. 测试业绩计算...")
        test_performance_calculation()
        
        # 4. 测试基础成本使用
        print("\n4. 测试基础成本使用...")
        test_base_cost_usage()
        
        print("\n=== 测试完成 ===")

def test_status_filtering():
    """测试状态过滤逻辑"""
    # 获取所有试听课
    trial_courses = Course.query.filter_by(is_trial=True).all()
    
    # 按MIGRATION_GUIDE.md规范分类
    valid_statuses = ['registered', 'converted', 'no_action', 'refunded']
    excluded_statuses = ['not_registered', 'mis_operation']
    
    included_count = 0
    excluded_count = 0
    
    for course in trial_courses:
        status = course.trial_status or 'registered'
        if status in excluded_statuses:
            excluded_count += 1
        elif status in valid_statuses:
            included_count += 1
        else:
            # 未知状态按已报名处理
            included_count += 1
    
    print(f"   - 计入汇总的试听课数量: {included_count}")
    print(f"   - 排除的试听课数量: {excluded_count}")
    print(f"   - 总计试听课数量: {len(trial_courses)}")
    
    # 验证：排除状态不应参与统计
    excluded_courses = [c for c in trial_courses if (c.trial_status or 'registered') in excluded_statuses]
    if excluded_courses:
        print(f"   - 排除的试听课: {[f'ID:{c.id}({c.trial_status})' for c in excluded_courses[:5]]}")

def test_refund_fee_calculation():
    """测试退款手续费计算"""
    # 获取退款试听课
    refunded_courses = Course.query.filter_by(is_trial=True, trial_status='refunded').all()
    
    print(f"   - 退款试听课数量: {len(refunded_courses)}")
    
    for course in refunded_courses[:3]:  # 只显示前3个
        refund_channel = course.refund_channel or ''
        trial_price = course.trial_price or 0
        
        if refund_channel == '淘宝':
            expected_fee = 0  # 淘宝原路退：手续费=0
        else:
            # 非原路退：按退款渠道计算手续费
            expected_fee = trial_price * 0.006  # 假设费率0.6%
        
        print(f"   - 试听课ID:{course.id}, 退款渠道:{refund_channel}, 原价:{trial_price}, 预期手续费:{expected_fee}")

def test_performance_calculation():
    """测试业绩计算"""
    # 使用CourseService计算业绩
    courses = CourseService.get_courses(course_type='trial')
    performance = CourseService.calculate_performance(courses)
    
    print(f"   - 试听课总数: {performance.get('trial_count', 0)}")
    print(f"   - 总收入: {performance.get('total_revenue', 0)}")
    print(f"   - 总成本: {performance.get('total_cost', 0)}")
    print(f"   - 总手续费: {performance.get('total_fees', 0)}")
    print(f"   - 总利润: {performance.get('total_profit', 0)}")
    
    # 验证利润计算公式
    calculated_profit = performance.get('total_revenue', 0) - performance.get('total_cost', 0)
    actual_profit = performance.get('total_profit', 0)
    
    if abs(calculated_profit - actual_profit) < 0.01:
        print("   ✅ 利润计算正确: 总收入 - 总成本")
    else:
        print(f"   ❌ 利润计算错误: 计算值={calculated_profit}, 实际值={actual_profit}")

def test_base_cost_usage():
    """测试基础成本使用"""
    # 获取基础试听成本配置
    trial_cost_config = Config.query.filter_by(key='trial_cost').first()
    base_trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
    
    print(f"   - 系统配置的基础试听成本: {base_trial_cost}")
    
    # 检查是否所有试听课都使用统一的基础成本
    trial_courses = Course.query.filter_by(is_trial=True).all()
    different_costs = set()
    
    for course in trial_courses:
        if course.cost and course.cost != base_trial_cost:
            different_costs.add(course.cost)
    
    if different_costs:
        print(f"   ⚠️  发现不同的成本值: {different_costs}")
        print("   - 建议：所有试听课应使用统一的基础成本配置")
    else:
        print("   ✅ 所有试听课使用统一的基础成本")

if __name__ == "__main__":
    test_migration_guide_compliance()



