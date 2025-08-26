#!/usr/bin/env python3
"""
测试员工管理功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_employee_management():
    """测试员工管理功能"""
    print("🧪 开始测试员工管理功能...")
    
    # 1. 测试获取员工列表
    print("\n1. 测试获取员工列表")
    try:
        response = requests.get(f"{BASE_URL}/api/employees")
        if response.status_code == 200:
            employees = response.json()
            print(f"✓ 成功获取 {len(employees)} 个员工")
            for emp in employees:
                print(f"  - {emp['name']} (底薪: ¥{emp.get('base_salary', 0)})")
        else:
            print(f"❌ 获取员工列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 2. 测试创建新员工
    print("\n2. 测试创建新员工")
    new_employee_data = {
        "name": "测试员工",
        "phone": "13800138000",
        "email": "test@example.com",
        "base_salary": 3000,
        "commission_type": "profit",
        "new_course_rate": 10,
        "renewal_rate": 15
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/employees",
            headers={"Content-Type": "application/json"},
            data=json.dumps(new_employee_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ 成功创建新员工")
                employee_id = result['employee']['id']
                print(f"  员工ID: {employee_id}")
                print(f"  姓名: {result['employee']['name']}")
                print(f"  底薪: ¥{result['employee']['base_salary']}")
                print(f"  提成类型: {result['employee']['commission_type']}")
                
                # 3. 测试更新员工
                print("\n3. 测试更新员工")
                update_data = {
                    "name": "测试员工(已更新)",
                    "base_salary": 3500,
                    "new_course_rate": 12
                }
                
                update_response = requests.put(
                    f"{BASE_URL}/api/employees/{employee_id}",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(update_data)
                )
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    if update_result.get('success'):
                        print("✓ 成功更新员工信息")
                        print(f"  新姓名: {update_result['employee']['name']}")
                        print(f"  新底薪: ¥{update_result['employee']['base_salary']}")
                    else:
                        print(f"❌ 更新失败: {update_result.get('message')}")
                else:
                    print(f"❌ 更新请求失败: {update_response.status_code}")
                
                # 4. 测试删除员工
                print("\n4. 测试删除员工")
                delete_response = requests.delete(f"{BASE_URL}/api/employees/{employee_id}")
                
                if delete_response.status_code == 200:
                    delete_result = delete_response.json()
                    if delete_result.get('success'):
                        print("✓ 成功删除员工")
                    else:
                        print(f"❌ 删除失败: {delete_result.get('message')}")
                else:
                    print(f"❌ 删除请求失败: {delete_response.status_code}")
                
            else:
                print(f"❌ 创建失败: {result.get('message')}")
        else:
            print(f"❌ 创建请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 5. 测试系统配置页面
    print("\n5. 测试系统配置页面")
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            print("✓ 系统配置页面可访问")
            if "员工管理" in response.text:
                print("✓ 员工管理模块已集成到系统配置页面")
            else:
                print("❌ 员工管理模块未找到")
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_employee_management()

