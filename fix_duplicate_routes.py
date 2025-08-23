#!/usr/bin/env python
"""
修复所有重复的路由定义
保留功能更完整的版本，删除简单的版本
"""
import re

def fix_duplicate_routes():
    """修复重复的路由"""
    
    # 读取文件内容
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要删除的函数列表（这些是简单版本，我们保留更完整的版本）
    functions_to_remove = [
        'update_customer_api',    # 保留 update_customer
        'delete_customer_api',    # 保留 delete_customer
        'get_customer_api',       # 保留 api_customer
        'api_formal_course',      # 保留 get_formal_course
        'api_trial_course',       # 保留 get_trial_course
    ]
    
    # 删除这些函数及其路由装饰器
    for func_name in functions_to_remove:
        # 构建正则表达式，匹配从路由装饰器到函数结束
        pattern = rf'@app\.route\([^)]+\)\s*\ndef {func_name}\([^)]*\):[^@]*?(?=\n@app\.route|\n\nclass|\n\n#|\Z)'
        
        # 替换匹配的内容为空
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 清理多余的空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 写回文件
    with open('app/routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 重复路由已修复")
    
    # 验证修复结果
    from clean_duplicate_routes import find_duplicate_routes
    duplicate_routes, duplicate_funcs = find_duplicate_routes('app/routes.py')
    
    if duplicate_routes or duplicate_funcs:
        print("\n⚠️  仍有一些重复需要手动处理：")
        if duplicate_routes:
            print("\n重复的路由：")
            for route, funcs in duplicate_routes.items():
                print(f"  {route}: {', '.join(funcs)}")
        if duplicate_funcs:
            print("\n重复的函数：")
            for func, routes in duplicate_funcs.items():
                print(f"  {func}: {', '.join(routes)}")
    else:
        print("✅ 所有重复路由已成功清理")

if __name__ == "__main__":
    print("开始修复重复的路由...")
    fix_duplicate_routes()