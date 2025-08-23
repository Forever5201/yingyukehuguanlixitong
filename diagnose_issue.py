#!/usr/bin/env python3
"""
诊断脚本 - 分析为什么测试中路由返回404
"""

from app import create_app, db
from app.models import Config, Employee
import sys

def test_different_scenarios():
    """测试不同场景下的路由行为"""
    
    print("=" * 80)
    print("诊断测试路由404问题")
    print("=" * 80)
    
    # 场景1：正常创建app
    print("\n场景1：正常创建app")
    app1 = create_app()
    with app1.app_context():
        print(f"  路由数量: {len(list(app1.url_map.iter_rules()))}")
        
        # 测试路由
        with app1.test_client() as client:
            response = client.get('/api/profit-report?period=month')
            print(f"  /api/profit-report -> {response.status_code}")
            if response.status_code == 200 and response.data:
                print(f"  响应: {response.data[:100]}...")
    
    # 场景2：修改配置后创建app（模拟测试环境）
    print("\n场景2：修改配置后创建app（模拟测试环境）")
    app2 = create_app()
    app2.config['TESTING'] = True
    app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app2.app_context():
        print(f"  路由数量: {len(list(app2.url_map.iter_rules()))}")
        
        # 创建数据库表
        db.create_all()
        
        # 测试路由
        with app2.test_client() as client:
            response = client.get('/api/profit-report?period=month')
            print(f"  /api/profit-report -> {response.status_code}")
            if response.status_code == 200 and response.data:
                print(f"  响应: {response.data[:100]}...")
    
    # 场景3：在app_context内外测试
    print("\n场景3：app_context内外测试对比")
    app3 = create_app()
    
    # 在context外测试
    print("  在app_context外:")
    client3 = app3.test_client()
    response = client3.get('/api/profit-report?period=month')
    print(f"    /api/profit-report -> {response.status_code}")
    
    # 在context内测试
    print("  在app_context内:")
    with app3.app_context():
        response = client3.get('/api/profit-report?period=month')
        print(f"    /api/profit-report -> {response.status_code}")
    
    # 场景4：检查路由函数
    print("\n场景4：检查路由函数是否存在")
    app4 = create_app()
    
    with app4.app_context():
        # 检查特定路由
        routes_to_check = [
            '/api/profit-report',
            '/api/profit-config',
            '/api/employees/<int:employee_id>/performance'
        ]
        
        for route_pattern in routes_to_check:
            found = False
            for rule in app4.url_map.iter_rules():
                if route_pattern.replace('<int:employee_id>', '1') == str(rule).replace('<int:employee_id>', '1'):
                    found = True
                    print(f"  ✓ {route_pattern} -> {rule.endpoint}")
                    
                    # 尝试获取视图函数
                    try:
                        view_func = app4.view_functions.get(rule.endpoint)
                        if view_func:
                            print(f"    函数: {view_func.__name__}")
                        else:
                            print(f"    ❌ 找不到视图函数!")
                    except Exception as e:
                        print(f"    错误: {e}")
                    break
            
            if not found:
                print(f"  ❌ {route_pattern} 未找到!")
    
    # 场景5：直接调用路由函数
    print("\n场景5：尝试直接调用路由函数")
    app5 = create_app()
    
    with app5.app_context():
        try:
            # 尝试导入并调用
            from app.routes import get_profit_report
            print(f"  get_profit_report函数存在: {get_profit_report}")
            
            # 模拟请求上下文
            with app5.test_request_context('/api/profit-report?period=month'):
                result = get_profit_report()
                print(f"  直接调用结果: {type(result)}")
        except Exception as e:
            print(f"  错误: {e}")
    
    # 场景6：检查是否有装饰器问题
    print("\n场景6：检查路由装饰器")
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 查找profit-report路由定义
        import re
        pattern = r'@app\.route\([\'"]([^\'"]*/profit-report[^\'"]*)[\'"]\)'
        matches = re.findall(pattern, content)
        
        if matches:
            print(f"  找到profit-report路由定义: {matches}")
        else:
            print("  ❌ 未找到profit-report路由定义!")
    
    print("\n" + "=" * 80)
    print("诊断总结")
    print("=" * 80)
    
    # 检查sys.modules
    print("\n已加载的app相关模块:")
    for module_name in sorted(sys.modules.keys()):
        if 'app' in module_name and not module_name.startswith('_'):
            print(f"  {module_name}")


if __name__ == '__main__':
    test_different_scenarios()