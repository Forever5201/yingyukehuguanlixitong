"""
测试员工分配冲突处理功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_conflict_scenario():
    """测试冲突场景"""
    print("=== 测试员工分配冲突处理 ===\n")
    
    # 假设试听课 ID 13 已经修复，我们测试另一个场景
    # 或者创造一个新的冲突场景
    
    course_id = 13  # 使用之前有问题的课程
    
    # 1. 第一次尝试分配（应该返回409冲突）
    print("1. 尝试分配员工，预期返回冲突...")
    response = requests.post(
        f"{BASE_URL}/api/trial-courses/{course_id}/assign",
        json={"employee_id": "2"},  # 假设要分配给员工ID 2
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   状态码: {response.status_code}")
    if response.status_code == 409:
        data = response.json()
        print(f"   ✅ 检测到冲突: {data.get('message', '')}")
        print(f"   冲突信息: {json.dumps(data.get('conflict_info', {}), ensure_ascii=False, indent=2)}")
    else:
        print(f"   响应: {response.json()}")
    
    # 2. 强制更新（解决冲突）
    print("\n2. 强制更新，解决冲突...")
    response = requests.post(
        f"{BASE_URL}/api/trial-courses/{course_id}/assign",
        json={
            "employee_id": "2",
            "force_update": True
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   状态码: {response.status_code}")
    data = response.json()
    if response.status_code == 200 and data.get('success'):
        print(f"   ✅ 成功: {data.get('message', '')}")
        details = data.get('details', {})
        print(f"   更新了 {details.get('updated_courses_count', 0)} 个课程")
        if details.get('resolved_conflict'):
            print(f"   解决了冲突，之前的员工是: {details.get('previous_formal_employee', '')}")
    else:
        print(f"   ❌ 失败: {data.get('message', '')}")


def test_null_assignment():
    """测试取消分配"""
    print("\n\n=== 测试取消分配 ===\n")
    
    course_id = 13
    
    print("尝试取消分配...")
    response = requests.post(
        f"{BASE_URL}/api/trial-courses/{course_id}/assign",
        json={"employee_id": None},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    if response.status_code == 200 and data.get('success'):
        print(f"✅ 成功: {data.get('message', '')}")
    else:
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")


if __name__ == '__main__':
    print("注意：请确保Flask应用正在运行 (http://localhost:5000)\n")
    
    try:
        # 测试服务器是否在运行
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器正在运行\n")
            
            test_conflict_scenario()
            # test_null_assignment()  # 可选：测试取消分配
        else:
            print("❌ 服务器未响应")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")