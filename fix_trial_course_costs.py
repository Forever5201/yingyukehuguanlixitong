import os
import sys
from datetime import datetime

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Course, Config

def fix_trial_course_costs():
    """
    修复数据库中存量的试听课成本数据。
    旧逻辑错误地将手续费计入了 course.cost 字段。
    此脚本将重新计算并修正成本为正确的基础成本。
    """
    app = create_app()
    with app.app_context():
        print("开始修复试听课成本数据...")

        # 1. 获取淘宝手续费率配置
        taobao_fee_rate_config = Config.query.filter_by(key='taobao_fee_rate').first()
        if taobao_fee_rate_config and taobao_fee_rate_config.value:
            try:
                taobao_fee_rate = float(taobao_fee_rate_config.value) / 100.0
            except (ValueError, TypeError):
                print("错误：淘宝手续费率配置无效，将使用默认值 0.006。")
                taobao_fee_rate = 0.006
        else:
            print("警告：未找到淘宝手续费率配置，将使用默认值 0.006。")
            taobao_fee_rate = 0.006
        print(f"使用的淘宝手续费率: {taobao_fee_rate:.4f}")

        # 2. 获取基础试听课成本
        base_trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(base_trial_cost_config.value) if base_trial_cost_config and base_trial_cost_config.value else 40.0 # 提供一个合理的默认值
        print(f"使用的基础试听课成本: {base_trial_cost}")

        # 3. 查询所有试听课
        trial_courses = Course.query.filter_by(is_trial=True).all()
        print(f"找到 {len(trial_courses)} 条试听课记录需要检查。")

        fixed_count = 0
        for course in trial_courses:
            # 确定正确的成本应该是多少
            if course.custom_trial_cost is not None:
                correct_cost = course.custom_trial_cost
            else:
                correct_cost = base_trial_cost

            # 只有在当前成本与正确成本差异较大时才进行修复
            if abs(course.cost - correct_cost) > 0.01:
                print(f"  - 课程ID: {course.id}")
                print(f"    原始成本: {course.cost:.4f}, 修正为 -> {correct_cost:.4f}")
                
                course.cost = correct_cost
                fixed_count += 1

        # 4. 提交数据库变更
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"\n成功修复了 {fixed_count} 条试听课的成本数据。")
            except Exception as e:
                db.session.rollback()
                print(f"\n数据库提交失败: {e}")
        else:
            print("\n没有需要修复的数据。")

if __name__ == '__main__':
    fix_trial_course_costs()

