"""
批量修复历史数据的员工分配不一致问题
提供多种修复策略
"""

from app import create_app, db
from app.models import Course, Employee

app = create_app()

def analyze_inconsistencies():
    """分析所有的数据不一致情况"""
    with app.app_context():
        print("=== 分析员工分配不一致情况 ===\n")
        
        # 查找所有已转化的试听课
        trial_courses = Course.query.filter(
            Course.is_trial == True,
            Course.converted_to_course != None
        ).all()
        
        inconsistencies = {
            'trial_null_formal_assigned': [],  # 试听课未分配，正课已分配
            'trial_assigned_formal_null': [],  # 试听课已分配，正课未分配
            'different_employees': []          # 试听课和正课分配给不同员工
        }
        
        for trial in trial_courses:
            formal = Course.query.get(trial.converted_to_course)
            if not formal:
                continue
            
            if trial.assigned_employee_id is None and formal.assigned_employee_id is not None:
                inconsistencies['trial_null_formal_assigned'].append({
                    'trial': trial,
                    'formal': formal,
                    'formal_employee': formal.assigned_employee.name
                })
            elif trial.assigned_employee_id is not None and formal.assigned_employee_id is None:
                inconsistencies['trial_assigned_formal_null'].append({
                    'trial': trial,
                    'formal': formal,
                    'trial_employee': trial.assigned_employee.name
                })
            elif (trial.assigned_employee_id is not None and 
                  formal.assigned_employee_id is not None and 
                  trial.assigned_employee_id != formal.assigned_employee_id):
                inconsistencies['different_employees'].append({
                    'trial': trial,
                    'formal': formal,
                    'trial_employee': trial.assigned_employee.name,
                    'formal_employee': formal.assigned_employee.name
                })
        
        # 显示统计
        total = sum(len(v) for v in inconsistencies.values())
        print(f"总共发现 {total} 个不一致的情况：")
        print(f"1. 试听课未分配，正课已分配: {len(inconsistencies['trial_null_formal_assigned'])} 个")
        print(f"2. 试听课已分配，正课未分配: {len(inconsistencies['trial_assigned_formal_null'])} 个")
        print(f"3. 试听课和正课分配给不同员工: {len(inconsistencies['different_employees'])} 个")
        
        return inconsistencies


def show_detailed_inconsistencies(inconsistencies):
    """显示详细的不一致情况"""
    print("\n\n=== 详细不一致情况 ===")
    
    # 1. 试听课未分配，正课已分配（最常见的历史数据问题）
    if inconsistencies['trial_null_formal_assigned']:
        print("\n1. 试听课未分配，正课已分配:")
        print("-" * 80)
        for item in inconsistencies['trial_null_formal_assigned']:
            trial = item['trial']
            formal = item['formal']
            customer_name = trial.customer.name if trial.customer else "未知"
            print(f"  客户: {customer_name}")
            print(f"  - 试听课ID {trial.id}: 未分配")
            print(f"  - 正课ID {formal.id}: {item['formal_employee']}")
            
            # 检查续课
            renewals = Course.query.filter_by(renewal_from_course_id=formal.id).all()
            if renewals:
                print(f"  - 续课: {len(renewals)} 个")
            print()
    
    # 2. 其他不一致情况
    if inconsistencies['trial_assigned_formal_null']:
        print("\n2. 试听课已分配，正课未分配:")
        print("-" * 80)
        for item in inconsistencies['trial_assigned_formal_null']:
            trial = item['trial']
            formal = item['formal']
            customer_name = trial.customer.name if trial.customer else "未知"
            print(f"  客户: {customer_name}")
            print(f"  - 试听课ID {trial.id}: {item['trial_employee']}")
            print(f"  - 正课ID {formal.id}: 未分配")
            print()
    
    if inconsistencies['different_employees']:
        print("\n3. 试听课和正课分配给不同员工:")
        print("-" * 80)
        for item in inconsistencies['different_employees']:
            trial = item['trial']
            formal = item['formal']
            customer_name = trial.customer.name if trial.customer else "未知"
            print(f"  客户: {customer_name}")
            print(f"  - 试听课ID {trial.id}: {item['trial_employee']}")
            print(f"  - 正课ID {formal.id}: {item['formal_employee']}")
            print()


def fix_strategy_1(dry_run=True):
    """
    修复策略1：以正课为准
    适用于历史数据，保持现有正课的员工分配不变
    """
    with app.app_context():
        print("\n=== 修复策略1：以正课为准 ===")
        print("将试听课的员工分配更新为与正课一致\n")
        
        inconsistencies = analyze_inconsistencies()
        
        # 主要处理第一种情况：试听课未分配，正课已分配
        to_fix = inconsistencies['trial_null_formal_assigned']
        
        if not to_fix:
            print("没有需要修复的记录")
            return
        
        if dry_run:
            print("（演示模式 - 不会实际修改数据）\n")
        
        fixed_count = 0
        for item in to_fix:
            trial = item['trial']
            formal = item['formal']
            
            print(f"修复试听课 ID {trial.id}:")
            print(f"  设置负责员工为: {item['formal_employee']}")
            
            if not dry_run:
                trial.assigned_employee_id = formal.assigned_employee_id
                fixed_count += 1
                print("  ✅ 已更新")
            else:
                print("  🔍 演示模式，未实际更新")
        
        if not dry_run and fixed_count > 0:
            db.session.commit()
            print(f"\n✅ 成功修复 {fixed_count} 条记录")
        elif dry_run:
            print(f"\n共需要修复 {len(to_fix)} 条记录")
            print("执行实际修复: python fix_historical_assignments.py --fix")


def fix_strategy_2(dry_run=True):
    """
    修复策略2：统一设置
    为所有不一致的情况统一设置员工
    """
    # 这个策略更激进，一般不推荐
    pass


def main():
    import sys
    
    if '--fix' in sys.argv:
        # 实际执行修复
        fix_strategy_1(dry_run=False)
    elif '--analyze' in sys.argv:
        # 只分析不修复
        inconsistencies = analyze_inconsistencies()
        show_detailed_inconsistencies(inconsistencies)
    else:
        # 默认：分析并演示修复
        inconsistencies = analyze_inconsistencies()
        show_detailed_inconsistencies(inconsistencies)
        
        if inconsistencies['trial_null_formal_assigned']:
            print("\n" + "="*50)
            fix_strategy_1(dry_run=True)
            
        print("\n" + "="*50)
        print("\n使用说明:")
        print("1. 分析详情: python fix_historical_assignments.py --analyze")
        print("2. 执行修复: python fix_historical_assignments.py --fix")
        print("3. 修复后，员工分配功能将正常工作")


if __name__ == '__main__':
    main()