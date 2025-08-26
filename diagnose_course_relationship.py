"""
诊断试听课和正课的关系异常
查找1个试听课对应多个正课的情况
"""

from app import create_app, db
from app.models import Employee, Course, Customer
from collections import defaultdict

app = create_app()

with app.app_context():
    print("=== 试听课-正课关系异常诊断 ===\n")
    
    # 1. 查找所有试听课
    trial_courses = Course.query.filter_by(is_trial=True).all()
    
    # 2. 分析每个试听课的转化情况
    print("1. 试听课转化分析：")
    print("-" * 80)
    
    for trial in trial_courses:
        # 查找声称从这个试听课转化的所有正课
        formal_courses_from_trial = Course.query.filter_by(
            converted_from_trial=trial.id,
            is_trial=False
        ).all()
        
        if len(formal_courses_from_trial) > 1:
            print(f"\n⚠️  异常发现：试听课ID {trial.id} 对应了 {len(formal_courses_from_trial)} 个正课！")
            print(f"   试听课信息：")
            print(f"   - 客户：{trial.customer.name if trial.customer else '未知'}")
            print(f"   - 分配员工ID：{trial.assigned_employee_id}")
            print(f"   - 创建时间：{trial.created_at}")
            print(f"   - converted_to_course字段值：{trial.converted_to_course}")
            
            print(f"\n   对应的正课：")
            for fc in formal_courses_from_trial:
                print(f"   - 正课ID：{fc.id}")
                print(f"     客户：{fc.customer.name if fc.customer else '未知'}")
                print(f"     分配员工ID：{fc.assigned_employee_id}")
                print(f"     课程类型：{fc.course_type}")
                print(f"     是否续课：{fc.is_renewal}")
                print(f"     创建时间：{fc.created_at}")
                print()
    
    # 3. 检查正课的来源一致性
    print("\n2. 正课来源一致性检查：")
    print("-" * 80)
    
    formal_courses = Course.query.filter_by(is_trial=False).all()
    for formal in formal_courses:
        if formal.converted_from_trial:
            # 检查对应的试听课是否指向这个正课
            trial = Course.query.get(formal.converted_from_trial)
            if trial:
                if trial.converted_to_course != formal.id:
                    print(f"\n⚠️  数据不一致：")
                    print(f"   正课ID {formal.id} 声称来自试听课ID {formal.converted_from_trial}")
                    print(f"   但试听课ID {trial.id} 的converted_to_course字段指向：{trial.converted_to_course}")
    
    # 4. 按员工统计异常数据
    print("\n3. 按员工统计课程数据：")
    print("-" * 80)
    
    employees = Employee.query.all()
    for emp in employees:
        trials = Course.query.filter_by(assigned_employee_id=emp.id, is_trial=True).all()
        formals = Course.query.filter_by(assigned_employee_id=emp.id, is_trial=False).all()
        
        # 统计转化来源
        converted_count = 0
        direct_count = 0
        for formal in formals:
            if formal.converted_from_trial:
                # 检查试听课是否也分配给同一员工
                trial = Course.query.get(formal.converted_from_trial)
                if trial and trial.assigned_employee_id == emp.id:
                    converted_count += 1
                else:
                    print(f"\n⚠️  跨员工转化：正课ID {formal.id} 来自其他员工的试听课")
            else:
                direct_count += 1
        
        print(f"\n员工：{emp.name} (ID: {emp.id})")
        print(f"  试听课：{len(trials)} 个")
        print(f"  正课总数：{len(formals)} 个")
        print(f"    - 从自己的试听课转化：{converted_count} 个")
        print(f"    - 直接分配（无试听）：{direct_count} 个")
        print(f"    - 其他来源：{len(formals) - converted_count - direct_count} 个")
    
    # 5. 查找可能的数据录入错误
    print("\n\n4. 可能的数据录入错误：")
    print("-" * 80)
    
    # 查找同一客户的多个正课
    customer_courses = defaultdict(list)
    for formal in formal_courses:
        if formal.customer_id:
            customer_courses[formal.customer_id].append(formal)
    
    for customer_id, courses in customer_courses.items():
        if len(courses) > 1:
            customer = Customer.query.get(customer_id)
            print(f"\n客户 {customer.name} 有 {len(courses)} 个正课：")
            for course in courses:
                print(f"  - 正课ID：{course.id}, 员工ID：{course.assigned_employee_id}, "
                      f"来自试听：{course.converted_from_trial}, 是否续课：{course.is_renewal}")
    
    print("\n\n=== 分析结论 ===")
    print("可能的原因：")
    print("1. 数据录入错误：多个正课错误地指向了同一个试听课")
    print("2. 续课处理不当：续课可能被错误地标记为从试听课转化")
    print("3. 数据导入问题：批量导入时关联关系设置错误")
    print("4. 程序逻辑错误：转化时没有正确更新关联字段")