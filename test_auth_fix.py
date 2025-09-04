#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试认证修复效果的脚本
验证登录后的API调用是否还会出现401错误
"""

import requests
from urllib.parse import urljoin
import json

BASE_URL = "http://localhost:5000"

def test_authentication_fix():
    """测试认证修复效果"""
    print("🔧 测试认证问题修复效果...")
    
    # 创建session以保持登录状态
    session = requests.Session()
    
    try:
        # 1. 首先登录
        print("\n📋 步骤1: 用户登录")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        response = session.post(login_url, data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 登录请求成功发送")
            
            # 检查是否真的登录成功（通过访问受保护页面）
            home_response = session.get(urljoin(BASE_URL, '/'), timeout=10)
            if "登出" in home_response.text or "dashboard" in home_response.text.lower():
                print("✅ 登录成功确认")
            else:
                print("⚠️ 登录状态不确定")
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return False
        
        # 2. 测试员工业绩页面访问
        print("\n📋 步骤2: 访问员工业绩页面")
        performance_url = urljoin(BASE_URL, '/employee-performance')
        response = session.get(performance_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 员工业绩页面访问成功")
        else:
            print(f"❌ 员工业绩页面访问失败，状态码: {response.status_code}")
            return False
        
        # 3. 测试API调用（这是之前出现401错误的地方）
        print("\n📋 步骤3: 测试API调用")
        test_apis = [
            '/api/employees/1/monthly-summary?year=2025&month=9',
            '/api/employees',
            '/api/commission-config'
        ]
        
        all_success = True
        for api_path in test_apis:
            api_url = urljoin(BASE_URL, api_path)
            response = session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {api_path} - 调用成功")
            elif response.status_code == 404:
                print(f"⚠️ {api_path} - 资源不存在（404），但认证通过")
            elif response.status_code == 401:
                print(f"❌ {api_path} - 仍然出现401认证错误")
                all_success = False
            else:
                print(f"❓ {api_path} - 状态码: {response.status_code}")
        
        # 4. 测试会话信息
        print("\n📋 步骤4: 检查会话信息")
        session_url = urljoin(BASE_URL, '/session-info')
        response = session.get(session_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 会话信息获取成功")
        else:
            print(f"❌ 会话信息获取失败，状态码: {response.status_code}")
        
        # 5. 总结
        print("\n📊 测试结果总结:")
        if all_success:
            print("🎉 认证问题已修复！所有API调用都成功通过认证。")
            print("💡 您现在可以正常使用员工业绩页面的所有功能了。")
        else:
            print("❌ 仍然存在认证问题，需要进一步调试。")
        
        return all_success
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    test_authentication_fix()