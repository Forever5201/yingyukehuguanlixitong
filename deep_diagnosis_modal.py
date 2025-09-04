#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深度诊断：刷单管理模态框无法显示的根本原因分析
根据控制台输出，函数被调用但模态框未显示，需要深入分析CSS、JavaScript和DOM问题
"""

import requests
from urllib.parse import urljoin
import re
import json

BASE_URL = "http://localhost:5000"

def deep_diagnosis_modal_issue():
    """深度诊断模态框问题的根本原因"""
    print("🔬 深度诊断：模态框无法显示的根本原因")
    print("=" * 60)
    
    # 创建session保持登录状态
    session = requests.Session()
    
    try:
        # 1. 登录系统
        print("\n🔐 步骤1: 用户认证")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ 登录失败，状态码: {login_response.status_code}")
            return False
        
        print("✅ 用户认证成功")
        
        # 2. 获取页面内容
        print("\n📄 步骤2: 获取页面源码")
        taobao_url = urljoin(BASE_URL, '/taobao-orders')
        page_response = session.get(taobao_url, timeout=10)
        
        if page_response.status_code != 200:
            print(f"❌ 页面访问失败，状态码: {page_response.status_code}")
            return False
        
        page_content = page_response.text
        print("✅ 页面源码获取成功")
        
        # 3. 分析模态框HTML结构
        print("\n🔍 步骤3: 分析模态框HTML结构")
        
        # 查找模态框元素
        modal_pattern = r'<div[^>]*id="orderModal"[^>]*>.*?</div>'
        modal_matches = re.findall(modal_pattern, page_content, re.DOTALL)
        
        if not modal_matches:
            print("❌ 严重问题：未找到orderModal元素！")
            return False
        
        modal_html = modal_matches[0]
        print("✅ 找到orderModal元素")
        
        # 分析模态框属性
        print("\n  📋 模态框属性分析:")
        
        # 检查class属性
        class_pattern = r'class="([^"]*)"'
        class_match = re.search(class_pattern, modal_html)
        if class_match:
            classes = class_match.group(1)
            print(f"    🏷️ CSS类: {classes}")
            
            if 'modal-hidden' in classes:
                print("    ✅ 包含modal-hidden类")
            else:
                print("    ❌ 缺少modal-hidden类")
        
        # 检查style属性
        style_pattern = r'style="([^"]*)"'
        style_match = re.search(style_pattern, modal_html)
        if style_match:
            style = style_match.group(1)
            print(f"    🎨 内联样式: {style}")
            
            # 分析display属性
            if 'display:' in style or 'display ' in style:
                print("    ⚠️ 内联样式包含display属性，可能与CSS类冲突")
            else:
                print("    ✅ 内联样式不包含display属性")
        
        # 4. 分析CSS样式定义
        print("\n🎨 步骤4: 分析CSS样式定义")
        
        # 查找modal-hidden样式定义
        css_pattern = r'\.modal-hidden\s*\{([^}]*)\}'
        css_match = re.search(css_pattern, page_content)
        
        if css_match:
            css_rules = css_match.group(1)
            print(f"    ✅ 找到modal-hidden样式: {css_rules.strip()}")
            
            if 'display: none !important' in css_rules:
                print("    ✅ modal-hidden使用了!important，优先级正确")
            else:
                print("    ❌ modal-hidden缺少!important，可能优先级不够")
        else:
            print("    ❌ 严重问题：未找到modal-hidden样式定义！")
        
        # 查找modal-show样式定义
        show_pattern = r'\.modal-show\s*\{([^}]*)\}'
        show_match = re.search(show_pattern, page_content)
        
        if show_match:
            show_rules = show_match.group(1)
            print(f"    ✅ 找到modal-show样式: {show_rules.strip()}")
            
            if 'display: flex !important' in show_rules:
                print("    ✅ modal-show使用了!important，优先级正确")
            else:
                print("    ❌ modal-show缺少!important，可能优先级不够")
        else:
            print("    ❌ 严重问题：未找到modal-show样式定义！")
        
        # 5. 分析JavaScript函数实现
        print("\n💻 步骤5: 分析JavaScript函数实现")
        
        # 查找showAddModal函数
        js_pattern = r'function showAddModal\(\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        js_match = re.search(js_pattern, page_content, re.DOTALL)
        
        if js_match:
            js_code = js_match.group(1)
            print("    ✅ 找到showAddModal函数")
            
            # 分析函数内容
            js_checks = {
                '获取modal元素': 'getElementById(\'orderModal\')' in js_code,
                '错误检查': 'console.error' in js_code,
                '移除hidden类': 'classList.remove(\'modal-hidden\')' in js_code,
                '添加show类': 'classList.add(\'modal-show\')' in js_code,
                '设置display样式': 'style.display = \'flex\'' in js_code,
                '调试日志': 'console.log' in js_code
            }
            
            print("    📋 函数功能检查:")
            for check_name, result in js_checks.items():
                status = "✅" if result else "❌"
                print(f"      {status} {check_name}")
        else:
            print("    ❌ 严重问题：未找到showAddModal函数！")
        
        # 6. 检查可能的CSS冲突
        print("\n⚔️ 步骤6: 检查可能的CSS冲突")
        
        # 查找其他modal相关样式
        modal_styles = re.findall(r'\.modal[^{]*\{[^}]*\}', page_content)
        print(f"    📊 找到{len(modal_styles)}个modal相关样式")
        
        # 检查是否有其他display样式
        conflict_checks = []
        for style in modal_styles:
            if 'display:' in style and 'modal-hidden' not in style and 'modal-show' not in style:
                conflict_checks.append(style)
        
        if conflict_checks:
            print("    ⚠️ 发现可能的样式冲突:")
            for conflict in conflict_checks:
                print(f"      - {conflict[:100]}...")
        else:
            print("    ✅ 未发现明显的样式冲突")
        
        # 7. 检查z-index层级问题
        print("\n📐 步骤7: 检查z-index层级问题")
        
        # 查找z-index设置
        zindex_pattern = r'z-index:\s*(\d+)'
        zindex_matches = re.findall(zindex_pattern, modal_html)
        
        if zindex_matches:
            zindex = int(zindex_matches[0])
            print(f"    📊 模态框z-index: {zindex}")
            
            if zindex >= 1000:
                print("    ✅ z-index层级合理")
            else:
                print("    ⚠️ z-index可能过低，容易被其他元素遮挡")
        else:
            print("    ❌ 未找到z-index设置")
        
        # 8. 检查JavaScript错误
        print("\n🐛 步骤8: 检查可能的JavaScript错误")
        
        # 查找可能的错误源
        error_patterns = [
            (r'console\.error\([^)]*\)', '错误日志'),
            (r'throw new Error\([^)]*\)', '抛出错误'),
            (r'catch\s*\([^)]*\)', '错误捕获'),
            (r'if\s*\(![^)]*\)\s*\{[^}]*return', '提前返回')
        ]
        
        potential_errors = []
        for pattern, desc in error_patterns:
            matches = re.findall(pattern, js_code if 'js_code' in locals() else '')
            if matches:
                potential_errors.extend([(desc, match) for match in matches])
        
        if potential_errors:
            print("    📋 发现潜在错误处理:")
            for desc, error in potential_errors:
                print(f"      - {desc}: {error[:60]}...")
        else:
            print("    ✅ 未发现错误处理代码")
        
        # 9. 综合分析和诊断结论
        print("\n" + "=" * 60)
        print("🎯 根本原因分析")
        print("=" * 60)
        
        # 根据检查结果分析根本原因
        issues_found = []
        
        if not css_match:
            issues_found.append("缺少modal-hidden CSS样式定义")
        
        if not show_match:
            issues_found.append("缺少modal-show CSS样式定义")
        
        if css_match and 'display: none !important' not in css_match.group(1):
            issues_found.append("modal-hidden样式缺少!important声明")
        
        if show_match and 'display: flex !important' not in show_match.group(1):
            issues_found.append("modal-show样式缺少!important声明")
        
        if conflict_checks:
            issues_found.append("存在CSS样式冲突")
        
        if not js_match:
            issues_found.append("缺少showAddModal函数")
        
        if issues_found:
            print("🚨 发现的问题:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print("🤔 未发现明显的代码问题，可能是运行时问题")
        
        # 10. 提供解决方案
        print("\n💡 解决方案建议:")
        
        if issues_found:
            print("1. 修复代码问题：")
            for issue in issues_found:
                if "CSS样式" in issue:
                    print("   - 添加或修复CSS样式定义")
                elif "函数" in issue:
                    print("   - 添加或修复JavaScript函数")
                elif "冲突" in issue:
                    print("   - 解决CSS样式冲突")
        
        print("2. 运行时调试：")
        print("   - 在浏览器中检查Elements面板的模态框元素")
        print("   - 查看Computed样式确认display属性的最终值")
        print("   - 在Console中手动执行showAddModal()函数")
        print("   - 检查是否有JavaScript运行时错误")
        
        print("3. 临时解决方案：")
        print("   - 直接在Console中执行: document.getElementById('orderModal').style.display = 'flex'")
        print("   - 检查模态框是否能手动显示")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 诊断过程发生错误: {e}")
        return False

if __name__ == "__main__":
    deep_diagnosis_modal_issue()