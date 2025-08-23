#!/usr/bin/env python
"""
修复模型字段相关的问题
"""
import re

def fix_model_issues():
    """修复所有模型字段相关的问题"""
    
    # 读取文件
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复 base_cost -> cost
    content = content.replace('course.base_cost', 'course.cost')
    
    # 2. 删除不存在的字段引用
    # 替换 base_cost_per_session 相关的计算
    pattern1 = r"""# 计算成本（使用基础成本和自定义成本）
            base_cost = \(course\.sessions \+ course\.gift_sessions\) \* course\.base_cost_per_session if course\.base_cost_per_session else 0
            custom_cost = course\.custom_course_cost if course\.custom_course_cost else 0
            course_cost = base_cost if course\.use_base_cost else custom_cost"""
    replacement1 = """# 计算成本
            course_cost = course.cost if course.cost else 0"""
    content = re.sub(pattern1, replacement1, content)
    
    # 3. 删除创建课程时的不存在字段
    fields_to_remove = [
        'base_cost_per_session',
        'use_base_cost',
        'snapshot_fee_rate'
    ]
    
    for field in fields_to_remove:
        # 删除字段赋值
        pattern = rf"\s*{field}=data\.get\('{field}'\),?\s*\n"
        content = re.sub(pattern, '', content)
        pattern = rf"\s*{field}=data\['{field}'\],?\s*\n"
        content = re.sub(pattern, '', content)
        # 删除表单字段获取
        pattern = rf"\s*course\.{field} = .*\n"
        content = re.sub(pattern, '', content)
    
    # 4. 修复多余的逗号
    content = re.sub(r',(\s*\))', r'\1', content)
    
    # 写回文件
    with open('app/routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 模型字段问题修复完成")

if __name__ == "__main__":
    fix_model_issues()