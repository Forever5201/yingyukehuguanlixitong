#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查用户认证状态和API访问权限
"""

import requests
from urllib.parse import urljoin
import json

BASE_URL = "http://localhost:5000"

def check_login_page():
    """检查登录页面是否可访问"""
    try:
        url = urljoin(BASE_URL, '/login')
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 登录页面可访问")
            print(f"📍 登录地址: {url}")
            return True
        else:
            print(f"❌ 登录页面访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录页面请求失败: {e}")
        return False

def check_api_without_auth():
    """检查API在未认证状态下的响应"""
    apis_to_check = [
        '/api/shareholders',
        '/api/dividend-records/calculate-period?year=2025&month=9'
    ]
    
    print("\n🔍 检查API未认证访问:")
    
    for api_path in apis_to_check:
        try:
            url = urljoin(BASE_URL, api_path)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 401:
                print(f"✅ {api_path} - 正确返回401未授权（符合预期）")
            elif response.status_code == 200:
                print(f"⚠️ {api_path} - 返回200（可能存在认证绕过问题）")
            else:
                print(f"❓ {api_path} - 状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {api_path} - 请求失败: {e}")

def test_login():
    """测试登录功能"""
    print("\n🔐 测试登录功能:")
    
    # 创建session以保持cookie
    session = requests.Session()
    
    try:
        # 1. 获取登录页面
        login_url = urljoin(BASE_URL, '/login')
        response = session.get(login_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 无法访问登录页面，状态码: {response.status_code}")
            return False
        
        # 2. 尝试登录（使用默认凭据）
        login_data = {
            'username': 'admin',
            'password': 'admin123'  # 常见的默认密码
        }
        
        response = session.post(login_url, data=login_data, timeout=10)
        
        if response.status_code == 200:
            # 检查是否重定向到主页或包含成功信息
            if 'dashboard' in response.url or 'index' in response.url or response.url.endswith('/'):
                print("✅ 登录成功！")
                
                # 3. 测试受保护的API
                api_url = urljoin(BASE_URL, '/api/shareholders')
                api_response = session.get(api_url, timeout=10)
                
                if api_response.status_code == 200:
                    print("✅ API访问成功，认证有效")
                    return True
                else:
                    print(f"❌ API访问失败，状态码: {api_response.status_code}")
                    return False
            else:
                print("❌ 登录失败，可能是用户名或密码错误")
                return False
        else:
            print(f"❌ 登录请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def provide_login_instructions():
    """提供登录说明"""
    print("\n📋 登录说明:")
    print("1. 在浏览器中访问: http://localhost:5000/login")
    print("2. 输入您的用户名和密码")
    print("3. 如果忘记密码，可以尝试以下常见组合:")
    print("   - 用户名: admin, 密码: admin123")
    print("   - 用户名: admin, 密码: 123456")
    print("   - 用户名: admin, 密码: admin")
    print("4. 登录成功后，返回股东利润分配页面")
    print("5. 页面应该能正常加载数据")

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 用户认证状态检查工具")
    print("=" * 60)
    
    # 1. 检查登录页面
    print("1️⃣ 检查登录页面:")
    login_available = check_login_page()
    
    if not login_available:
        print("❌ 登录页面不可访问，请检查服务器状态")
        return False
    
    # 2. 检查API未认证访问
    check_api_without_auth()
    
    # 3. 测试登录功能
    login_success = test_login()
    
    # 4. 提供说明
    provide_login_instructions()
    
    print("\n" + "=" * 60)
    print("📊 检查结果:")
    print(f"登录页面可访问: {'✅' if login_available else '❌'}")
    print(f"自动登录测试: {'✅' if login_success else '❌'}")
    
    if login_success:
        print("\n🎉 系统认证功能正常！您可以直接登录使用。")
    else:
        print("\n⚠️ 需要手动登录，请按照上述说明操作。")
    
    return login_success

if __name__ == '__main__':
    main()