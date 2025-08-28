"""
检查试听课 ID 1 的状态和关联情况
"""

from app import create_app, db
from app.models import Course, Employee

app = create_app()

def check_course_status(course_id):
    """检查课程的详细状态"""
    with app.app_context():
        print(f"=== 检查课程 ID {course_id} 的状态 ===\n")
        
        # 查找试听课
        trial = Course.query.get(course_id)
        if not trial:
            print(f"未找到课程 ID {course_id}")
            return
        
        if not trial.is_trial:
            print(f"课程 ID {course_id} 不是试听课")
            return
        
        print("试听课信息:")
        print(f"  - ID: {trial.id}")
        print(f"  - 客户: {trial.customer.name if trial.customer else '未知'}")
        print(f"  - 当前负责员工: {trial.assigned_employee.name if trial.assigned_employee else '未分配'}")
        print(f"  - 员工ID: {trial.assigned_employee_id}")
        print(f"  - 创建时间: {trial.created_at}")
        
        # 检查是否转化
        if trial.converted_to_course:
            print(f"\n已转化为正课 ID: {trial.converted_to_course}")
            
            # 查找正课
            formal = Course.query.get(trial.converted_to_course)
            if formal:
                print("\n正课信息:")
                print(f"  - ID: {formal.id}")
                print(f"  - 客户: {formal.customer.name if formal.customer else '未知'}")
                print(f"  - 负责员工: {formal.assigned_employee.name if formal.assigned_employee else '未分配'}")
                print(f"  - 员工ID: {formal.assigned_employee_id}")
                print(f"  - 课程类型: {formal.course_type}")
                print(f"  - 节数: {formal.sessions}")
                print(f"  - 创建时间: {formal.created_at}")
                
                # 检查是否一致
                if trial.assigned_employee_id != formal.assigned_employee_id:
                    print(f"\n⚠️ 发现不一致！")
                    print(f"  试听课员工ID: {trial.assigned_employee_id}")
                    print(f"  正课员工ID: {formal.assigned_employee_id}")
                    
                    # 这就是导致409冲突的原因
                    if formal.assigned_employee_id is not None:
                        print(f"\n这会导致409冲突的情况：")
                        print(f"  1. 试听课要分配给新员工")
                        print(f"  2. 但正课已经分配给了 {formal.assigned_employee.name}")
                        print(f"  3. 系统会提示用户确认是否统一更新")
                else:
                    print(f"\n✅ 员工分配一致")
                
                # 检查续课
                renewals = Course.query.filter_by(
                    renewal_from_course_id=formal.id
                ).all()
                
                if renewals:
                    print(f"\n续课情况:")
                    for i, renewal in enumerate(renewals, 1):
                        print(f"  续课{i} ID {renewal.id}: {renewal.assigned_employee.name if renewal.assigned_employee else '未分配'}")
        else:
            print("\n尚未转化为正课")
        
        print("\n" + "="*50)
        print("\n可能的操作场景：")
        print("1. 之前运行了 fix_historical_assignments.py --fix")
        print("   将试听课的员工更新为与正课一致（都是袁文）")
        print("2. 现在尝试将试听课分配给其他员工")
        print("3. 系统检测到正课已经有员工，返回409冲突")
        print("4. 这是正常的保护机制，确保数据一致性")


if __name__ == '__main__':
    check_course_status(1)