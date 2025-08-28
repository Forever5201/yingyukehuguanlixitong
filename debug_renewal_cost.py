#!/usr/bin/env python3
"""
调试续课成本计算的脚本
"""

import requests
import re

def debug_renewal_cost():
    """调试续课成本计算"""
    base_url = "http://localhost:5000"
    
    print("🔍 调试续课成本计算...")
    print("=" * 50)
    
    try:
        # 获取页面内容
        response = requests.get(f"{base_url}/formal-courses/18/details")
        if response.status_code == 200:
            content = response.text
            
            # 查找续课信息部分
            renewal_section = re.search(r'续课信息.*?计算明细.*?收入计算.*?成本计算.*?利润计算', content, re.DOTALL)
            if renewal_section:
                print("✅ 找到续课信息部分")
                
                # 查找具体的成本数值
                cost_patterns = [
                    r'单节成本：</strong>\s*<span>¥([^<]+)</span>',
                    r'手续费：</strong>\s*<span>¥([^<]+)</span>',
                    r'总成本：</strong>\s*<span[^>]*>¥([^<]+)</span>'
                ]
                
                for i, pattern in enumerate(cost_patterns):
                    match = re.search(pattern, content)
                    if match:
                        value = match.group(1)
                        if i == 0:
                            print(f"✅ 单节成本: {value}")
                        elif i == 1:
                            print(f"✅ 手续费: {value}")
                        elif i == 2:
                            print(f"✅ 总成本: {value}")
                    else:
                        if i == 0:
                            print("❌ 单节成本: 未找到")
                        elif i == 1:
                            print("❌ 手续费: 未找到")
                        elif i == 2:
                            print("❌ 总成本: 未找到")
                
                # 查找计算明细的HTML结构
                print("\n🔍 检查HTML结构...")
                
                # 检查收入计算部分
                if "基础收入" in content:
                    print("✅ 基础收入字段存在")
                else:
                    print("❌ 基础收入字段缺失")
                
                if "实际收入" in content:
                    print("✅ 实际收入字段存在")
                else:
                    print("❌ 实际收入字段缺失")
                
                # 检查成本计算部分
                if "课时成本" in content:
                    print("✅ 课时成本字段存在")
                else:
                    print("❌ 课时成本字段缺失")
                
                # 检查利润计算部分
                if "净利润" in content:
                    print("✅ 净利润字段存在")
                else:
                    print("❌ 净利润字段缺失")
                
                if "利润率" in content:
                    print("✅ 利润率字段存在")
                else:
                    print("❌ 利润率字段缺失")
                
                # 查找具体的数值显示
                print("\n🔍 查找具体数值...")
                
                # 查找所有金额显示
                amount_pattern = r'¥([0-9,]+\.?[0-9]*)'
                amounts = re.findall(amount_pattern, content)
                unique_amounts = list(set(amounts))
                
                print(f"找到 {len(unique_amounts)} 个不同的金额:")
                for amount in sorted(unique_amounts, key=lambda x: float(x.replace(',', ''))):
                    print(f"   ¥{amount}")
                
            else:
                print("❌ 未找到续课信息部分")
                
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        return
    
    print()
    print("🎉 调试完成！")

if __name__ == "__main__":
    debug_renewal_cost()





