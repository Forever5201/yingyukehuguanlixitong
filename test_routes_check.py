#!/usr/bin/env python3
"""
检查路由是否正确加载的测试脚本
"""

from app import create_app

def check_routes():
    """检查应用的路由"""
    app = create_app()
    
    print("应用中注册的所有路由：")
    print("=" * 80)
    
    routes = []
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and rule.endpoint != 'static':
            routes.append((rule.rule, rule.endpoint))
    
    # 按路径排序
    routes.sort()
    
    # 打印所有路由
    for path, endpoint in routes:
        print(f"{path:<50} -> {endpoint}")
    
    print("\n" + "=" * 80)
    print("检查测试所需的路由：")
    
    # 测试所需的路由
    test_routes = [
        '/api/profit-report',
        '/api/profit-config',
        '/api/employees/<int:employee_id>/performance',
        '/api/employees/<int:employee_id>/commission-config',
    ]
    
    for test_route in test_routes:
        found = False
        for path, _ in routes:
            if test_route.replace('<int:employee_id>', '1') == path.replace('<int:employee_id>', '1'):
                found = True
                break
        
        if found:
            print(f"✅ {test_route}")
        else:
            print(f"❌ {test_route} - 未找到")
    
    # 测试一个实际的请求
    print("\n" + "=" * 80)
    print("测试实际请求：")
    
    with app.test_client() as client:
        response = client.get('/api/profit-report?period=month')
        print(f"GET /api/profit-report?period=month -> 状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 路由正常工作")
        else:
            print("❌ 路由返回错误")
            if response.data:
                print(f"响应内容: {response.data.decode('utf-8')[:200]}...")

if __name__ == '__main__':
    check_routes()