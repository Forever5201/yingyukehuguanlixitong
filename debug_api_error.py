#!/usr/bin/env python3
"""
调试API错误的脚本
"""

import requests
import json

def debug_api_error():
    """调试API错误"""
    base_url = "http://localhost:5000"
    
    print("🔍 调试API错误...")
    print("=" * 40)
    
    # 测试数据
    test_cost = {
        'cost_type': '房租',
        'cost_name': '测试房租费用',
        'amount': 5000.00,
        'cost_date': '2024-01-15',
        'billing_period': '月',
        'allocation_method': 'proportional',
        'allocated_to_courses': True,
        'description': '这是测试用的房租费用',
        'supplier': '测试房东',
        'invoice_number': 'TEST001'
    }
    
    print("📤 发送测试数据:")
    print(json.dumps(test_cost, indent=2, ensure_ascii=False))
    print()
    
    try:
        # 发送POST请求
        response = requests.post(
            f"{base_url}/api/operational-costs",
            json=test_cost,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            print("✅ 请求成功")
            try:
                data = response.json()
                print(f"✅ 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"✅ 响应内容: {response.text}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            
            try:
                error_data = response.json()
                print(f"❌ 错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ 错误响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_error()
