#!/usr/bin/env python
"""
查找并清理重复的路由定义
"""
import re
from collections import defaultdict

def find_duplicate_routes(filename):
    """查找文件中的重复路由"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有路由定义
    route_pattern = r'@app\.route\((.*?)\)\s*\ndef\s+(\w+)'
    routes = re.findall(route_pattern, content, re.DOTALL)
    
    # 统计路由
    route_map = defaultdict(list)
    func_map = defaultdict(list)
    
    for route, func_name in routes:
        # 清理路由字符串
        route = route.strip()
        route_map[route].append(func_name)
        func_map[func_name].append(route)
    
    # 查找重复
    duplicate_routes = {}
    duplicate_funcs = {}
    
    for route, funcs in route_map.items():
        if len(funcs) > 1:
            duplicate_routes[route] = funcs
    
    for func, routes in func_map.items():
        if len(routes) > 1:
            duplicate_funcs[func] = routes
    
    return duplicate_routes, duplicate_funcs

def main():
    print("="*60)
    print("查找重复的路由定义")
    print("="*60)
    
    duplicate_routes, duplicate_funcs = find_duplicate_routes('app/routes.py')
    
    if duplicate_routes:
        print("\n发现重复的路由定义：")
        for route, funcs in duplicate_routes.items():
            print(f"\n路由: {route}")
            print(f"  函数: {', '.join(funcs)}")
    
    if duplicate_funcs:
        print("\n发现重复的函数名：")
        for func, routes in duplicate_funcs.items():
            print(f"\n函数: {func}")
            print(f"  路由: {', '.join(routes)}")
    
    if not duplicate_routes and not duplicate_funcs:
        print("\n✅ 没有发现重复的路由定义")
    else:
        print("\n❌ 请手动检查并删除重复的定义")
        print("\n建议：")
        print("1. 保留功能更完整的版本")
        print("2. 确保API的一致性")
        print("3. 删除简单的重复版本")

if __name__ == "__main__":
    main()