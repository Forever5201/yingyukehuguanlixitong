"""
测试修复后的员工业绩API
"""

from app import create_app
import json

app = create_app()

with app.test_client() as client:
    # 测试员工ID 2的业绩API
    response = client.get('/api/employees/2/performance')
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print("\nAPI响应成功!")
        print(f"员工姓名: {data.get('employee_name', '未知')}")
        print(f"试听课数量: {data.get('stats', {}).get('trial_count', 0)}")
        print(f"正课数量: {data.get('stats', {}).get('formal_count', 0)}")
        print(f"转化率: {data.get('stats', {}).get('conversion_rate', 0)}%")
        print(f"总业绩: ¥{data.get('stats', {}).get('total_revenue', 0)}")
        
        # 检查必需的字段
        required_fields = ['success', 'employee_name', 'stats', 'trial_courses', 'formal_courses', 'commission']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"\n警告: 缺少字段: {missing_fields}")
        else:
            print("\n✅ 所有必需字段都存在")
            
        # 检查提成字段
        commission = data.get('commission', {})
        commission_fields = ['new_course_commission', 'renewal_commission', 'total_commission', 'base_salary', 'total_salary']
        missing_commission = [field for field in commission_fields if field not in commission]
        
        if missing_commission:
            print(f"警告: 缺少提成字段: {missing_commission}")
        else:
            print("✅ 所有提成字段都存在")
            
    else:
        print(f"\n❌ API错误: {response.status_code}")
        error_data = response.get_json()
        print(f"错误信息: {error_data.get('message', '未知错误')}")