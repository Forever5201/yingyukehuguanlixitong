#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行时模态框问题诊断工具
专门检查浏览器端实际执行情况，而不仅仅是代码存在性
"""

import requests
from urllib.parse import urljoin
import re
import json

BASE_URL = "http://localhost:5000"

def runtime_modal_diagnostic():
    """运行时模态框问题诊断"""
    print("🔬 运行时模态框问题深度诊断")
    print("=" * 60)
    
    session = requests.Session()
    
    try:
        # 1. 登录
        print("\n🔐 步骤1: 用户认证")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            return False
            
        print("✅ 用户认证成功")
        
        # 2. 深度分析正课管理页面
        print("\n📋 步骤2: 深度分析正课管理页面")
        analyze_formal_courses_page(session)
        
        # 3. 深度分析试听课管理页面
        print("\n📋 步骤3: 深度分析试听课管理页面")
        analyze_trial_courses_page(session)
        
        # 4. 生成浏览器实时诊断脚本
        print("\n📋 步骤4: 生成浏览器实时诊断脚本")
        generate_browser_diagnostic_script()
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断过程发生错误: {e}")
        return False

def analyze_formal_courses_page(session):
    """深度分析正课管理页面"""
    print("  🎓 分析正课管理页面运行时问题...")
    
    try:
        response = session.get(urljoin(BASE_URL, '/formal-courses'), timeout=10)
        if response.status_code != 200:
            print(f"    ❌ 页面访问失败: {response.status_code}")
            return
            
        content = response.text
        
        # 1. 检查JavaScript加载顺序
        print("    📊 JavaScript加载顺序分析:")
        
        # 查找所有script标签
        script_pattern = r'<script[^>]*src=["\']([^"\']*)["\'][^>]*>'
        scripts = re.findall(script_pattern, content)
        
        script_order = []
        for i, script in enumerate(scripts):
            script_order.append(f"    {i+1}. {script}")
            if 'global-modal-fix.js' in script:
                print(f"    ✅ 找到全局修复脚本，加载顺序: 第{i+1}位")
        
        if script_order:
            print("    📜 JavaScript加载顺序:")
            for order in script_order:
                print(order)
        
        # 2. 检查按钮HTML结构
        print("\n    🔘 按钮HTML结构分析:")
        
        # 查找退费按钮
        refund_button_pattern = r'onclick=["\']showRefundModal\([^)]*\)["\']'
        refund_buttons = re.findall(refund_button_pattern, content)
        
        if refund_buttons:
            print(f"    ✅ 找到 {len(refund_buttons)} 个退费按钮")
            for i, button in enumerate(refund_buttons[:3]):  # 只显示前3个
                print(f"    📄 按钮{i+1}: {button}")
        else:
            print("    ❌ 未找到退费按钮的onclick事件")
        
        # 查找查看按钮
        view_button_pattern = r'onclick=["\']showCustomerDetail\([^)]*\)["\']'
        view_buttons = re.findall(view_button_pattern, content)
        
        if view_buttons:
            print(f"    ✅ 找到 {len(view_buttons)} 个查看按钮")
            for i, button in enumerate(view_buttons[:3]):  # 只显示前3个
                print(f"    📄 按钮{i+1}: {button}")
        else:
            print("    ❌ 未找到查看按钮的onclick事件")
        
        # 3. 检查模态框HTML结构
        print("\n    🎭 模态框HTML结构分析:")
        
        # 退费模态框
        if 'id="refundModal"' in content:
            print("    ✅ 退费模态框HTML存在")
        else:
            print("    ❌ 退费模态框HTML缺失")
        
        # 客户详情模态框（来自组件）
        if 'customer_detail_modal.html' in content:
            print("    ✅ 客户详情模态框组件已引入")
        else:
            print("    ❌ 客户详情模态框组件缺失")
        
        # 4. 检查可能的冲突
        print("\n    ⚔️ 潜在冲突分析:")
        
        # 检查是否有重复的函数定义
        showRefundModal_count = content.count('function showRefundModal')
        showCustomerDetail_count = content.count('function showCustomerDetail')
        
        print(f"    📊 showRefundModal函数定义数量: {showRefundModal_count}")
        print(f"    📊 showCustomerDetail函数定义数量: {showCustomerDetail_count}")
        
        if showRefundModal_count > 1:
            print("    ⚠️ 发现showRefundModal函数重复定义，可能导致冲突")
        if showCustomerDetail_count > 1:
            print("    ⚠️ 发现showCustomerDetail函数重复定义，可能导致冲突")
        
        # 检查是否有JavaScript错误
        if 'console.error' in content:
            print("    ⚠️ 页面包含错误处理代码，可能有潜在错误")
        
    except Exception as e:
        print(f"    ❌ 分析失败: {e}")

def analyze_trial_courses_page(session):
    """深度分析试听课管理页面"""
    print("  🎵 分析试听课管理页面运行时问题...")
    
    try:
        response = session.get(urljoin(BASE_URL, '/trial-courses'), timeout=10)
        if response.status_code != 200:
            print(f"    ❌ 页面访问失败: {response.status_code}")
            return
            
        content = response.text
        
        # 1. 检查编辑按钮
        print("    🔘 编辑按钮HTML结构分析:")
        
        edit_button_pattern = r'onclick=["\']editTrialCourse\([^)]*\)["\']'
        edit_buttons = re.findall(edit_button_pattern, content)
        
        if edit_buttons:
            print(f"    ✅ 找到 {len(edit_buttons)} 个编辑按钮")
            for i, button in enumerate(edit_buttons[:3]):
                print(f"    📄 按钮{i+1}: {button}")
        else:
            print("    ❌ 未找到编辑按钮的onclick事件")
        
        # 2. 检查查看按钮
        view_button_pattern = r'onclick=["\']showCustomerDetail\([^)]*\)["\']'
        view_buttons = re.findall(view_button_pattern, content)
        
        if view_buttons:
            print(f"    ✅ 找到 {len(view_buttons)} 个查看按钮")
        else:
            print("    ❌ 未找到查看按钮的onclick事件")
        
        # 3. 检查CourseManager依赖
        print("\n    🔧 CourseManager依赖分析:")
        
        if 'CourseManager.editTrialCourse' in content:
            print("    ✅ 找到CourseManager.editTrialCourse调用")
        else:
            print("    ❌ 未找到CourseManager.editTrialCourse调用")
        
        if 'course-management.js' in content:
            print("    ✅ course-management.js脚本已引入")
        else:
            print("    ❌ course-management.js脚本缺失")
        
        # 4. 检查editTrialModal
        if 'id="editTrialModal"' in content:
            print("    ✅ editTrialModal元素存在")
        else:
            print("    ❌ editTrialModal元素缺失")
        
    except Exception as e:
        print(f"    ❌ 分析失败: {e}")

def generate_browser_diagnostic_script():
    """生成浏览器实时诊断脚本"""
    print("  📜 生成浏览器实时诊断脚本...")
    
    diagnostic_script = '''
// ========================================
// 浏览器端实时模态框诊断脚本
// 在有问题的页面Console中执行此脚本
// ========================================

console.log('🔬 开始浏览器端实时诊断...');

// 1. 检查全局对象
console.log('\\n📊 全局对象检查:');
console.log('  GlobalModalManager:', typeof GlobalModalManager);
console.log('  showRefundModal:', typeof showRefundModal);
console.log('  showCustomerDetail:', typeof showCustomerDetail);
console.log('  editTrialCourse:', typeof editTrialCourse);
console.log('  CourseManager:', typeof CourseManager);

// 2. 检查关键元素
console.log('\\n🎭 关键元素检查:');
const elements = [
    'refundModal',
    'customerDetailModal', 
    'editTrialModal',
    'orderModal'
];

elements.forEach(id => {
    const element = document.getElementById(id);
    console.log(`  ${id}:`, element ? '✅ 存在' : '❌ 缺失');
    if (element) {
        const style = window.getComputedStyle(element);
        console.log(`    display: ${style.display}, visibility: ${style.visibility}`);
    }
});

// 3. 检查按钮事件绑定
console.log('\\n🔘 按钮事件绑定检查:');

// 查找所有包含onclick的按钮
const buttons = document.querySelectorAll('button[onclick]');
console.log(`  找到 ${buttons.length} 个有onclick事件的按钮`);

let refundButtons = 0;
let viewButtons = 0;
let editButtons = 0;

buttons.forEach((btn, index) => {
    const onclick = btn.getAttribute('onclick');
    if (onclick.includes('showRefundModal')) {
        refundButtons++;
        console.log(`  退费按钮${refundButtons}: ${onclick}`);
    } else if (onclick.includes('showCustomerDetail')) {
        viewButtons++;
        console.log(`  查看按钮${viewButtons}: ${onclick}`);
    } else if (onclick.includes('editTrialCourse')) {
        editButtons++;
        console.log(`  编辑按钮${editButtons}: ${onclick}`);
    }
});

console.log(`\\n📊 按钮统计: 退费${refundButtons}个, 查看${viewButtons}个, 编辑${editButtons}个`);

// 4. 手动测试函数调用
console.log('\\n🧪 手动测试函数调用:');

// 测试showRefundModal
if (typeof showRefundModal === 'function') {
    console.log('  showRefundModal函数存在，可手动测试');
    console.log('  执行: showRefundModal(1)');
} else {
    console.log('  ❌ showRefundModal函数不存在');
}

// 测试showCustomerDetail
if (typeof showCustomerDetail === 'function') {
    console.log('  showCustomerDetail函数存在，可手动测试');
    console.log('  执行: showCustomerDetail(1, 1, "formal")');
} else {
    console.log('  ❌ showCustomerDetail函数不存在');
}

// 测试editTrialCourse
if (typeof editTrialCourse === 'function') {
    console.log('  editTrialCourse函数存在，可手动测试');
    console.log('  执行: editTrialCourse(1)');
} else {
    console.log('  ❌ editTrialCourse函数不存在');
}

// 5. 检查错误监听
console.log('\\n💥 错误监听设置:');
window.addEventListener('error', function(e) {
    console.error('🚨 捕获到JavaScript错误:', e.error.message);
    console.error('🚨 错误详情:', e.error);
});

// 6. 提供测试命令
console.log('\\n🎯 建议测试命令:');
console.log('1. 手动测试退费模态框: showRefundModal(1)');
console.log('2. 手动测试客户详情: showCustomerDetail(1, 1, "formal")'); 
console.log('3. 手动测试试听课编辑: editTrialCourse(1)');
console.log('4. 强制显示模态框: GlobalModalManager.forceShowModal("refundModal")');
console.log('5. 检查点击事件: $("button[onclick*=showRefundModal]").click()');

console.log('\\n✅ 浏览器端诊断完成！请尝试上述测试命令。');
'''
    
    # 保存脚本
    with open('f:/3454353/browser_runtime_diagnostic.js', 'w', encoding='utf-8') as f:
        f.write(diagnostic_script)
    
    print("    ✅ 诊断脚本已保存到: f:/3454353/browser_runtime_diagnostic.js")
    
    print("\n💡 使用方法:")
    print("1. 在有问题的页面按F12打开开发者工具")
    print("2. 切换到Console标签")
    print("3. 复制并执行上述脚本")
    print("4. 根据诊断结果判断具体问题")

if __name__ == "__main__":
    print("🔬 启动运行时模态框问题诊断...")
    
    success = runtime_modal_diagnostic()
    
    print("\n" + "=" * 60)
    print("🎯 诊断结果总结")
    print("=" * 60)
    
    if success:
        print("✅ 诊断脚本执行成功")
        print()
        print("📋 下一步操作:")
        print("1. 在浏览器中打开有问题的页面")
        print("2. 按F12打开开发者工具")
        print("3. 在Console中执行诊断脚本")
        print("4. 根据诊断结果定位具体问题")
        print()
        print("🔧 可能的根本原因:")
        print("- JavaScript加载顺序问题")
        print("- 函数重复定义导致冲突")
        print("- DOM元素缺失或ID错误")
        print("- 网络请求失败或API不存在")
        print("- 浏览器缓存问题")
    else:
        print("❌ 诊断过程遇到问题，请检查网络连接")