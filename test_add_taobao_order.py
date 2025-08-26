#!/usr/bin/env python3
"""
测试添加新的刷单记录
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_add_taobao_order():
    """测试添加新的刷单记录"""
    print("🧪 测试添加新的刷单记录...")
    
    # 测试数据
    test_data = {
        'customer_name': '测试客户',
        'level': '皇冠1',
        'product_name': '英语课程A',  # 使用预设的商品
        'amount': '39.9',
        'commission': '5.0',
        'evaluated': 'on',
        'order_time': datetime.now().strftime('%Y-%m-%dT%H:%M')
    }
    
    try:
        print(f"📝 添加测试记录:")
        print(f"  客户姓名: {test_data['customer_name']}")
        print(f"  等级: {test_data['level']}")
        print(f"  商品名称: {test_data['product_name']}")
        print(f"  金额: ¥{test_data['amount']}")
        print(f"  佣金: ¥{test_data['commission']}")
        
        # 发送POST请求添加记录
        response = requests.post(f"{BASE_URL}/taobao-orders", data=test_data)
        
        if response.status_code == 200:
            print("✓ 刷单记录添加成功")
            
            # 验证记录是否正确保存
            print("\n🔍 验证记录是否正确保存...")
            verify_response = requests.get(f"{BASE_URL}/taobao-orders")
            
            if verify_response.status_code == 200:
                html_content = verify_response.text
                
                # 检查是否包含新添加的记录
                if test_data['customer_name'] in html_content:
                    print("✓ 新记录在页面中可见")
                    
                    # 检查商品名称是否正确
                    if test_data['product_name'] in html_content:
                        print("✓ 商品名称正确显示")
                    else:
                        print("❌ 商品名称未正确显示")
                else:
                    print("❌ 新记录在页面中不可见")
            else:
                print("❌ 无法验证记录")
        else:
            print(f"❌ 刷单记录添加失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print("\n📝 说明:")
    print("- 如果测试成功，说明新添加的刷单记录会正确显示预设的商品")
    print("- 现有的空商品名称记录是历史数据，不影响新记录")
    print("- 您可以在刷单管理页面查看新添加的记录")

if __name__ == "__main__":
    test_add_taobao_order()

