"""
测试员工业绩API的错误
"""

from app import create_app
from app.services import PerformanceService

app = create_app()

with app.app_context():
    try:
        # 模拟API调用
        employee_id = 2
        start_date = None
        end_date = None
        
        print(f"测试员工ID {employee_id} 的业绩数据获取...")
        
        # 调用服务层
        performance = PerformanceService.calculate_employee_performance(
            employee_id, start_date, end_date
        )
        
        print("成功获取业绩数据：")
        print(f"- 员工信息: {performance.get('employee', {})}")
        print(f"- 试听课统计: {performance.get('trial_courses', {})}")
        print(f"- 正课统计: {performance.get('formal_courses', {})}")
        print(f"- 转化统计: {performance.get('conversion', {})}")
        print(f"- 提成信息: {performance.get('commission', {})}")
        
    except Exception as e:
        print(f"错误发生: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()