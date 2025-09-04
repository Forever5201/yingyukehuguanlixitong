#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证员工绩效页面的修复内容
"""

import os

def check_fixes():
    """检查修复是否正确应用"""
    print("=" * 60)
    print("🔧 员工绩效页面JSON解析修复验证")
    print("=" * 60)
    
    template_path = "f:\\3454353\\app\\templates\\employee_performance.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查修复项目
        fixes_to_check = [
            {
                'name': 'JSON解析错误处理',
                'pattern': 'catch (e)',
                'context': 'JSON.parse(this.dataset.employeeName)'
            },
            {
                'name': '数据结构兼容性处理',
                'pattern': 'const students = data.students || data.data || []',
                'context': 'renderStudentsList'
            },
            {
                'name': 'API错误处理优化',
                'pattern': 'if (!response.ok)',
                'context': 'loadEmployeeStudents'
            },
            {
                'name': '空值安全处理 - 试听课',
                'pattern': '(course.trial_price || 0)',
                'context': 'renderTrialContent'
            },
            {
                'name': '空值安全处理 - 正课',
                'pattern': '(course.course_type || \'未知\')',
                'context': 'renderFormalContent'
            },
            {
                'name': '空值安全处理 - 续课',
                'pattern': '(course.renewal_type || \'未知\')',
                'context': 'renderRenewalContent'
            },
            {
                'name': '空值安全处理 - 退课',
                'pattern': '(refund.refund_sessions || 0)',
                'context': 'renderRefundContent'
            }
        ]
        
        print("✅ 模板文件读取成功")
        print("ℹ️ 正在检查修复项目...")
        
        all_fixed = True
        
        for fix in fixes_to_check:
            if fix['pattern'] in content:
                if fix['context'] in content:
                    print(f"✅ {fix['name']}: 已修复")
                else:
                    print(f"⚠️ {fix['name']}: 修复代码存在但上下文不匹配")
            else:
                print(f"❌ {fix['name']}: 未修复")
                all_fixed = False
        
        # 检查具体的修复代码段
        print("\n📋 详细修复检查:")
        
        # 检查JSON解析修复
        json_parse_fixed = (
            'try {' in content and
            'if (this.dataset.employeeName) {' in content and
            'employeeName = JSON.parse(this.dataset.employeeName);' in content and
            'catch (e) {' in content and
            'employeeName = this.dataset.employeeName || \'\';' in content
        )
        
        print(f"🔧 JSON解析安全处理: {'✅ 完整' if json_parse_fixed else '❌ 不完整'}")
        
        # 检查数据兼容性修复
        data_compat_fixed = (
            'const students = data.students || data.data || []' in content
        )
        
        print(f"🔧 数据结构兼容性: {'✅ 完整' if data_compat_fixed else '❌ 不完整'}")
        
        # 检查错误处理修复
        error_handling_fixed = (
            'if (!response.ok) {' in content and
            'throw new Error(' in content
        )
        
        print(f"🔧 API错误处理: {'✅ 完整' if error_handling_fixed else '❌ 不完整'}")
        
        # 总结
        print("\n" + "=" * 60)
        if all_fixed and json_parse_fixed and data_compat_fixed and error_handling_fixed:
            print("🎉 所有修复都已正确应用！")
            print("📝 修复包括:")
            print("   • JSON解析安全处理 (防止null值错误)")
            print("   • API数据结构兼容性处理")
            print("   • 增强的HTTP错误处理")
            print("   • 所有渲染函数的空值安全处理")
            print("\n💡 这些修复应该解决了原始的JSON解析错误")
            return True
        else:
            print("⚠️ 部分修复可能不完整，建议检查代码")
            return False
            
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return False

if __name__ == '__main__':
    success = check_fixes()
    print(f"\n📊 验证结果: {'通过' if success else '失败'}")
    exit(0 if success else 1)