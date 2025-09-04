#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证customers.html修复效果的脚本
"""

import os

def verify_customers_fix():
    """验证customers.html修复效果"""
    print("🔍 验证customers.html修复效果...")
    
    file_path = "app/templates/customers.html"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n=== 检查修复项目 ===")
    
    # 检查是否移除了有问题的onclick属性
    if 'onclick="editCustomer({{ customer.id }})"' in content:
        print("❌ 仍然存在有问题的editCustomer onclick")
        return False
    else:
        print("✅ 已移除有问题的editCustomer onclick")
    
    if 'onclick="deleteCustomer({{ customer.id }})"' in content:
        print("❌ 仍然存在有问题的deleteCustomer onclick")
        return False
    else:
        print("✅ 已移除有问题的deleteCustomer onclick")
    
    # 检查是否添加了data属性
    if 'data-customer-id="{{ customer.id }}"' in content:
        print("✅ 已添加data-customer-id属性")
    else:
        print("❌ 缺少data-customer-id属性")
        return False
    
    # 检查是否添加了CSS类
    if 'edit-btn' in content and 'delete-btn' in content:
        print("✅ 已添加edit-btn和delete-btn CSS类")
    else:
        print("❌ 缺少edit-btn或delete-btn CSS类")
        return False
    
    # 检查是否添加了事件监听器初始化
    if 'initEventListeners' in content:
        print("✅ 已添加事件监听器初始化函数")
    else:
        print("❌ 缺少事件监听器初始化函数")
        return False
    
    if 'DOMContentLoaded' in content:
        print("✅ 已添加DOMContentLoaded事件监听")
    else:
        print("❌ 缺少DOMContentLoaded事件监听")
        return False
    
    print("\n=== 检查JavaScript结构 ===")
    
    # 检查关键函数是否存在
    functions_to_check = [
        'showAddModal',
        'closeAddModal', 
        'editCustomer',
        'deleteCustomer',
        'initEventListeners'
    ]
    
    for func in functions_to_check:
        if f'function {func}(' in content:
            print(f"✅ 函数 {func} 存在")
        else:
            print(f"❌ 函数 {func} 缺失")
            return False
    
    print("\n🎉 所有修复项目检查通过！")
    
    print("\n💡 修复说明:")
    print("1. 移除了onclick属性中的模板语法，避免JavaScript语法错误")
    print("2. 使用data-customer-id属性存储客户ID")
    print("3. 添加了edit-btn和delete-btn CSS类用于事件绑定")
    print("4. 使用事件监听器替代onclick属性")
    print("5. 在DOMContentLoaded时初始化所有事件监听器")
    
    return True

if __name__ == '__main__':
    print("🚀 开始验证customers.html修复效果...")
    
    success = verify_customers_fix()
    
    if success:
        print("\n✅ customers.html修复验证成功！")
        print("\n📋 后续步骤:")
        print("1. 重启Flask应用")
        print("2. 访问客户管理页面: http://localhost:5000/customers")
        print("3. 测试编辑和删除功能")
    else:
        print("\n❌ customers.html修复验证失败！")