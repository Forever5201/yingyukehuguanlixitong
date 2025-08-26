"""
修复试听课-正课关系异常
查找并修复1个试听课对应多个正课的问题
"""

from app import create_app, db
from app.models import Course
import sys

app = create_app()

def fix_course_relationships(dry_run=True):
    """
    修复课程关系异常
    
    Args:
        dry_run: 如果为True，只显示问题不修复；如果为False，执行修复
    """
    with app.app_context():
        print("=== 检查试听课-正课关系异常 ===\n")
        
        issues_found = []
        
        # 1. 查找所有试听课
        trial_courses = Course.query.filter_by(is_trial=True).all()
        
        for trial in trial_courses:
            # 查找声称从这个试听课转化的所有正课
            formal_courses_from_trial = Course.query.filter_by(
                converted_from_trial=trial.id,
                is_trial=False
            ).order_by(Course.created_at).all()  # 按创建时间排序
            
            if len(formal_courses_from_trial) > 1:
                print(f"⚠️  发现异常：试听课ID {trial.id} 对应了 {len(formal_courses_from_trial)} 个正课")
                print(f"   客户：{trial.customer.name if trial.customer else '未知'}")
                
                # 第一个（最早的）是真正的转化
                valid_formal = formal_courses_from_trial[0]
                print(f"   ✓ 保留：正课ID {valid_formal.id} (创建于 {valid_formal.created_at})")
                
                # 其余的需要修正
                for formal in formal_courses_from_trial[1:]:
                    print(f"   ✗ 需要修正：正课ID {formal.id} (创建于 {formal.created_at})")
                    issues_found.append({
                        'trial_id': trial.id,
                        'formal_id': formal.id,
                        'action': 'clear_converted_from_trial'
                    })
        
        # 2. 检查试听课的converted_to_course字段
        print("\n检查试听课的converted_to_course字段...")
        for trial in trial_courses:
            if trial.converted_to_course:
                # 验证对应的正课是否存在且指向这个试听课
                formal = Course.query.get(trial.converted_to_course)
                if not formal:
                    print(f"⚠️  试听课ID {trial.id} 指向不存在的正课ID {trial.converted_to_course}")
                    issues_found.append({
                        'trial_id': trial.id,
                        'action': 'clear_converted_to_course'
                    })
                elif formal.converted_from_trial != trial.id:
                    print(f"⚠️  数据不一致：试听课ID {trial.id} 指向正课ID {formal.id}，"
                          f"但正课指向试听课ID {formal.converted_from_trial}")
                    # 以正课的指向为准
                    issues_found.append({
                        'trial_id': trial.id,
                        'action': 'clear_converted_to_course'
                    })
        
        # 显示统计
        print(f"\n总共发现 {len(issues_found)} 个问题")
        
        if not dry_run and issues_found:
            print("\n开始修复...")
            fixed_count = 0
            
            try:
                for issue in issues_found:
                    if issue['action'] == 'clear_converted_from_trial':
                        # 清除错误的converted_from_trial
                        formal = Course.query.get(issue['formal_id'])
                        if formal:
                            print(f"修复：清除正课ID {formal.id} 的converted_from_trial字段")
                            formal.converted_from_trial = None
                            fixed_count += 1
                    
                    elif issue['action'] == 'clear_converted_to_course':
                        # 清除错误的converted_to_course
                        trial = Course.query.get(issue['trial_id'])
                        if trial:
                            print(f"修复：清除试听课ID {trial.id} 的converted_to_course字段")
                            trial.converted_to_course = None
                            # 如果状态是converted，改为completed
                            if trial.trial_status == 'converted':
                                trial.trial_status = 'completed'
                            fixed_count += 1
                
                db.session.commit()
                print(f"\n✅ 成功修复 {fixed_count} 个问题")
                
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 修复失败：{str(e)}")
                return False
        
        elif dry_run and issues_found:
            print("\n这是预览模式，未执行实际修复")
            print("运行 'python fix_course_relationships.py --fix' 来执行修复")
        
        else:
            print("\n✅ 没有发现需要修复的问题")
        
        return True


if __name__ == '__main__':
    # 检查命令行参数
    dry_run = '--fix' not in sys.argv
    
    if dry_run:
        print("=== 预览模式 ===")
        print("将只显示问题，不会修改数据\n")
    else:
        print("=== 修复模式 ===")
        print("将修复发现的问题\n")
        response = input("确定要修复吗？(yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            sys.exit(0)
    
    fix_course_relationships(dry_run)