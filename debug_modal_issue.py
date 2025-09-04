#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试刷单管理页面模态框问题
"""

import requests
from urllib.parse import urljoin
import re

BASE_URL = "http://localhost:5000"

def debug_modal_issue():
    """调试模态框问题"""
    print("🔍 调试刷单管理页面模态框问题...")
    
    # 创建session保持登录状态
    session = requests.Session()
    
    try:
        # 1. 登录
        print("\n🔐 步骤1: 登录系统")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ 登录失败，状态码: {login_response.status_code}")
            return False
        
        print("✅ 登录成功")
        
        # 2. 获取页面内容
        print("\n📄 步骤2: 获取页面内容")
        taobao_url = urljoin(BASE_URL, '/taobao-orders')
        response = session.get(taobao_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 页面访问失败，状态码: {response.status_code}")
            return False
        
        content = response.text
        print("✅ 页面内容获取成功")
        
        # 3. 检查关键元素
        print("\n🔍 步骤3: 检查关键元素")
        
        # 检查按钮
        button_pattern = r'<button[^>]*onclick="showAddModal\(\)"[^>]*>'
        button_match = re.search(button_pattern, content)
        if button_match:
            print("✅ 找到添加按钮")
            print(f"  按钮HTML: {button_match.group(0)}")
        else:
            print("❌ 未找到添加按钮")
        
        # 检查模态框
        modal_pattern = r'<div[^>]*id="orderModal"[^>]*>'
        modal_match = re.search(modal_pattern, content)
        if modal_match:
            print("✅ 找到模态框元素")
            print(f"  模态框HTML: {modal_match.group(0)}")
        else:
            print("❌ 未找到模态框元素")
        
        # 检查showAddModal函数
        function_pattern = r'function showAddModal\(\)[^}]*\}'
        function_match = re.search(function_pattern, content, re.DOTALL)
        if function_match:
            print("✅ 找到showAddModal函数")
            print(f"  函数定义:")
            function_code = function_match.group(0)
            for i, line in enumerate(function_code.split('\n'), 1):
                print(f"    {i}: {line.strip()}")
        else:
            print("❌ 未找到showAddModal函数")
        
        # 4. 检查可能的JavaScript错误
        print("\n🐛 步骤4: 检查潜在问题")
        
        # 检查重复的function定义
        showAddModal_count = content.count('function showAddModal')
        if showAddModal_count > 1:
            print(f"⚠️ 发现{showAddModal_count}个showAddModal函数定义，可能存在冲突")
        else:
            print("✅ showAddModal函数定义唯一")
        
        # 检查orderModal元素数量
        orderModal_count = content.count('id="orderModal"')
        if orderModal_count > 1:
            print(f"⚠️ 发现{orderModal_count}个orderModal元素，ID重复")
        elif orderModal_count == 1:
            print("✅ orderModal元素ID唯一")
        else:
            print("❌ 未找到orderModal元素")
        
        # 检查是否有CSS冲突
        css_issues = []
        if 'display: none' in content and 'display: flex' in content:
            css_issues.append("CSS中同时存在display:none和display:flex，可能有优先级问题")
        
        if '.modal' in content and 'z-index' in content:
            print("✅ 找到模态框相关CSS")
        
        # 检查Bootstrap冲突
        if 'bootstrap' in content.lower() and 'modal' in content.lower():
            if 'bootstrap.Modal' in content:
                css_issues.append("页面可能同时使用自定义模态框和Bootstrap模态框，可能冲突")
        
        if css_issues:
            print("⚠️ 发现潜在CSS问题:")
            for issue in css_issues:
                print(f"  - {issue}")
        else:
            print("✅ 未发现明显CSS冲突")
        
        # 5. 检查JavaScript加载顺序
        print("\n📚 步骤5: 检查JavaScript加载")
        
        # 查找所有script标签
        script_pattern = r'<script[^>]*>.*?</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        print(f"找到{len(scripts)}个script块")
        
        # 检查是否有语法错误
        syntax_issues = []
        for i, script in enumerate(scripts):
            if 'showAddModal' in script:
                print(f"  Script {i+1}: 包含showAddModal函数")
                # 简单检查语法问题
                if script.count('{') != script.count('}'):
                    syntax_issues.append(f"Script {i+1}: 大括号不匹配")
                if script.count('(') != script.count(')'):
                    syntax_issues.append(f"Script {i+1}: 小括号不匹配")
        
        if syntax_issues:
            print("⚠️ 发现潜在语法问题:")
            for issue in syntax_issues:
                print(f"  - {issue}")
        else:
            print("✅ 未发现明显语法问题")
        
        # 6. 生成修复建议
        print("\n💡 修复建议:")
        
        if not button_match or not modal_match:
            print("1. 检查HTML模板是否正确渲染")
        
        if not function_match:
            print("2. 确保showAddModal函数正确定义")
        
        if showAddModal_count > 1 or orderModal_count > 1:
            print("3. 删除重复的函数定义或元素ID")
        
        if css_issues:
            print("4. 解决CSS样式冲突")
        
        print("5. 建议在浏览器开发者工具中:")
        print("   - 检查控制台是否有JavaScript错误")
        print("   - 在console中手动执行: showAddModal()")
        print("   - 检查元素: document.getElementById('orderModal')")
        print("   - 检查CSS: getComputedStyle(document.getElementById('orderModal'))")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    debug_modal_issue()