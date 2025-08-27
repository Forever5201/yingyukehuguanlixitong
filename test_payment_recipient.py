#!/usr/bin/env python3
"""
测试运营成本支付对象字段的脚本
"""

import requests
import json

def test_payment_recipient():
    """测试支付对象字段"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试运营成本支付对象字段...")
    print("=" * 50)
    
    try:
        # 测试创建运营成本（包含支付对象）
        test_cost = {
            'cost_type': '房租',
            'cost_name': '测试房租费用',
            'amount': 5000.00,
            'cost_date': '2025-01-01',
            'billing_period': 'month',
            'allocation_method': 'proportional',
            'allocated_to_courses': True,
            'description': '测试房租费用，包含支付对象字段',
            'invoice_number': 'TEST001',
            'supplier': '测试房东',
            'payment_recipient': '房东张三',  # 新增的支付对象字段
            'status': 'active'
        }
        
        print("📝 测试数据:")
        print(f"   - 成本类型: {test_cost['cost_type']}")
        print(f"   - 成本名称: {test_cost['cost_name']}")
        print(f"   - 金额: ¥{test_cost['amount']:.2f}")
        print(f"   - 供应商: {test_cost['supplier']}")
        print(f"   - 支付对象: {test_cost['payment_recipient']}")
        
        # 发送POST请求创建运营成本
        response = requests.post(
            f"{base_url}/api/operational-costs",
            json=test_cost,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📡 API响应状态: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ 运营成本创建成功")
            
            result = response.json()
            if result.get('success'):
                cost_data = result.get('cost', {})
                print("\n📊 返回的成本数据:")
                print(f"   - ID: {cost_data.get('id')}")
                print(f"   - 成本类型: {cost_data.get('cost_type')}")
                print(f"   - 成本名称: {cost_data.get('cost_name')}")
                print(f"   - 金额: ¥{cost_data.get('amount')}")
                print(f"   - 供应商: {cost_data.get('supplier')}")
                print(f"   - 支付对象: {cost_data.get('payment_recipient')}")
                
                # 验证支付对象字段是否正确返回
                if cost_data.get('payment_recipient') == '房东张三':
                    print("✅ 支付对象字段正确返回")
                else:
                    print("❌ 支付对象字段返回错误")
                    print(f"   期望: 房东张三")
                    print(f"   实际: {cost_data.get('payment_recipient')}")
                
                # 测试获取运营成本列表
                print("\n📋 测试获取运营成本列表...")
                list_response = requests.get(f"{base_url}/api/operational-costs")
                
                if list_response.status_code == 200:
                    list_result = list_response.json()
                    if list_result.get('success'):
                        costs = list_result.get('costs', [])
                        print(f"✅ 获取到 {len(costs)} 条运营成本记录")
                        
                        # 查找刚创建的记录
                        new_cost = None
                        for cost in costs:
                            if cost.get('cost_name') == '测试房租费用':
                                new_cost = cost
                                break
                        
                        if new_cost:
                            print("✅ 找到新创建的记录")
                            print(f"   - 支付对象: {new_cost.get('payment_recipient')}")
                        else:
                            print("❌ 未找到新创建的记录")
                    else:
                        print(f"❌ 获取列表失败: {list_result.get('message')}")
                else:
                    print(f"❌ 获取列表请求失败: {list_response.status_code}")
                
            else:
                print(f"❌ 创建失败: {result.get('message')}")
        else:
            print(f"❌ 创建请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    
    print()
    print("🎉 支付对象字段测试完成！")
    return True

if __name__ == "__main__":
    test_payment_recipient()


