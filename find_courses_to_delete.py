"""
查找袁文员工下的特定课程记录
"""

from app import create_app, db
from app.models import Course, Employee, Customer
from datetime import datetime

app = create_app()

def find_yuanwen_courses():
    """查找袁文的特定课程"""
    with app.app_context():
        print("=== 查找袁文的课程记录 ===\n")
        
        # 1. 查找袁文员工
        yuanwen = Employee.query.filter_by(name='袁文').first()
        if not yuanwen:
            print("未找到名为'袁文'的员工")
            return
        
        print(f"找到员工: {yuanwen.name} (ID: {yuanwen.id})")
        
        # 2. 查找袁文的所有正课
        formal_courses = Course.query.filter_by(
            assigned_employee_id=yuanwen.id,
            is_trial=False
        ).all()
        
        print(f"\n袁文共有 {len(formal_courses)} 个正课记录:\n")
        
        # 3. 查找特定的两条记录
        target_courses = []
        
        for course in formal_courses:
            if course.customer:
                # 计算总金额
                total_amount = (course.sessions or 0) * (course.price or 0)
                
                # 检查是否是目标记录
                if (course.customer.name == '花花小姐' and 
                    course.course_type == '单词课' and 
                    course.sessions == 20 and 
                    abs(total_amount - 3160) < 1):
                    target_courses.append(('花花小姐', course))
                    
                elif (course.customer.name == '刘' and 
                      course.course_type == '单词课' and 
                      course.sessions == 30 and 
                      abs(total_amount - 4740) < 1):
                    target_courses.append(('刘', course))
        
        # 4. 显示所有正课（用于调试）
        print("所有正课列表:")
        print("-" * 100)
        print(f"{'ID':>6} | {'客户名':>10} | {'课程类型':>10} | {'节数':>6} | {'单价':>8} | {'总金额':>10} | {'创建日期':>12}")
        print("-" * 100)
        
        for course in formal_courses:
            if course.customer:
                total = (course.sessions or 0) * (course.price or 0)
                created_date = course.created_at.strftime('%Y-%m-%d') if course.created_at else 'N/A'
                print(f"{course.id:>6} | {course.customer.name:>10} | {course.course_type or 'N/A':>10} | "
                      f"{course.sessions or 0:>6} | ¥{course.price or 0:>7.2f} | ¥{total:>9.2f} | {created_date:>12}")
        
        # 5. 显示找到的目标记录
        if target_courses:
            print(f"\n\n找到 {len(target_courses)} 条目标记录:")
            print("=" * 50)
            for customer_name, course in target_courses:
                print(f"\n客户: {customer_name}")
                print(f"课程ID: {course.id}")
                print(f"课程类型: {course.course_type}")
                print(f"节数: {course.sessions}")
                print(f"单价: ¥{course.price}")
                print(f"总金额: ¥{course.sessions * course.price}")
                print(f"创建时间: {course.created_at}")
                
                # 检查是否有关联
                if course.converted_from_trial:
                    print(f"⚠️ 此课程是从试听课(ID: {course.converted_from_trial})转化而来")
                if course.renewal_from_course_id:
                    print(f"⚠️ 此课程是续课，续自课程ID: {course.renewal_from_course_id}")
                    
                # 检查是否有续课
                renewals = Course.query.filter_by(
                    renewal_from_course_id=course.id
                ).count()
                if renewals > 0:
                    print(f"⚠️ 此课程有 {renewals} 个续课")
                
                # 检查是否有退款
                if course.refunds:
                    print(f"⚠️ 此课程有 {len(course.refunds)} 条退款记录")
        else:
            print("\n未找到符合条件的目标记录")
            print("\n可能原因：")
            print("1. 客户名称不完全匹配")
            print("2. 金额计算有差异")
            print("3. 课程类型不同")
            print("4. 这些课程可能已被删除或修改")
        
        return target_courses


def check_course_dependencies(course_id):
    """检查课程的依赖关系"""
    with app.app_context():
        course = Course.query.get(course_id)
        if not course:
            print(f"未找到ID为 {course_id} 的课程")
            return
        
        print(f"\n=== 课程 ID {course_id} 的依赖关系检查 ===")
        
        # 1. 是否从试听课转化
        if course.converted_from_trial:
            trial = Course.query.get(course.converted_from_trial)
            if trial:
                print(f"- 从试听课转化 (ID: {trial.id}, 客户: {trial.customer.name if trial.customer else 'N/A'})")
        
        # 2. 是否是续课
        if course.renewal_from_course_id:
            parent = Course.query.get(course.renewal_from_course_id)
            if parent:
                print(f"- 是续课，续自 (ID: {parent.id}, 客户: {parent.customer.name if parent.customer else 'N/A'})")
        
        # 3. 是否有续课
        renewals = Course.query.filter_by(renewal_from_course_id=course.id).all()
        if renewals:
            print(f"- 有 {len(renewals)} 个续课:")
            for renewal in renewals:
                print(f"  * ID: {renewal.id}, 节数: {renewal.sessions}, 金额: ¥{(renewal.sessions or 0) * (renewal.price or 0)}")
        
        # 4. 是否有退款
        if course.refunds:
            print(f"- 有 {len(course.refunds)} 条退款记录:")
            for refund in course.refunds:
                print(f"  * 退款金额: ¥{refund.refund_amount}, 时间: {refund.created_at}")
        
        # 5. 判断是否可以安全删除
        can_delete = True
        reasons = []
        
        if course.renewal_from_course_id:
            can_delete = False
            reasons.append("这是一个续课，删除可能影响续课链的完整性")
        
        if renewals:
            can_delete = False
            reasons.append(f"有 {len(renewals)} 个续课依赖此课程")
        
        if course.refunds:
            can_delete = False
            reasons.append("有退款记录，删除会影响财务数据")
        
        print(f"\n删除建议: {'⚠️ 不建议删除' if not can_delete else '✅ 可以删除'}")
        if reasons:
            print("原因:")
            for reason in reasons:
                print(f"- {reason}")


if __name__ == '__main__':
    # 查找课程
    target_courses = find_yuanwen_courses()
    
    # 如果找到了，检查依赖关系
    if target_courses:
        print("\n" + "="*50)
        print("正在检查这些课程的依赖关系...")
        for _, course in target_courses:
            check_course_dependencies(course.id)