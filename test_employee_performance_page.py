#!/usr/bin/env python3
"""
测试员工业绩页面修改
"""

import requests
import re

BASE_URL = "http://localhost:5000"

def test_employee_performance_page():
    """测试员工业绩页面修改"""
    print("🧪 开始测试员工业绩页面修改...")
    
    # 测试员工业绩页面
    print("\n1. 测试员工业绩页面")
    try:
        response = requests.get(f"{BASE_URL}/employee-performance")
        if response.status_code == 200:
            print("✓ 员工业绩页面可访问")
            
            # 检查是否还有"添加员工"按钮
            if "添加员工" in response.text:
                print("❌ 员工业绩页面仍包含'添加员工'按钮")
            else:
                print("✓ 员工业绩页面已移除'添加员工'按钮")
            
            # 检查是否有"员工管理"链接
            if "员工管理" in response.text:
                print("✓ 员工业绩页面包含'员工管理'链接")
            else:
                print("❌ 员工业绩页面缺少'员工管理'链接")
            
            # 检查是否还有添加员工模态框
            if "addEmployeeModal" in response.text:
                print("❌ 员工业绩页面仍包含添加员工模态框")
            else:
                print("✓ 员工业绩页面已移除添加员工模态框")
            
            # 检查是否还有showAddEmployeeModal函数
            if "showAddEmployeeModal" in response.text:
                print("❌ 员工业绩页面仍包含showAddEmployeeModal函数")
            else:
                print("✓ 员工业绩页面已移除showAddEmployeeModal函数")
            
            # 检查是否还有saveNewEmployee函数
            if "saveNewEmployee" in response.text:
                print("❌ 员工业绩页面仍包含saveNewEmployee函数")
            else:
                print("✓ 员工业绩页面已移除saveNewEmployee函数")
            
        else:
            print(f"❌ 员工业绩页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 测试系统配置页面
    print("\n2. 测试系统配置页面")
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            print("✓ 系统配置页面可访问")
            
            # 检查是否有员工管理标签页
            if "员工管理" in response.text:
                print("✓ 系统配置页面包含员工管理模块")
            else:
                print("❌ 系统配置页面缺少员工管理模块")
            
            # 检查是否有新增员工按钮
            if "新增员工" in response.text:
                print("✓ 系统配置页面包含新增员工功能")
            else:
                print("❌ 系统配置页面缺少新增员工功能")
            
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_employee_performance_page()

