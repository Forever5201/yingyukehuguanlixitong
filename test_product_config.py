#!/usr/bin/env python3
"""
测试商品配置功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_config():
    """测试商品配置功能"""
    print("🧪 开始测试商品配置功能...")
    
    # 测试系统配置页面
    print("\n1. 测试系统配置页面")
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            print("✓ 系统配置页面可访问")
            
            # 检查商品配置相关元素
            if "shuadan_products" in response.text:
                print("✓ 商品配置字段存在")
            else:
                print("❌ 商品配置字段不存在")
            
            if "addProduct" in response.text:
                print("✓ 添加商品功能存在")
            else:
                print("❌ 添加商品功能不存在")
            
            if "product-config-container" in response.text:
                print("✓ 商品配置容器存在")
            else:
                print("❌ 商品配置容器不存在")
            
        else:
            print(f"❌ 系统配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 测试保存商品配置
    print("\n2. 测试保存商品配置")
    try:
        test_products = ["英语课程A", "数学课程B", "语文课程C"]
        test_data = {
            'trial_cost': '39.9',
            'course_cost': '100',
            'taobao_fee_rate': '0.6',
            'shuadan_products': json.dumps(test_products)
        }
        
        response = requests.post(f"{BASE_URL}/config", data=test_data)
        if response.status_code == 200:
            print("✓ 商品配置保存成功")
            
            # 验证保存结果
            response = requests.get(f"{BASE_URL}/config")
            if response.status_code == 200:
                if json.dumps(test_products) in response.text:
                    print("✓ 商品配置数据已正确保存")
                else:
                    print("❌ 商品配置数据保存失败")
            else:
                print("❌ 无法验证保存结果")
        else:
            print(f"❌ 商品配置保存失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 保存测试失败: {str(e)}")
    
    # 测试刷单管理页面是否使用商品配置
    print("\n3. 测试刷单管理页面")
    try:
        response = requests.get(f"{BASE_URL}/taobao-orders")
        if response.status_code == 200:
            print("✓ 刷单管理页面可访问")
            
            # 检查是否使用了商品配置
            if "product_name" in response.text and "select" in response.text:
                print("✓ 刷单管理页面包含商品选择功能")
            else:
                print("⚠️ 刷单管理页面缺少商品选择功能")
                
            # 检查是否有商品选项
            if "option value=" in response.text:
                print("✓ 刷单管理页面包含商品选项")
            else:
                print("⚠️ 刷单管理页面暂无商品选项")
        else:
            print(f"❌ 刷单管理页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n🎉 商品配置功能测试完成！")
    print("\n📝 说明：")
    print("- 商品配置现在支持可视化添加和删除")
    print("- 商品会自动保存为JSON格式")
    print("- 支持回车键快速添加商品")
    print("- 商品配置会用于刷单管理的下拉选择")

if __name__ == "__main__":
    test_product_config()
