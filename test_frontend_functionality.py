#!/usr/bin/env python3
"""
测试前端功能的脚本
"""

import requests
from datetime import datetime

def test_frontend_functionality():
    """测试前端功能"""
    base_url = "http://localhost:5000"
    
    print("🚀 开始测试前端功能...")
    print("=" * 50)
    
    # 1. 测试系统配置页面
    print("1. 测试系统配置页面...")
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            print("✅ 系统配置页面访问成功")
            # 检查是否包含运营成本相关的内容
            content = response.text
            if "运营成本管理" in content:
                print("✅ 运营成本管理标签页存在")
            else:
                print("❌ 运营成本管理标签页缺失")
                
            if "新增成本" in content:
                print("✅ 新增成本按钮存在")
            else:
                print("❌ 新增成本按钮缺失")
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 2. 测试利润分配页面
    print("2. 测试利润分配页面...")
    try:
        response = requests.get(f"{base_url}/profit-distribution")
        if response.status_code == 200:
            print("✅ 利润分配页面访问成功")
            # 检查是否包含运营成本相关的内容
            content = response.text
            if "运营成本" in content:
                print("✅ 运营成本显示正常")
            else:
                print("❌ 运营成本显示缺失")
        else:
            print(f"❌ 利润分配页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 3. 测试综合利润报表API（包含运营成本）
    print("3. 测试综合利润报表API（包含运营成本）...")
    try:
        response = requests.get(f"{base_url}/api/comprehensive-profit-report?period=month")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 综合利润报表API访问成功")
                # 检查是否包含运营成本
                report_data = data.get('data', {})
                if 'operational_cost_detail' in report_data:
                    print("✅ 运营成本已集成到利润计算中")
                    operational_cost = report_data.get('cost', {}).get('operational_cost', 0)
                    print(f"   - 运营成本金额: ¥{operational_cost:,.2f}")
                    
                    # 显示更多详细信息
                    operational_detail = report_data.get('operational_cost_detail', {})
                    if operational_detail:
                        print(f"   - 运营成本详情:")
                        print(f"     * 总运营成本: ¥{operational_detail.get('total_operational_cost', 0):,.2f}")
                        print(f"     * 成本项目数: {operational_detail.get('cost_count', 0)}")
                        
                        # 显示成本类型分布
                        cost_by_type = operational_detail.get('cost_by_type', {})
                        if cost_by_type:
                            for cost_type, info in cost_by_type.items():
                                print(f"       - {cost_type}: ¥{info['amount']:,.2f} ({info['count']}项)")
                else:
                    print("❌ 运营成本未集成到利润计算中")
            else:
                print(f"❌ 综合利润报表API失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 综合利润报表API访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    
    # 4. 测试运营成本统计API
    print("4. 测试运营成本统计API...")
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
                print("✅ 运营成本统计API访问成功")
                print(f"   - 总成本: ¥{stats.get('total_amount', 0):,.2f}")
                print(f"   - 成本项目数: {stats.get('cost_count', 0)}")
                
                # 检查成本类型分布
                cost_by_type = stats.get('cost_by_type', {})
                if cost_by_type:
                    print("   - 成本类型分布:")
                    for cost_type, info in cost_by_type.items():
                        print(f"     * {cost_type}: ¥{info['amount']:,.2f} ({info['count']}项)")
                else:
                    print("   - 本月暂无运营成本数据")
            else:
                print(f"❌ 运营成本统计API失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 运营成本统计API访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    print("=" * 50)
    print("🎉 前端功能测试完成！")

if __name__ == "__main__":
    test_frontend_functionality()
