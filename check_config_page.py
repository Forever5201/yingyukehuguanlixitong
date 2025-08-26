#!/usr/bin/env python3
"""
检查系统配置页面的商品配置显示
"""

import requests
import re

BASE_URL = "http://localhost:5000"

def check_config_page():
    """检查系统配置页面的商品配置显示"""
    print("🔍 检查系统配置页面的商品配置显示...")
    
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            print("✓ 系统配置页面可访问")
            
            html_content = response.text
            
            # 查找textarea中的shuadan_products值
            pattern = r'<textarea[^>]*id="shuadan_products"[^>]*>(.*?)</textarea>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if match:
                value = match.group(1).strip()
                print(f"✓ 找到商品配置textarea")
                print(f"  值: {repr(value)}")
                
                if value:
                    print("✓ 商品配置有值")
                    try:
                        import json
                        products = json.loads(value)
                        print(f"  解析为JSON: {products}")
                        print(f"  商品数量: {len(products)}")
                    except json.JSONDecodeError:
                        print("  ❌ JSON解析失败")
                else:
                    print("❌ 商品配置为空")
            else:
                print("❌ 未找到商品配置textarea")
            
            # 检查是否有商品列表容器
            if 'productList' in html_content:
                print("✓ 找到商品列表容器")
            else:
                print("❌ 未找到商品列表容器")
                
            # 检查是否有initProductConfig函数
            if 'initProductConfig' in html_content:
                print("✓ 找到initProductConfig函数")
            else:
                print("❌ 未找到initProductConfig函数")
                
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    check_config_page()
