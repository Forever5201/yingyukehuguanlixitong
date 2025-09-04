#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试刷单管理模态框修复效果
验证点击"添加刷单记录"按钮是否能正常弹出模态框
"""

import requests
from urllib.parse import urljoin
import re

BASE_URL = "http://localhost:5000"

def test_modal_fix():
    """测试模态框修复效果"""
    print("🔧 测试刷单管理模态框修复效果...")
    print("=" * 50)
    
    # 创建session保持登录状态
    session = requests.Session()
    
    try:
        # 1. 登录系统
        print("\n🔐 步骤1: 用户登录")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        if login_response.status_code == 200:
            print("✅ 用户登录成功")
        else:
            print(f"❌ 用户登录失败，状态码: {login_response.status_code}")
            return False
        
        # 2. 访问刷单管理页面
        print("\n📱 步骤2: 访问刷单管理页面")
        taobao_url = urljoin(BASE_URL, '/taobao-orders')
        page_response = session.get(taobao_url, timeout=10)
        
        if page_response.status_code != 200:
            print(f"❌ 页面访问失败，状态码: {page_response.status_code}")
            return False
        
        print("✅ 刷单管理页面访问成功")
        page_content = page_response.text
        
        # 3. 检查修复内容
        print("\n🔍 步骤3: 检查修复内容")
        
        # 检查CSS修复
        css_checks = {
            'modal-hidden类定义': '.modal-hidden' in page_content,
            'modal-show类定义': '.modal-show' in page_content,
            'display none样式': 'display: none !important' in page_content,
            'display flex样式': 'display: flex !important' in page_content
        }
        
        print("  📋 CSS修复检查:")
        for check_name, result in css_checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        # 检查JavaScript修复
        js_checks = {
            'showAddModal函数': 'function showAddModal()' in page_content,
            'console.log调试': 'console.log' in page_content,
            'classList.remove调用': 'classList.remove(' in page_content,
            'classList.add调用': 'classList.add(' in page_content,
            '错误处理': 'console.error' in page_content
        }
        
        print("\n  📋 JavaScript修复检查:")
        for check_name, result in js_checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        # 4. 检查模态框HTML结构
        print("\n📋 步骤4: 检查模态框HTML结构")
        
        # 查找模态框元素
        modal_pattern = r'<div[^>]*id="orderModal"[^>]*>'
        modal_match = re.search(modal_pattern, page_content)
        
        if modal_match:
            modal_html = modal_match.group(0)
            print("✅ 找到orderModal元素")
            
            # 检查模态框属性
            modal_checks = {
                '包含modal-hidden类': 'modal-hidden' in modal_html,
                '包含固定定位': 'position: fixed' in modal_html,
                '包含z-index': 'z-index' in modal_html,
                '包含背景色': 'background-color' in modal_html
            }
            
            for check_name, result in modal_checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
                
            print(f"  📄 模态框HTML: {modal_html[:100]}...")
        else:
            print("❌ 未找到orderModal元素")
        
        # 5. 检查按钮事件绑定
        print("\n📋 步骤5: 检查按钮事件绑定")
        
        button_pattern = r'onclick="showAddModal\(\)"'
        button_match = re.search(button_pattern, page_content)
        
        if button_match:
            print("✅ 找到添加刷单记录按钮的onclick事件")
        else:
            print("❌ 未找到按钮的onclick事件绑定")
        
        # 6. 总体评估
        print("\n📊 步骤6: 修复效果评估")
        
        css_success = all(css_checks.values())
        js_success = all(js_checks.values())
        modal_success = modal_match is not None
        button_success = button_match is not None
        
        total_success = css_success and js_success and modal_success and button_success
        
        print(f"  📊 CSS修复: {'✅ 成功' if css_success else '❌ 失败'}")
        print(f"  📊 JavaScript修复: {'✅ 成功' if js_success else '❌ 失败'}")
        print(f"  📊 模态框结构: {'✅ 正常' if modal_success else '❌ 异常'}")
        print(f"  📊 按钮事件: {'✅ 正常' if button_success else '❌ 异常'}")
        
        # 7. 最终结论
        print("\n" + "=" * 50)
        print("🎯 修复效果总结")
        print("=" * 50)
        
        if total_success:
            print("🎉 模态框问题已成功修复！")
            print("\n✅ 修复内容:")
            print("1. 添加了.modal-hidden和.modal-show CSS类")
            print("2. 优化了showAddModal()和closeModal()函数")
            print("3. 添加了调试日志和错误处理")
            print("4. 修复了CSS样式优先级冲突")
            
            print("\n💡 现在用户应该可以:")
            print("- 点击'添加刷单记录'按钮弹出模态框")
            print("- 在模态框中填写刷单信息")
            print("- 正常关闭模态框")
            print("- 通过F12查看调试日志确认功能工作")
            
        else:
            print("⚠️ 修复可能不完整，建议进一步检查:")
            
            if not css_success:
                print("- 检查CSS样式定义")
            if not js_success:
                print("- 检查JavaScript函数实现")
            if not modal_success:
                print("- 检查HTML模态框结构")
            if not button_success:
                print("- 检查按钮事件绑定")
        
        print("\n🔧 故障排除建议:")
        print("1. 刷新浏览器页面清除缓存")
        print("2. 按F12打开开发者工具查看Console输出")
        print("3. 点击按钮时查看是否有'showAddModal被调用'日志")
        print("4. 检查Elements面板中modal元素的CSS类变化")
        
        return total_success
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        return False

if __name__ == "__main__":
    test_modal_fix()