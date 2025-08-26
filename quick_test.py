#!/usr/bin/env python3
"""快速测试修复是否生效"""

from app import create_app

app = create_app()

with app.test_client() as client:
    # 测试profit-report路由
    response = client.get('/api/profit-report?period=month')
    if response.status_code == 200:
        print("✅ /api/profit-report 路由正常")
    else:
        print(f"❌ /api/profit-report 返回 {response.status_code}")
    
    # 测试profit-config路由
    response = client.post('/api/profit-config', data={
        'new_course_shareholder_a': '50'
    })
    if response.status_code == 200:
        print("✅ /api/profit-config 路由正常")
    else:
        print(f"❌ /api/profit-config 返回 {response.status_code}")

print("\n测试完成！")
