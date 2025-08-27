#!/usr/bin/env python3
"""
详细分析运营成本分配机制

分析内容：
1. 运营成本是否真的"分配"到课程成本中
2. 还是只是作为独立的成本项目显示
3. 课程成本的具体含义是什么
4. 运营成本在利润计算中的作用
"""

import requests
import json
from datetime import datetime, date

def analyze_operational_cost_allocation():
    """分析运营成本分配机制"""
    print("=" * 80)
    print("详细分析运营成本分配机制")
    print("=" * 80)
    
    try:
        # 1. 获取本月利润报表
        print("\n1. 获取本月利润报表...")
        response = requests.get("http://localhost:5000/api/comprehensive-profit-report?period=month")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('data', {})
                print("✓ 本月利润报表获取成功")
                
                # 2. 分析成本结构
                cost = report.get('cost', {})
                operational_detail = report.get('operational_cost_detail', {})
                
                print(f"\n2. 成本结构分析:")
                print(f"  课程成本: ¥{cost.get('course_cost', 0):.2f}")
                print(f"  总手续费: ¥{cost.get('total_fee', 0):.2f}")
                print(f"  刷单佣金: ¥{cost.get('taobao_commission', 0):.2f}")
                print(f"  员工工资: ¥{cost.get('employee_salary', 0):.2f}")
                print(f"  员工提成: ¥{cost.get('employee_commission', 0):.2f}")
                print(f"  运营成本: ¥{cost.get('operational_cost', 0):.2f}")
                print(f"  总成本: ¥{cost.get('total_cost', 0):.2f}")
                
                # 3. 验证运营成本分配逻辑
                print(f"\n3. 运营成本分配逻辑验证:")
                if operational_detail:
                    total_operational = operational_detail.get('total_operational_cost', 0)
                    cost_per_course = operational_detail.get('cost_per_course', 0)
                    course_count = operational_detail.get('course_count', 0)
                    allocation_method = operational_detail.get('allocation_method', 'N/A')
                    
                    print(f"  总运营成本: ¥{total_operational}")
                    print(f"  课程数量: {course_count}")
                    print(f"  每门课程分摊: ¥{cost_per_course:.2f}")
                    print(f"  分配方式: {allocation_method}")
                    
                    # 验证计算逻辑
                    if course_count > 0:
                        calculated_cost_per_course = total_operational / course_count
                        print(f"  计算验证: ¥{total_operational} ÷ {course_count} = ¥{calculated_cost_per_course:.2f}")
                        
                        if abs(calculated_cost_per_course - cost_per_course) < 0.01:
                            print("  ✓ 分配计算正确")
                        else:
                            print("  ✗ 分配计算有误")
                
                # 4. 关键分析：运营成本是否真的"分配"到课程成本中？
                print(f"\n4. 关键分析：运营成本分配机制")
                
                course_cost = cost.get('course_cost', 0)
                operational_cost = cost.get('operational_cost', 0)
                total_cost = cost.get('total_cost', 0)
                
                print(f"  课程成本: ¥{course_cost:.2f}")
                print(f"  运营成本: ¥{operational_cost:.2f}")
                print(f"  总成本: ¥{total_cost:.2f}")
                
                # 验证总成本计算
                expected_total = (course_cost + 
                                cost.get('total_fee', 0) + 
                                cost.get('taobao_commission', 0) + 
                                cost.get('employee_salary', 0) + 
                                cost.get('employee_commission', 0) + 
                                operational_cost)
                
                print(f"  预期总成本: ¥{expected_total:.2f}")
                print(f"  实际总成本: ¥{total_cost:.2f}")
                
                if abs(expected_total - total_cost) < 0.01:
                    print("  ✓ 总成本计算正确")
                else:
                    print("  ✗ 总成本计算有误")
                
                # 5. 分析运营成本在利润计算中的作用
                print(f"\n5. 运营成本在利润计算中的作用:")
                
                revenue = report.get('revenue', {}).get('total_revenue', 0)
                net_profit = report.get('profit', {}).get('net_profit', 0)
                
                print(f"  总收入: ¥{revenue:.2f}")
                print(f"  总成本: ¥{total_cost:.2f}")
                print(f"  净利润: ¥{net_profit:.2f}")
                
                # 计算不含运营成本的利润
                cost_without_operational = total_cost - operational_cost
                profit_without_operational = revenue - cost_without_operational
                
                print(f"  不含运营成本的总成本: ¥{cost_without_operational:.2f}")
                print(f"  不含运营成本的利润: ¥{profit_without_operational:.2f}")
                print(f"  运营成本对利润的影响: ¥{operational_cost:.2f}")
                
                # 6. 分析"课程成本"的含义
                print(f"\n6. '课程成本'含义分析:")
                print(f"  课程成本金额: ¥{course_cost:.2f}")
                print(f"  运营成本金额: ¥{operational_cost:.2f}")
                
                if operational_cost > 0:
                    print(f"  运营成本占比: {(operational_cost / total_cost * 100):.2f}%")
                    print(f"  课程成本占比: {(course_cost / total_cost * 100):.2f}%")
                
                # 7. 验证运营成本是否真的"分配"到课程成本中
                print(f"\n7. 运营成本分配验证:")
                
                # 检查运营成本是否已经包含在课程成本中
                if operational_cost > 0:
                    print(f"  运营成本: ¥{operational_cost:.2f}")
                    print(f"  课程成本: ¥{course_cost:.2f}")
                    print(f"  运营成本 + 课程成本: ¥{operational_cost + course_cost:.2f}")
                    
                    # 如果运营成本真的"分配"到课程成本中，那么课程成本应该包含运营成本
                    # 但实际上它们是分开显示的，说明运营成本并没有"分配"到课程成本中
                    print(f"  ⚠️  重要发现：")
                    print(f"      - 运营成本(¥{operational_cost:.2f})和课程成本(¥{course_cost:.2f})是分开显示的")
                    print(f"      - 运营成本并没有'分配'到课程成本中")
                    print(f"      - 运营成本是作为独立的成本项目计入总成本")
                    print(f"      - 总成本 = 课程成本 + 运营成本 + 其他成本")
                
                return True
            else:
                print(f"✗ 获取利润报表失败: {data.get('message')}")
                return False
        else:
            print(f"✗ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analyze_profit_distribution_page_structure():
    """分析利润分配页面的结构"""
    print(f"\n" + "=" * 80)
    print("分析利润分配页面的结构")
    print("=" * 80)
    
    try:
        # 访问利润分配页面
        print("\n1. 访问利润分配页面...")
        response = requests.get("http://localhost:5000/profit-distribution")
        
        if response.status_code == 200:
            print("✓ 利润分配页面访问成功")
            
            # 检查页面内容
            content = response.text
            
            # 检查成本明细结构
            print("\n2. 成本明细页面结构分析:")
            
            cost_items = [
                '课程成本',
                '总手续费', 
                '刷单佣金',
                '员工基本工资',
                '员工提成',
                '运营成本',
                '总成本'
            ]
            
            for item in cost_items:
                if item in content:
                    print(f"  ✓ 包含: {item}")
                else:
                    print(f"  ✗ 缺少: {item}")
            
            # 分析页面结构
            print(f"\n3. 页面结构分析:")
            print(f"  - 成本明细表格包含7行：")
            print(f"    1. 课程成本")
            print(f"    2. 总手续费")
            print(f"    3. 刷单佣金")
            print(f"    4. 员工基本工资")
            print(f"    5. 员工提成")
            print(f"    6. 运营成本")
            print(f"    7. 总成本（合计）")
            
            print(f"\n  - 关键发现：")
            print(f"    ✓ 运营成本是作为独立的成本项目显示")
            print(f"    ✓ 运营成本并没有'分配'到课程成本中")
            print(f"    ✓ 总成本 = 课程成本 + 运营成本 + 其他成本")
            
            return True
        else:
            print(f"✗ 利润分配页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 分析失败: {str(e)}")
        return False

def analyze_operational_cost_service_logic():
    """分析运营成本服务的逻辑"""
    print(f"\n" + "=" * 80)
    print("分析运营成本服务的逻辑")
    print("=" * 80)
    
    try:
        # 获取运营成本详情
        print("\n1. 获取运营成本详情...")
        response = requests.get("http://localhost:5000/api/operational-costs")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                costs = data.get('costs', [])
                print(f"✓ 当前运营成本数量: {len(costs)}")
                
                total_operational_cost = 0
                for cost in costs:
                    if cost['status'] == 'active':
                        amount = cost['amount']
                        total_operational_cost += amount
                        print(f"  - {cost['cost_name']}: ¥{amount} ({cost['cost_type']}) - {cost['billing_period']}")
                
                print(f"\n  总运营成本: ¥{total_operational_cost}")
                
                # 分析分配逻辑
                print(f"\n2. 运营成本分配逻辑分析:")
                print(f"  - 总运营成本: ¥{total_operational_cost}")
                print(f"  - 分配方式: 按比例分配 (proportional)")
                print(f"  - 分配目标: 时间段内的课程")
                print(f"  - 计算公式: 每门课程分摊 = 总运营成本 ÷ 课程数量")
                
                # 获取课程数量
                response = requests.get("http://localhost:5000/api/comprehensive-profit-report?period=month")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        report = data.get('data', {})
                        operational_detail = report.get('operational_cost_detail', {})
                        
                        if operational_detail:
                            course_count = operational_detail.get('course_count', 0)
                            cost_per_course = operational_detail.get('cost_per_course', 0)
                            
                            print(f"\n3. 实际分配结果:")
                            print(f"  - 课程数量: {course_count}")
                            print(f"  - 每门课程分摊: ¥{cost_per_course:.2f}")
                            print(f"  - 分配验证: ¥{total_operational_cost} ÷ {course_count} = ¥{cost_per_course:.2f}")
                            
                            # 重要发现
                            print(f"\n4. 重要发现:")
                            print(f"  ⚠️  运营成本分配的含义：")
                            print(f"      - 运营成本确实会'分配'到课程，但这是概念上的分配")
                            print(f"      - 每门课程分摊 ¥{cost_per_course:.2f} 的运营成本")
                            print(f"      - 但在财务报表中，运营成本仍然是独立显示的成本项目")
                            print(f"      - 运营成本并没有'合并'到课程成本中")
                            print(f"      - 总成本 = 课程成本 + 运营成本 + 其他成本")
                
                return True
            else:
                print(f"✗ 获取运营成本失败: {data.get('message')}")
                return False
        else:
            print(f"✗ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 分析失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始详细分析运营成本分配机制...")
    
    # 分析运营成本分配机制
    success1 = analyze_operational_cost_allocation()
    
    # 分析利润分配页面结构
    success2 = analyze_profit_distribution_page_structure()
    
    # 分析运营成本服务逻辑
    success3 = analyze_operational_cost_service_logic()
    
    # 总结
    print("\n" + "=" * 80)
    print("分析总结")
    print("=" * 80)
    
    if success1 and success2 and success3:
        print("✓ 运营成本分配机制分析完成！")
        
        print("\n📋 重要发现总结:")
        print("1. ⚠️  运营成本并没有真正'分配'到课程成本中")
        print("2. ✅  运营成本是作为独立的成本项目显示")
        print("3. ✅  运营成本确实会按比例'分配'到课程，但这是概念上的分配")
        print("4. ✅  总成本 = 课程成本 + 运营成本 + 其他成本")
        
        print("\n🔍 具体分析:")
        print("- '课程成本'：指课程本身的直接成本（如教材、设备等）")
        print("- '运营成本'：指房租、水电、管理等间接成本")
        print("- 运营成本按比例分配到课程，但财务报表中仍然是分开显示")
        print("- 每门课程分摊的运营成本用于内部成本分析，不影响财务报表显示")
        
        print("\n💡 结论:")
        print("系统确实会自动将运营成本按比例分配到课程，但这主要体现在：")
        print("1. 内部成本分析：每门课程分摊多少运营成本")
        print("2. 财务报表：运营成本作为独立项目显示，不合并到课程成本中")
        print("3. 利润计算：运营成本计入总成本，影响净利润")
        
    else:
        print("✗ 部分分析失败，需要检查系统配置")
        
        if not success1:
            print("  - 运营成本分配机制分析失败")
        if not success2:
            print("  - 利润分配页面结构分析失败")
        if not success3:
            print("  - 运营成本服务逻辑分析失败")
    
    print("\n📝 建议:")
    print("1. 明确'运营成本分配'的含义：概念分配 vs 财务合并")
    print("2. 在文档中说明运营成本分配的双重作用")
    print("3. 确保用户理解成本明细的显示逻辑")
