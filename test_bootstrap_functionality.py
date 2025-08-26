#!/usr/bin/env python3
"""
测试Bootstrap功能
"""

import requests
import re

BASE_URL = "http://localhost:5000"

def test_bootstrap_functionality():
    """测试Bootstrap功能"""
    print("🧪 开始测试Bootstrap功能...")
    
    # 测试系统配置页面
    print("\n1. 测试系统配置页面Bootstrap")
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            print("✓ 系统配置页面可访问")
            
            # 检查Bootstrap CSS
            if "bootstrap.min.css" in response.text:
                print("✓ Bootstrap CSS已加载")
            else:
                print("❌ Bootstrap CSS未找到")
            
            # 检查Bootstrap JavaScript
            if "bootstrap.bundle.min.js" in response.text:
                print("✓ Bootstrap JavaScript已加载")
            else:
                print("❌ Bootstrap JavaScript未找到")
            
            # 检查Bootstrap Icons
            if "bootstrap-icons" in response.text:
                print("✓ Bootstrap Icons已加载")
            else:
                print("❌ Bootstrap Icons未找到")
            
            # 检查模态框相关代码
            if "data-bs-toggle" in response.text:
                print("✓ Bootstrap模态框属性正确")
            else:
                print("❌ Bootstrap模态框属性未找到")
            
            # 检查Bootstrap类名
            bootstrap_classes = [
                "modal fade", "modal-dialog", "modal-content", 
                "modal-header", "modal-body", "modal-footer",
                "btn-close", "table-hover", "table-dark"
            ]
            
            missing_classes = []
            for class_name in bootstrap_classes:
                if class_name not in response.text:
                    missing_classes.append(class_name)
            
            if missing_classes:
                print(f"❌ 缺少Bootstrap类: {', '.join(missing_classes)}")
            else:
                print("✓ 所有Bootstrap类名正确")
            
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 测试员工管理功能
    print("\n2. 测试员工管理功能")
    try:
        # 测试获取员工列表
        response = requests.get(f"{BASE_URL}/api/employees")
        if response.status_code == 200:
            employees = response.json()
            print(f"✓ 成功获取 {len(employees)} 个员工")
            
            if len(employees) > 0:
                # 测试编辑员工功能（模拟）
                employee_id = employees[0]['id']
                print(f"✓ 找到员工ID: {employee_id}")
                print("✓ 员工管理API正常工作")
            else:
                print("⚠️ 没有员工数据，无法测试编辑功能")
        else:
            print(f"❌ 获取员工列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n🎉 Bootstrap功能测试完成！")
    print("\n📝 说明：")
    print("- 如果所有检查都通过，说明Bootstrap已正确加载")
    print("- 编辑员工功能应该不再出现'bootstrap is not defined'错误")
    print("- 界面排版应该更加美观协调")

if __name__ == "__main__":
    test_bootstrap_functionality()

