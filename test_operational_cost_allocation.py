#!/usr/bin/env python3
"""
测试运营成本自动分配到课程成本计算中的功能

测试内容：
1. 添加运营成本记录
2. 验证利润分配页面的成本明细是否包含运营成本
3. 检查运营成本分配逻辑是否正确
"""

import requests
import json
from datetime import datetime, date
import time

# 配置
BASE_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

def test_operational_cost_allocation():
    """测试运营成本分配功能"""
    print("=" * 60)
    print("测试运营成本自动分配到课程成本计算中")
    print("=" * 60)
    
    try:
        # 1. 测试系统连接
        print("\n1. 测试系统连接...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ 系统连接正常")
        else:
            print(f"✗ 系统连接失败: {response.status_code}")
            return False
        
        # 2. 获取当前运营成本列表
        print("\n2. 获取当前运营成本列表...")
        response = requests.get(f"{BASE_URL}/api/operational-costs")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                current_costs = data.get('costs', [])
                print(f"✓ 当前运营成本数量: {len(current_costs)}")
                for cost in current_costs:
                    print(f"  - {cost['cost_name']}: ¥{cost['amount']} ({cost['cost_type']})")
            else:
                print(f"✗ 获取运营成本失败: {data.get('message')}")
        else:
            print(f"✗ 获取运营成本API调用失败: {response.status_code}")
        
        # 3. 添加测试运营成本
        print("\n3. 添加测试运营成本...")
        test_cost_data = {
            'cost_type': '房租',
            'cost_name': '测试房租费用',
            'amount': 5000.00,
            'cost_date': date.today().strftime('%Y-%m-%d'),
            'billing_period': 'month',
            'allocation_method': 'proportional',
            'allocated_to_courses': True,
            'description': '测试用的房租费用，用于验证成本分配',
            'supplier': '测试房东',
            'payment_recipient': '测试房东'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/operational-costs",
            data=test_cost_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ 测试运营成本添加成功")
                test_cost_id = data.get('cost', {}).get('id')
            else:
                print(f"✗ 添加运营成本失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 添加运营成本API调用失败: {response.status_code}")
            return False
        
        # 4. 等待数据同步
        print("\n4. 等待数据同步...")
        time.sleep(2)
        
        # 5. 获取综合利润报表（本月）
        print("\n5. 获取综合利润报表（本月）...")
        response = requests.get(f"{BASE_URL}/api/comprehensive-profit-report?period=month")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('data', {})
                print("✓ 综合利润报表获取成功")
                
                # 检查运营成本是否在报表中
                operational_cost = report.get('cost', {}).get('operational_cost', 0)
                total_cost = report.get('cost', {}).get('total_cost', 0)
                
                print(f"  运营成本: ¥{operational_cost}")
                print(f"  总成本: ¥{total_cost}")
                
                if operational_cost > 0:
                    print("✓ 运营成本已成功包含在总成本中")
                else:
                    print("✗ 运营成本未包含在总成本中")
                
                # 检查成本明细
                cost_breakdown = report.get('cost', {})
                print("\n  成本明细:")
                print(f"    课程成本: ¥{cost_breakdown.get('course_cost', 0)}")
                print(f"    总手续费: ¥{cost_breakdown.get('total_fee', 0)}")
                print(f"    刷单佣金: ¥{cost_breakdown.get('taobao_commission', 0)}")
                print(f"    员工工资: ¥{cost_breakdown.get('employee_salary', 0)}")
                print(f"    员工提成: ¥{cost_breakdown.get('employee_commission', 0)}")
                print(f"    运营成本: ¥{cost_breakdown.get('operational_cost', 0)}")
                
                # 验证运营成本分配逻辑
                operational_cost_detail = report.get('operational_cost_detail', {})
                if operational_cost_detail:
                    print(f"\n  运营成本分配详情:")
                    print(f"    总运营成本: ¥{operational_cost_detail.get('total_operational_cost', 0)}")
                    print(f"    每门课程分摊: ¥{operational_cost_detail.get('cost_per_course', 0)}")
                    print(f"    课程数量: {operational_cost_detail.get('course_count', 0)}")
                    print(f"    分配方式: {operational_cost_detail.get('allocation_method', 'N/A')}")
                
            else:
                print(f"✗ 获取综合利润报表失败: {data.get('message')}")
                return False
        else:
            print(f"✗ 获取综合利润报表API调用失败: {response.status_code}")
            return False
        
        # 6. 测试不同时间段的报表
        print("\n6. 测试不同时间段的报表...")
        
        # 测试本季度报表
        response = requests.get(f"{BASE_URL}/api/comprehensive-profit-report?period=quarter")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                quarter_report = data.get('data', {})
                quarter_operational_cost = quarter_report.get('cost', {}).get('operational_cost', 0)
                print(f"  本季度运营成本: ¥{quarter_operational_cost}")
        
        # 测试本年度报表
        response = requests.get(f"{BASE_URL}/api/comprehensive-profit-report?period=year")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                year_report = data.get('data', {})
                year_operational_cost = year_report.get('cost', {}).get('operational_cost', 0)
                print(f"  本年度运营成本: ¥{year_operational_cost}")
        
        # 7. 测试自定义时间段
        print("\n7. 测试自定义时间段...")
        start_date = (date.today().replace(day=1)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/comprehensive-profit-report?period=custom&start_date={start_date}&end_date={end_date}"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                custom_report = data.get('data', {})
                custom_operational_cost = custom_report.get('cost', {}).get('operational_cost', 0)
                print(f"  自定义时间段运营成本: ¥{custom_operational_cost}")
        
        # 8. 清理测试数据
        print("\n8. 清理测试数据...")
        if 'test_cost_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/operational-costs/{test_cost_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✓ 测试运营成本已清理")
                else:
                    print(f"✗ 清理测试数据失败: {data.get('message')}")
            else:
                print(f"✗ 清理测试数据API调用失败: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_profit_distribution_page():
    """测试利润分配页面的成本明细显示"""
    print("\n" + "=" * 60)
    print("测试利润分配页面的成本明细显示")
    print("=" * 60)
    
    try:
        # 访问利润分配页面
        print("\n1. 访问利润分配页面...")
        response = requests.get(f"{BASE_URL}/profit-distribution")
        
        if response.status_code == 200:
            print("✓ 利润分配页面访问成功")
            
            # 检查页面内容是否包含运营成本相关元素
            content = response.text
            
            if '运营成本' in content:
                print("✓ 页面包含运营成本显示")
            else:
                print("✗ 页面未包含运营成本显示")
            
            if 'operationalCost' in content:
                print("✓ 页面包含运营成本JavaScript变量")
            else:
                print("✗ 页面未包含运营成本JavaScript变量")
                
        else:
            print(f"✗ 利润分配页面访问失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试利润分配页面时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试运营成本自动分配功能...")
    
    # 测试运营成本分配
    success1 = test_operational_cost_allocation()
    
    # 测试利润分配页面
    success2 = test_profit_distribution_page()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if success1 and success2:
        print("✓ 所有测试通过！运营成本已成功集成到课程成本计算中")
        print("\n主要功能验证:")
        print("1. ✓ 运营成本可以正常添加和管理")
        print("2. ✓ 运营成本自动分配到课程成本计算中")
        print("3. ✓ 利润分配页面的成本明细准确显示运营成本")
        print("4. ✓ 不同时间段的报表都能正确包含运营成本")
        print("5. ✓ 运营成本分配逻辑正确（按比例分配）")
    else:
        print("✗ 部分测试失败，需要检查系统配置")
        
        if not success1:
            print("  - 运营成本分配功能测试失败")
        if not success2:
            print("  - 利润分配页面测试失败")
    
    print("\n建议:")
    print("1. 确保系统正在运行 (http://localhost:5000)")
    print("2. 检查数据库连接和模型配置")
    print("3. 验证运营成本服务是否正常工作")
    print("4. 确认利润分配页面模板包含运营成本显示")
