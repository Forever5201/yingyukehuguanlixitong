"""
分析课程关系，找出独立创建的正课
"""

from app import create_app, db
from app.models import Course, Employee, Customer

app = create_app()

def analyze_independent_courses():
    """分析独立创建的正课（不是从试听课转化来的）"""
    with app.app_context():
        print("=== 分析课程关系 ===\n")
        
        # 1. 查找所有正课
        formal_courses = Course.query.filter_by(is_trial=False).all()
        
        independent_courses = []
        converted_courses = []
        
        for course in formal_courses:
            if course.converted_from_trial:
                converted_courses.append(course)
            else:
                independent_courses.append(course)
        
        print(f"总共找到 {len(formal_courses)} 个正课")
        print(f"- 从试听课转化: {len(converted_courses)} 个")
        print(f"- 独立创建: {len(independent_courses)} 个")
        
        # 2. 显示独立创建的正课详情
        if independent_courses:
            print("\n\n=== 独立创建的正课（这些不会跟随试听课变化）===")
            print("-" * 100)
            print(f"{'ID':>6} | {'客户':>15} | {'课程类型':>10} | {'负责员工':>15} | {'创建时间':>20}")
            print("-" * 100)
            
            for course in independent_courses:
                customer_name = course.customer.name if course.customer else "未知"
                employee_name = course.assigned_employee.name if course.assigned_employee else "未分配"
                created_at = course.created_at.strftime('%Y-%m-%d %H:%M') if course.created_at else "未知"
                
                print(f"{course.id:>6} | {customer_name:>15} | {course.course_type or 'N/A':>10} | "
                      f"{employee_name:>15} | {created_at:>20}")
        
        # 3. 分析每个客户的课程情况
        print("\n\n=== 按客户分析课程情况 ===")
        
        # 获取所有有课程的客户
        customers_with_courses = set()
        for course in Course.query.all():
            if course.customer_id:
                customers_with_courses.add(course.customer_id)
        
        for customer_id in customers_with_courses:
            customer = Customer.query.get(customer_id)
            if not customer:
                continue
                
            # 获取该客户的所有课程
            customer_courses = Course.query.filter_by(customer_id=customer_id).all()
            trial_courses = [c for c in customer_courses if c.is_trial]
            formal_courses = [c for c in customer_courses if not c.is_trial]
            
            if len(formal_courses) > 0:
                print(f"\n客户: {customer.name}")
                print(f"  试听课: {len(trial_courses)} 个")
                print(f"  正课: {len(formal_courses)} 个")
                
                # 检查是否有独立创建的正课
                independent_count = sum(1 for c in formal_courses if not c.converted_from_trial)
                if independent_count > 0:
                    print(f"  ⚠️ 有 {independent_count} 个正课是独立创建的，不会跟随试听课变化")
                    
                    # 显示详情
                    for course in formal_courses:
                        if not course.converted_from_trial:
                            employee_name = course.assigned_employee.name if course.assigned_employee else "未分配"
                            print(f"    - 正课ID {course.id}: {course.course_type}, 负责员工: {employee_name}")
        
        return independent_courses


def find_problematic_scenario():
    """查找问题场景：同一客户既有试听课又有独立的正课"""
    with app.app_context():
        print("\n\n=== 查找问题场景 ===")
        
        problematic_customers = []
        
        customers = Customer.query.all()
        for customer in customers:
            courses = Course.query.filter_by(customer_id=customer.id).all()
            
            has_trial = any(c.is_trial for c in courses)
            has_independent_formal = any(not c.is_trial and not c.converted_from_trial for c in courses)
            
            if has_trial and has_independent_formal:
                problematic_customers.append({
                    'customer': customer,
                    'trial_courses': [c for c in courses if c.is_trial],
                    'independent_formals': [c for c in courses if not c.is_trial and not c.converted_from_trial],
                    'converted_formals': [c for c in courses if not c.is_trial and c.converted_from_trial]
                })
        
        if problematic_customers:
            print(f"\n发现 {len(problematic_customers)} 个客户存在问题场景：")
            print("（既有试听课，又有独立创建的正课）\n")
            
            for item in problematic_customers:
                customer = item['customer']
                print(f"\n客户: {customer.name}")
                
                # 试听课
                for trial in item['trial_courses']:
                    employee_name = trial.assigned_employee.name if trial.assigned_employee else "未分配"
                    print(f"  试听课 ID {trial.id}: 负责员工={employee_name}")
                
                # 独立的正课
                print("  独立创建的正课（不会跟随试听课）:")
                for formal in item['independent_formals']:
                    employee_name = formal.assigned_employee.name if formal.assigned_employee else "未分配"
                    print(f"    - ID {formal.id}: {formal.course_type}, 负责员工={employee_name}")
                
                # 转化的正课
                if item['converted_formals']:
                    print("  从试听课转化的正课（会跟随试听课）:")
                    for formal in item['converted_formals']:
                        employee_name = formal.assigned_employee.name if formal.assigned_employee else "未分配"
                        print(f"    - ID {formal.id}: {formal.course_type}, 负责员工={employee_name}")
        
        return problematic_customers


if __name__ == '__main__':
    # 分析独立课程
    independent_courses = analyze_independent_courses()
    
    # 查找问题场景
    problematic = find_problematic_scenario()
    
    if problematic:
        print("\n" + "="*50)
        print("\n解决方案：")
        print("1. 这些独立创建的正课需要手动建立与试听课的关联")
        print("2. 或者单独管理这些正课的员工分配")
        print("3. 可以考虑添加一个功能：将独立的正课关联到试听课")