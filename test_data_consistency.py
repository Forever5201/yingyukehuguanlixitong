"""
测试员工课程数据一致性
检查不同查询方式下的数据差异
"""

from app import create_app, db
from app.models import Employee, Course

app = create_app()

with app.app_context():
    # 获取所有员工
    employees = Employee.query.all()
    
    print("=== 员工课程数据一致性检查 ===\n")
    
    for employee in employees:
        print(f"员工: {employee.name} (ID: {employee.id})")
        print("-" * 50)
        
        # 方式1：直接查询所有试听课
        trial_courses_all = Course.query.filter_by(
            assigned_employee_id=employee.id,
            is_trial=True
        ).all()
        print(f"试听课总数: {len(trial_courses_all)}")
        
        # 方式2：直接查询所有正课
        formal_courses_all = Course.query.filter_by(
            assigned_employee_id=employee.id,
            is_trial=False
        ).all()
        print(f"正课总数: {len(formal_courses_all)}")
        
        # 方式3：只查询通过试听转化的正课（原员工业绩页面的逻辑）
        converted_formal_courses = []
        for trial_course in trial_courses_all:
            if trial_course.converted_to_course:
                formal_course = Course.query.get(trial_course.converted_to_course)
                if formal_course and formal_course.assigned_employee_id == employee.id:
                    converted_formal_courses.append(formal_course)
        print(f"通过试听转化的正课数: {len(converted_formal_courses)}")
        
        # 方式4：查询不是通过试听转化的正课
        converted_course_ids = [c.id for c in converted_formal_courses]
        direct_formal_courses = [c for c in formal_courses_all if c.id not in converted_course_ids]
        print(f"直接分配的正课数: {len(direct_formal_courses)}")
        
        # 显示直接分配的正课详情
        if direct_formal_courses:
            print("\n直接分配的正课详情:")
            for course in direct_formal_courses:
                customer_name = course.customer.name if course.customer else "未知"
                print(f"  - 客户: {customer_name}, 类型: {course.course_type}, "
                      f"节数: {course.sessions}, 是否续课: {course.is_renewal}")
        
        print("\n")
    
    # 统计汇总
    print("=== 数据一致性分析 ===")
    print("问题原因：")
    print("1. 员工业绩页面只显示'通过试听转化的正课'")
    print("2. 删除员工API统计'所有分配给该员工的正课'")
    print("3. 可能存在直接分配的正课（未经试听转化）")
    print("4. 可能存在续课（renewal）被直接分配给员工")