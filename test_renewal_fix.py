#!/usr/bin/env python3
"""
测试续课成本修复的脚本
"""

import requests

def test_renewal_fix():
    """测试续课成本修复"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试续课成本修复...")
    print("=" * 50)
    
    try:
        # 测试正课详情页面
        response = requests.get(f"{base_url}/formal-courses/18/details")
        if response.status_code == 200:
            print("✅ 正课详情页面访问成功")
            
            content = response.text
            
            # 检查续课信息
            if "续课信息" in content:
                print("✅ 续课信息部分存在")
            else:
                print("❌ 续课信息部分缺失")
                return
            
            # 检查计算明细
            if "计算明细" in content:
                print("✅ 续课计算明细部分存在")
            else:
                print("❌ 续课计算明细部分缺失")
                return
            
            # 检查具体的成本字段
            if "单节成本" in content:
                print("✅ 单节成本字段存在")
            else:
                print("❌ 单节成本字段缺失")
            
            if "手续费" in content:
                print("✅ 手续费字段存在")
            else:
                print("❌ 手续费字段缺失")
            
            if "总成本" in content:
                print("✅ 总成本字段存在")
            else:
                print("❌ 总成本字段缺失")
            
            # 检查是否显示具体的数值（而不是"未设置"）
            if "¥90.00" in content:
                print("✅ 单节成本显示正确: ¥90.00")
            else:
                print("❌ 单节成本显示异常")
            
            if "¥18.96" in content:
                print("✅ 手续费显示正确: ¥18.96")
            else:
                print("❌ 手续费显示异常")
            
            if "¥1,938.96" in content:
                print("✅ 总成本显示正确: ¥1,938.96")
            else:
                print("❌ 总成本显示异常")
            
        else:
            print(f"❌ 正课详情页面访问失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return
    
    print()
    print("🎉 续课成本修复测试完成！")
    print("📋 请在浏览器中访问以下地址验证:")
    print(f"   {base_url}/formal-courses/18/details")

if __name__ == "__main__":
    test_renewal_fix()






