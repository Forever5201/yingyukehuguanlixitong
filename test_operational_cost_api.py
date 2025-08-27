#!/usr/bin/env python3
"""
测试运营成本API接口的脚本
"""

import requests
import json
from datetime import datetime

def test_operational_cost_api():
    """测试运营成本API接口"""
    base_url = "http://localhost:5000"
    
    print("🚀 开始测试运营成本API接口...")
    print("=" * 50)
    
    # 1. 测试获取运营成本列表
    print("1. 测试获取运营成本列表...")
    try:
        response = requests.get(f"{base_url}/api/operational-costs")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 获取成功，共 {data.get('total_count', 0)} 条记录")
                costs = data.get('costs', [])
                for cost in costs[:3]:  # 只显示前3条
                    print(f"   - {cost['cost_type']}: {cost['cost_name']} ¥{cost['amount']}")
            else:
                print(f"❌ 获取失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 2. 测试获取运营成本统计
    print("2. 测试获取运营成本统计...")
    try:
        # 获取本月统计
        now = datetime.now()
        month_start = now.replace(day=1).strftime('%Y-%m-%d')
        month_end = now.strftime('%Y-%m-%d')
        
        response = requests.get(f"{base_url}/api/operational-costs/statistics?start_date={month_start}&end_date={month_end}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"✅ 统计获取成功")
                print(f"   - 总成本: ¥{stats.get('total_amount', 0):,.2f}")
                print(f"   - 成本项目数: {stats.get('cost_count', 0)}")
            else:
                print(f"❌ 统计获取失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 3. 测试获取选项配置
    print("3. 测试获取选项配置...")
    try:
        response = requests.get(f"{base_url}/api/operational-costs/options")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 选项获取成功")
                print(f"   - 成本类型: {', '.join(data.get('cost_types', []))}")
                print(f"   - 计费周期: {', '.join(data.get('billing_periods', []))}")
            else:
                print(f"❌ 选项获取失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 4. 测试创建运营成本
    print("4. 测试创建运营成本...")
    try:
        test_cost_data = {
            'cost_type': '测试成本',
            'cost_name': 'API测试成本',
            'amount': 100.00,
            'cost_date': datetime.now().strftime('%Y-%m-%d'),
            'billing_period': 'one-time',
            'allocation_method': 'proportional',
            'allocated_to_courses': True,
            'description': '这是通过API测试创建的运营成本',
            'supplier': '测试供应商'
        }
        
        response = requests.post(f"{base_url}/api/operational-costs", data=test_cost_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 创建成功，成本ID: {data.get('cost_id')}")
                test_cost_id = data.get('cost_id')
                
                # 5. 测试更新运营成本
                print("5. 测试更新运营成本...")
                update_data = {
                    'cost_name': 'API测试成本-已更新',
                    'amount': 150.00,
                    'description': '这是更新后的描述'
                }
                
                response = requests.put(f"{base_url}/api/operational-costs/{test_cost_id}", 
                                     json=update_data,
                                     headers={'Content-Type': 'application/json'})
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ 更新成功")
                    else:
                        print(f"❌ 更新失败: {data.get('message', '未知错误')}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                
                # 6. 测试删除运营成本
                print("6. 测试删除运营成本...")
                response = requests.delete(f"{base_url}/api/operational-costs/{test_cost_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ 删除成功")
                    else:
                        print(f"❌ 删除失败: {data.get('message', '未知错误')}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                
            else:
                print(f"❌ 创建失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    print("=" * 50)
    print("🎉 API接口测试完成！")

if __name__ == "__main__":
    test_operational_cost_api()

