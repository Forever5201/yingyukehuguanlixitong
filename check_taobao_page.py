#!/usr/bin/env python3
"""
检查刷单管理页面的实际HTML内容
"""

import requests
import re

BASE_URL = "http://localhost:5000"

def check_taobao_page():
    """检查刷单管理页面的实际HTML内容"""
    print("🔍 检查刷单管理页面的HTML内容...")
    
    try:
        response = requests.get(f"{BASE_URL}/taobao-orders")
        if response.status_code == 200:
            print("✓ 刷单管理页面可访问")
            
            # 查找商品选择相关的HTML
            html_content = response.text
            
            # 查找select标签
            select_pattern = r'<select[^>]*id="product_name"[^>]*>(.*?)</select>'
            select_match = re.search(select_pattern, html_content, re.DOTALL)
            
            if select_match:
                select_content = select_match.group(0)
                print("✓ 找到商品选择下拉框")
                print("  下拉框HTML:")
                print(f"  {select_content}")
                
                # 查找所有option标签
                option_pattern = r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>'
                options = re.findall(option_pattern, select_content)
                
                print(f"\n  商品选项:")
                for value, text in options:
                    print(f"    {value} -> {text}")
                    
            else:
                print("❌ 未找到商品选择下拉框")
                
                # 查找input标签
                input_pattern = r'<input[^>]*id="product_name"[^>]*>'
                input_match = re.search(input_pattern, html_content)
                
                if input_match:
                    print("✓ 找到商品输入框（未配置商品列表）")
                    print(f"  输入框HTML: {input_match.group(0)}")
                else:
                    print("❌ 未找到商品输入字段")
            
            # 检查是否有商品配置相关的提示
            if "系统未配置商品列表" in html_content:
                print("⚠️ 页面显示'系统未配置商品列表'")
            elif "shuadan_products" in html_content:
                print("✓ 页面包含商品配置引用")
                
        else:
            print(f"❌ 刷单管理页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    check_taobao_page()

