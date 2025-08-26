"""
深入分析袁文的课程记录，找到需要删除的课程
"""

from app import create_app, db
from app.models import Course, Employee, Customer
from datetime import datetime

app = create_app()

def analyze_courses():
    """分析袁文的所有课程"""
    with app.app_context():
        print("=== 深入分析袁文的课程记录 ===\n")
        
        # 1. 查找袁文员工
        yuanwen = Employee.query.filter_by(name='袁文').first()
        if not yuanwen:
            print("未找到名为'袁文'的员工")
            return
        
        print(f"找到员工: {yuanwen.name} (ID: {yuanwen.id})")
        
        # 2. 查找所有相关课程
        all_courses = Course.query.filter_by(
            assigned_employee_id=yuanwen.id
        ).all()
        
        print(f"\n袁文共有 {len(all_courses)} 个课程记录")
        
        # 3. 分类统计
        trial_courses = [c for c in all_courses if c.is_trial]
        formal_courses = [c for c in all_courses if not c.is_trial]
        
        print(f"- 试听课: {len(trial_courses)} 个")
        print(f"- 正式课: {len(formal_courses)} 个")
        
        # 4. 查找可能的目标记录（使用模糊匹配）
        print("\n\n=== 查找可能的目标记录 ===")
        print("目标1: 花花小姐, 单词课, 20节, ¥3160")
        print("目标2: 刘, 单词课, 30节, ¥4740")
        
        possible_matches = []
        
        for course in formal_courses:
            if not course.customer:
                continue
                
            total_amount = (course.sessions or 0) * (course.price or 0)
            
            # 检查是否可能是花花小姐的课程
            if ('花' in course.customer.name or '小姐' in course.customer.name):
                if abs(total_amount - 3160) < 100:  # 允许100元误差
                    possible_matches.append(('可能是花花小姐', course, 1))
            
            # 检查是否可能是刘的课程
            if '刘' in course.customer.name:
                if abs(total_amount - 4740) < 100:  # 允许100元误差
                    possible_matches.append(('可能是刘', course, 2))
            
            # 检查金额完全匹配的
            if abs(total_amount - 3160) < 1:
                possible_matches.append(('金额匹配3160', course, 1))
            elif abs(total_amount - 4740) < 1:
                possible_matches.append(('金额匹配4740', course, 2))
        
        # 5. 显示所有正式课程详情
        print("\n\n=== 所有正式课程列表 ===")
        print("-" * 120)
        print(f"{'ID':>6} | {'客户名':>15} | {'课程类型':>10} | {'节数':>6} | {'单价':>8} | {'总金额':>10} | {'是否续课':>8} | {'创建日期':>12}")
        print("-" * 120)
        
        for course in sorted(formal_courses, key=lambda x: x.created_at or datetime.min):
            if course.customer:
                total = (course.sessions or 0) * (course.price or 0)
                created_date = course.created_at.strftime('%Y-%m-%d') if course.created_at else 'N/A'
                is_renewal = '是' if course.renewal_from_course_id else '否'
                
                # 高亮显示可能的目标
                highlight = ''
                if any(c[1].id == course.id for c in possible_matches):
                    highlight = ' ⭐'
                
                print(f"{course.id:>6} | {course.customer.name[:15]:>15} | "
                      f"{(course.course_type or 'N/A')[:10]:>10} | "
                      f"{course.sessions or 0:>6} | ¥{course.price or 0:>7.2f} | "
                      f"¥{total:>9.2f} | {is_renewal:>8} | {created_date:>12}{highlight}")
        
        # 6. 显示可能的匹配
        if possible_matches:
            print(f"\n\n=== 找到 {len(possible_matches)} 个可能的匹配 ===")
            for reason, course, target_num in possible_matches:
                print(f"\n[{reason}] - 目标{target_num}")
                print(f"  课程ID: {course.id}")
                print(f"  客户: {course.customer.name}")
                print(f"  课程类型: {course.course_type}")
                print(f"  节数: {course.sessions}")
                print(f"  单价: ¥{course.price}")
                print(f"  总金额: ¥{(course.sessions or 0) * (course.price or 0)}")
                print(f"  创建时间: {course.created_at}")
                
                # 检查关联
                if course.converted_from_trial:
                    print(f"  ⚠️ 从试听课转化")
                if course.renewal_from_course_id:
                    print(f"  ⚠️ 是续课")
                
                # 检查是否有后续课程
                renewals = Course.query.filter_by(renewal_from_course_id=course.id).count()
                if renewals > 0:
                    print(f"  ⚠️ 有{renewals}个续课")
        
        return possible_matches


def safe_delete_course(course_id):
    """安全删除课程的建议"""
    with app.app_context():
        course = Course.query.get(course_id)
        if not course:
            print(f"未找到ID为 {course_id} 的课程")
            return
        
        print(f"\n=== 课程删除安全性分析 (ID: {course_id}) ===")
        print(f"客户: {course.customer.name if course.customer else 'N/A'}")
        print(f"课程: {course.course_type}, {course.sessions}节, ¥{(course.sessions or 0) * (course.price or 0)}")
        
        # 分析是否可以安全删除
        issues = []
        
        # 1. 检查试听课关联
        if course.converted_from_trial:
            trial = Course.query.get(course.converted_from_trial)
            if trial:
                issues.append(f"此课程是从试听课(ID: {trial.id})转化而来，需要先解除关联")
        
        # 2. 检查续课链
        if course.renewal_from_course_id:
            issues.append("此课程是续课，删除会破坏续课链的完整性")
        
        renewals = Course.query.filter_by(renewal_from_course_id=course.id).all()
        if renewals:
            issues.append(f"有{len(renewals)}个课程续自此课程，需要先处理这些续课")
        
        # 3. 检查退款
        if hasattr(course, 'refunds') and course.refunds:
            issues.append(f"有{len(course.refunds)}条退款记录，删除会影响财务统计")
        
        # 4. 给出建议
        if not issues:
            print("\n✅ 此课程可以安全删除")
            print("\n删除步骤：")
            print("1. 在数据库中执行: DELETE FROM course WHERE id = %d;" % course_id)
            print("2. 或使用代码: Course.query.filter_by(id=%d).delete()" % course_id)
        else:
            print("\n⚠️ 不建议直接删除此课程")
            print("\n存在的问题：")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
            
            print("\n建议方案：")
            print("1. 将课程标记为'已取消'状态（添加状态字段）")
            print("2. 或者将assigned_employee_id设为NULL（取消分配）")
            print("3. 如果确实要删除，需要先处理上述问题")


if __name__ == '__main__':
    # 分析课程
    matches = analyze_courses()
    
    # 对每个可能的匹配进行安全性分析
    if matches:
        print("\n" + "="*50)
        print("开始安全性分析...")
        
        unique_courses = []
        for _, course, _ in matches:
            if course.id not in [c.id for c in unique_courses]:
                unique_courses.append(course)
        
        for course in unique_courses:
            safe_delete_course(course.id)