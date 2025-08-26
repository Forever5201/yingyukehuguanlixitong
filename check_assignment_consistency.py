"""
检查和修复试听课与正课的员工分配一致性
"""

from app import create_app, db
from app.models import Course, Employee

app = create_app()

def check_assignment_consistency():
    """检查试听课和正课的员工分配是否一致"""
    with app.app_context():
        print("=== 检查试听课与正课的员工分配一致性 ===\n")
        
        inconsistent_cases = []
        
        # 1. 查找所有已转化的试听课
        trial_courses = Course.query.filter(
            Course.is_trial == True,
            Course.converted_to_course != None
        ).all()
        
        print(f"找到 {len(trial_courses)} 个已转化的试听课\n")
        
        # 2. 检查每个试听课与其正课的员工分配
        for trial in trial_courses:
            formal = Course.query.get(trial.converted_to_course)
            if not formal:
                print(f"⚠️ 试听课 ID {trial.id} 的转化正课 ID {trial.converted_to_course} 不存在")
                continue
            
            # 检查员工分配是否一致
            if trial.assigned_employee_id != formal.assigned_employee_id:
                inconsistent_cases.append({
                    'trial': trial,
                    'formal': formal,
                    'trial_employee': trial.assigned_employee.name if trial.assigned_employee else "未分配",
                    'formal_employee': formal.assigned_employee.name if formal.assigned_employee else "未分配"
                })
        
        # 3. 显示不一致的情况
        if inconsistent_cases:
            print(f"发现 {len(inconsistent_cases)} 个不一致的情况：\n")
            print("-" * 100)
            print(f"{'试听课ID':>10} | {'客户':>15} | {'试听课员工':>15} | {'正课ID':>10} | {'正课员工':>15}")
            print("-" * 100)
            
            for case in inconsistent_cases:
                trial = case['trial']
                formal = case['formal']
                customer_name = trial.customer.name if trial.customer else "未知"
                
                print(f"{trial.id:>10} | {customer_name:>15} | {case['trial_employee']:>15} | "
                      f"{formal.id:>10} | {case['formal_employee']:>15}")
                
                # 检查续课
                renewals = Course.query.filter_by(
                    renewal_from_course_id=formal.id,
                    is_trial=False
                ).all()
                
                if renewals:
                    print(f"           └─ 此正课还有 {len(renewals)} 个续课")
                    for renewal in renewals:
                        renewal_employee = renewal.assigned_employee.name if renewal.assigned_employee else "未分配"
                        print(f"              续课 ID {renewal.id}: {renewal_employee}")
        else:
            print("✅ 所有试听课与正课的员工分配都是一致的")
        
        return inconsistent_cases


def fix_assignment_consistency(dry_run=True):
    """修复不一致的员工分配"""
    with app.app_context():
        inconsistent_cases = check_assignment_consistency()
        
        if not inconsistent_cases:
            return
        
        print("\n\n=== 修复方案 ===")
        print("规则：以正课的员工分配为准，更新试听课的员工分配\n")
        
        if dry_run:
            print("（演示模式 - 不会实际修改数据）\n")
        
        fixed_count = 0
        
        for case in inconsistent_cases:
            trial = case['trial']
            formal = case['formal']
            
            print(f"\n处理试听课 ID {trial.id}:")
            print(f"  当前：{case['trial_employee']} → 目标：{case['formal_employee']}")
            
            if not dry_run:
                # 更新试听课的员工分配
                trial.assigned_employee_id = formal.assigned_employee_id
                fixed_count += 1
                print("  ✅ 已更新")
            else:
                print("  🔍 演示模式，未实际更新")
        
        if not dry_run and fixed_count > 0:
            db.session.commit()
            print(f"\n✅ 成功修复 {fixed_count} 个不一致的记录")
        elif dry_run:
            print(f"\n💡 如需实际修复，请运行: fix_assignment_consistency(dry_run=False)")


def check_specific_course(course_id):
    """检查特定课程的分配情况"""
    with app.app_context():
        course = Course.query.get(course_id)
        if not course:
            print(f"未找到 ID 为 {course_id} 的课程")
            return
        
        print(f"\n=== 课程 ID {course_id} 的详细信息 ===")
        print(f"客户: {course.customer.name if course.customer else '未知'}")
        print(f"类型: {'试听课' if course.is_trial else '正课'}")
        print(f"负责员工: {course.assigned_employee.name if course.assigned_employee else '未分配'}")
        
        if course.is_trial and course.converted_to_course:
            formal = Course.query.get(course.converted_to_course)
            if formal:
                print(f"\n关联的正课 ID: {formal.id}")
                print(f"正课负责员工: {formal.assigned_employee.name if formal.assigned_employee else '未分配'}")
                
                if course.assigned_employee_id != formal.assigned_employee_id:
                    print("\n⚠️ 发现不一致！试听课和正课的负责员工不同")
        
        elif not course.is_trial and course.converted_from_trial:
            trial = Course.query.get(course.converted_from_trial)
            if trial:
                print(f"\n来源试听课 ID: {trial.id}")
                print(f"试听课负责员工: {trial.assigned_employee.name if trial.assigned_employee else '未分配'}")
                
                if course.assigned_employee_id != trial.assigned_employee_id:
                    print("\n⚠️ 发现不一致！试听课和正课的负责员工不同")


if __name__ == '__main__':
    # 检查一致性
    print("正在检查数据一致性...\n")
    inconsistent_cases = check_assignment_consistency()
    
    if inconsistent_cases:
        print("\n" + "="*50)
        print("发现数据不一致！")
        print("\n运行以下命令查看具体课程：")
        print("  python -c \"from check_assignment_consistency import check_specific_course; check_specific_course(13)\"")
        print("\n运行以下命令修复（演示）：")
        print("  python -c \"from check_assignment_consistency import fix_assignment_consistency; fix_assignment_consistency(dry_run=True)\"")
        print("\n运行以下命令实际修复：")
        print("  python -c \"from check_assignment_consistency import fix_assignment_consistency; fix_assignment_consistency(dry_run=False)\"")