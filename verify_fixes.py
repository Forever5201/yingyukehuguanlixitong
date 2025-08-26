#!/usr/bin/env python3
"""验证修复是否成功"""

from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig

app = create_app()

with app.app_context():
    print("检查数据库连接...")
    try:
        # 测试数据库查询
        Config.query.first()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
    
    print("\n检查路由...")
    with app.test_client() as client:
        # 测试各个路由
        tests = [
            ('/api/profit-report?period=month', 'GET', None),
            ('/api/profit-config', 'POST', {'new_course_shareholder_a': '50'}),
            ('/api/employees/9999/performance', 'GET', None),  # 不存在的员工
            ('/api/employees/9999/commission-config', 'POST', {'commission_type': 'profit'})
        ]
        
        for url, method, data in tests:
            try:
                if method == 'GET':
                    response = client.get(url)
                else:
                    response = client.post(url, data=data)
                
                if response.status_code in [200, 404]:
                    print(f"✅ {method} {url} -> {response.status_code}")
                else:
                    print(f"⚠️  {method} {url} -> {response.status_code}")
            except Exception as e:
                print(f"❌ {method} {url} -> 错误: {e}")

print("\n验证完成！")
