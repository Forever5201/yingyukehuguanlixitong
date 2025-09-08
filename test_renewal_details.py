#!/usr/bin/env python3
"""
测试续课信息页面计算明细功能的脚本
"""

import requests
from datetime import datetime

def test_renewal_details():
    """测试续课信息页面"""
    base_url = "http://localhost:5000"
    
    print("🚀 开始测试续课信息页面计算明细功能...")
    print("=" * 60)
    
    # 测试正课详情页面（包含续课信息）
    print("1. 测试正课详情页面...")
    try:
        # 使用您提到的课程ID 18
        response = requests.get(f"{base_url}/formal-courses/18/details")
        if response.status_code == 200:
            print("✅ 正课详情页面访问成功")
            
            content = response.text
            
            # 检查是否包含续课信息
            if "续课信息" in content:
                print("✅ 续课信息部分存在")
            else:
                print("❌ 续课信息部分缺失")
                return
            
            # 检查是否包含计算明细
            if "计算明细" in content:
                print("✅ 续课计算明细部分存在")
            else:
                print("❌ 续课计算明细部分缺失")
                return
            
            # 检查计算明细的具体内容
            if "收入计算" in content:
                print("✅ 收入计算部分存在")
            else:
                print("❌ 收入计算部分缺失")
            
            if "成本计算" in content:
                print("✅ 成本计算部分存在")
            else:
                print("❌ 成本计算部分缺失")
            
            if "利润计算" in content:
                print("✅ 利润计算部分存在")
            else:
                print("❌ 利润计算部分缺失")
            
            # 检查具体的计算字段
            calculation_fields = [
                "续课节数", "单节价格", "基础收入", "实际收入",
                "单节成本", "课时成本", "其他成本", "手续费", "总成本",
                "净利润", "利润率"
            ]
            
            missing_fields = []
            for field in calculation_fields:
                if field in content:
                    print(f"✅ {field} 字段存在")
                else:
                    print(f"❌ {field} 字段缺失")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n⚠️  缺失的字段: {', '.join(missing_fields)}")
            else:
                print("\n🎉 所有计算明细字段都存在！")
            
        else:
            print(f"❌ 正课详情页面访问失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return
    
    print()
    
    # 测试API接口
    print("2. 测试正课API接口...")
    try:
        response = requests.get(f"{base_url}/api/formal-courses/18")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 正课API接口访问成功")
                
                # 检查续课信息
                renewal_courses = data.get('renewal_courses', [])
                print(f"   - 续课记录数量: {len(renewal_courses)}")
                
                if renewal_courses:
                    print("   - 续课记录详情:")
                    for i, renewal in enumerate(renewal_courses, 1):
                        print(f"     续课 {i}:")
                        print(f"       - 课程类型: {renewal.get('course_type')}")
                        print(f"       - 续课节数: {renewal.get('sessions')} 节")
                        print(f"       - 单节价格: ¥{renewal.get('price', 0):.2f}")
                        print(f"       - 其他成本: ¥{renewal.get('other_cost', 0):.2f}")
                        print(f"       - 支付渠道: {renewal.get('payment_channel')}")
                        
                        # 检查是否包含成本信息
                        if 'cost' in renewal:
                            print(f"       - 单节成本: ¥{renewal.get('cost', 0):.2f}")
                        else:
                            print("       - 单节成本: 未设置")
                        
                        if 'fee' in renewal:
                            print(f"       - 手续费: ¥{renewal.get('fee', 0):.2f}")
                        else:
                            print("       - 手续费: 未设置")
                        
                        if 'total_cost' in renewal:
                            print(f"       - 总成本: ¥{renewal.get('total_cost', 0):.2f}")
                        else:
                            print("       - 总成本: 未设置")
                        
                        print()
                else:
                    print("   - 暂无续课记录")
            else:
                print(f"❌ 正课API接口失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 正课API接口访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    print("=" * 60)
    print("🎉 续课信息页面计算明细功能测试完成！")
    
    # 提供访问建议
    print("\n📋 访问建议:")
    print(f"   在浏览器中访问: {base_url}/formal-courses/18/details")
    print("   查看续课信息部分的计算明细是否正常显示")
    print("   检查收入计算、成本计算、利润计算是否完整")

if __name__ == "__main__":
    test_renewal_details()








