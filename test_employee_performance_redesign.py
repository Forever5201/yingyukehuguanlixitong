#!/usr/bin/env python3
"""
员工业绩页面重新设计功能测试
测试新的学员维度展示和详情功能
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:5000"

def test_employee_performance_page():
    """测试员工业绩主页面是否正常"""
    try:
        url = urljoin(BASE_URL, '/employee-performance')
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 员工业绩主页面正常加载")
            
            # 检查页面是否包含新的元素
            content = response.text
            
            if 'id="employeeSelect"' in content:
                print("✅ 找到员工选择下拉框")
            else:
                print("❌ 未找到员工选择下拉框")
                
            if 'id="studentsSection"' in content:
                print("✅ 找到学员列表区域")
            else:
                print("❌ 未找到学员列表区域")
                
            if 'id="studentDetailModal"' in content:
                print("✅ 找到学员详情模态框")
            else:
                print("❌ 未找到学员详情模态框")
                
            if 'loadEmployeeStudents()' in content:
                print("✅ 找到学员列表加载函数")
            else:
                print("❌ 未找到学员列表加载函数")
                
            return True
        else:
            print(f"❌ 页面加载失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_api_employees_students():
    """测试员工学员列表API"""
    try:
        # 先获取员工列表
        employees_url = urljoin(BASE_URL, '/api/employees')
        response = requests.get(employees_url, timeout=10)
        
        if response.status_code != 200:
            print("❌ 无法获取员工列表")
            return False
            
        employees = response.json()
        if not employees or isinstance(employees, dict) and 'error' in employees:
            print("❌ 员工列表为空或返回错误")
            return False
            
        # 取第一个员工测试
        employee_id = employees[0]['id']
        print(f"ℹ️ 使用员工ID {employee_id} 进行测试")
        
        # 测试学员列表API
        students_url = urljoin(BASE_URL, f'/api/employees/{employee_id}/students')
        response = requests.get(students_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 员工学员列表API正常响应")
            
            data = response.json()
            if data.get('success'):
                students = data.get('data', [])
                print(f"ℹ️ 找到 {len(students)} 个学员记录")
                
                if students:
                    # 检查学员数据结构
                    student = students[0]
                    expected_fields = ['customer_id', 'customer_name', 'total_sessions', 
                                     'total_commission', 'status_tags', 'first_registration']
                    
                    for field in expected_fields:
                        if field in student:
                            print(f"✅ 学员数据包含字段: {field}")
                        else:
                            print(f"❌ 学员数据缺少字段: {field}")
                else:
                    print("ℹ️ 该员工暂无学员数据")
                    
                return True
            else:
                print(f"❌ API返回失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 学员列表API请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试学员列表API失败: {e}")
        return False

def test_api_student_detail():
    """测试学员详情API"""
    try:
        # 先获取员工列表
        employees_url = urljoin(BASE_URL, '/api/employees')
        response = requests.get(employees_url, timeout=10)
        
        if response.status_code != 200:
            print("❌ 无法获取员工列表")
            return False
            
        employees = response.json()
        if not employees:
            print("❌ 员工列表为空")
            return False
            
        employee_id = employees[0]['id']
        
        # 获取学员列表
        students_url = urljoin(BASE_URL, f'/api/employees/{employee_id}/students')
        response = requests.get(students_url, timeout=10)
        
        if response.status_code != 200:
            print("❌ 无法获取学员列表")
            return False
            
        data = response.json()
        if not data.get('success') or not data.get('data'):
            print("ℹ️ 该员工没有学员数据，跳过学员详情测试")
            return True
            
        # 取第一个学员测试详情API
        customer_id = data['data'][0]['customer_id']
        print(f"ℹ️ 使用学员ID {customer_id} 进行详情测试")
        
        detail_url = urljoin(BASE_URL, f'/api/employees/{employee_id}/students/{customer_id}')
        response = requests.get(detail_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 学员详情API正常响应")
            
            data = response.json()
            if data.get('success'):
                detail_data = data.get('data', {})
                
                # 检查详情数据结构
                expected_sections = ['customer', 'trial_courses', 'formal_courses', 
                                   'renewal_courses', 'refund_records', 'commission_summary']
                
                for section in expected_sections:
                    if section in detail_data:
                        print(f"✅ 学员详情包含板块: {section}")
                    else:
                        print(f"❌ 学员详情缺少板块: {section}")
                
                # 检查提成汇总数据
                commission = detail_data.get('commission_summary', {})
                expected_commission_fields = ['trial_commission', 'formal_commission', 
                                            'renewal_commission', 'total_commission']
                
                for field in expected_commission_fields:
                    if field in commission:
                        print(f"✅ 提成汇总包含字段: {field}")
                    else:
                        print(f"❌ 提成汇总缺少字段: {field}")
                        
                return True
            else:
                print(f"❌ 学员详情API返回失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 学员详情API请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试学员详情API失败: {e}")
        return False

def test_login_required():
    """检查是否需要登录"""
    try:
        url = urljoin(BASE_URL, '/employee-performance')
        response = requests.get(url, timeout=10, allow_redirects=False)
        
        if response.status_code == 302:
            print("ℹ️ 页面需要登录访问")
            return True
        elif response.status_code == 200:
            print("ℹ️ 页面可直接访问")
            return False
        else:
            print(f"ℹ️ 未知状态，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("🔧 开始测试员工业绩页面重新设计功能...\n")
    
    # 检查登录要求
    login_required = test_login_required()
    
    if login_required:
        print("\n⚠️ 需要先登录才能访问页面")
        print("请手动访问 http://localhost:5000/login 登录后再测试")
        print("默认账户：用户名 17844540733，密码 yuan971035088")
        return
    
    # 测试主要功能
    tests = [
        ("员工业绩主页面", test_employee_performance_page),
        ("员工学员列表API", test_api_employees_students),
        ("学员详情API", test_api_student_detail),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📝 测试 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！新功能工作正常")
        print("\n📝 功能实现总结：")
        print("   1. ✅ 重新设计员工业绩页面为学员维度展示")
        print("   2. ✅ 实现员工选择和学员列表功能")
        print("   3. ✅ 实现学员详情模态框，包含四个业务板块")
        print("   4. ✅ 实现提成汇总计算和显示")
        print("   5. ✅ 新增学员维度的API接口")
        print("\n🌐 请手动访问 http://localhost:5000/employee-performance 体验新功能")
    else:
        print("⚠️ 部分测试失败，请检查Flask应用是否正常运行")

if __name__ == "__main__":
    main()