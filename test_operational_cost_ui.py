#!/usr/bin/env python3
"""
测试运营成本管理UI的脚本
"""

import requests
import re

def test_operational_cost_ui():
    """测试运营成本管理UI"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试运营成本管理UI...")
    print("=" * 50)
    
    try:
        # 测试系统配置页面
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            print("✅ 系统配置页面访问成功")
            
            content = response.text
            
            # 检查运营成本标签页
            if "运营成本" in content:
                print("✅ 运营成本标签页存在")
            else:
                print("❌ 运营成本标签页缺失")
                return
            
            # 检查运营成本标签页按钮
            if 'id="operational-cost-tab"' in content:
                print("✅ 运营成本标签页按钮存在")
            else:
                print("❌ 运营成本标签页按钮缺失")
            
            # 检查运营成本标签页内容
            if 'id="operational-cost-config"' in content:
                print("✅ 运营成本标签页内容存在")
            else:
                print("❌ 运营成本标签页内容缺失")
            
            # 检查运营成本管理标题
            if "运营成本管理" in content:
                print("✅ 运营成本管理标题存在")
            else:
                print("❌ 运营成本管理标题缺失")
            
            # 检查新增成本按钮
            if "新增成本" in content:
                print("✅ 新增成本按钮存在")
            else:
                print("❌ 新增成本按钮缺失")
            
            # 检查成本统计概览
            if "本月运营成本" in content:
                print("✅ 本月运营成本统计存在")
            else:
                print("❌ 本月运营成本统计缺失")
            
            if "本季度运营成本" in content:
                print("✅ 本季度运营成本统计存在")
            else:
                print("❌ 本季度运营成本统计缺失")
            
            if "成本分配" in content:
                print("✅ 成本分配统计存在")
            else:
                print("❌ 成本分配统计缺失")
            
            # 检查成本列表表格
            if "成本类型" in content and "成本名称" in content:
                print("✅ 成本列表表格存在")
            else:
                print("❌ 成本列表表格缺失")
            
            # 检查JavaScript函数
            if "loadOperationalCosts" in content:
                print("✅ 加载运营成本函数存在")
            else:
                print("❌ 加载运营成本函数缺失")
            
            if "loadOperationalCostStatistics" in content:
                print("✅ 加载运营成本统计函数存在")
            else:
                print("❌ 加载运营成本统计函数缺失")
            
            # 检查页面结构
            print("\n🔍 页面结构检查...")
            
            # 查找所有标签页
            tab_pattern = r'id="([^"]*-tab)"'
            tabs = re.findall(tab_pattern, content)
            print(f"找到的标签页: {tabs}")
            
            # 查找所有标签页内容
            content_pattern = r'id="([^"]*-config)"'
            contents = re.findall(content_pattern, content)
            print(f"找到的标签页内容: {contents}")
            
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return
    
    print()
    print("🎉 运营成本管理UI测试完成！")
    print("📋 请在浏览器中访问以下地址验证:")
    print(f"   {base_url}/config")
    print("   然后点击 '运营成本' 标签页")

if __name__ == "__main__":
    test_operational_cost_ui()





