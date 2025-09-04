#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试刷单管理页面访问问题
"""

import requests
from urllib.parse import urljoin

BASE_URL = "http://localhost:5000"

def test_taobao_orders_access():
    """测试刷单管理页面访问"""
    print("🔍 测试刷单管理页面访问问题...")
    
    # 创建session以保持登录状态
    session = requests.Session()
    
    try:
        # 1. 首先测试未登录时的访问
        print("\n📋 步骤1: 测试未登录访问")
        taobao_url = urljoin(BASE_URL, '/taobao-orders')
        response = session.get(taobao_url, timeout=10)
        
        print(f"  状态码: {response.status_code}")
        print(f"  响应长度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            if "登录" in response.text:
                print("  ✅ 页面正确要求用户登录")
            elif "刷单管理" in response.text:
                print("  ⚠️ 页面可以无需认证访问（可能存在安全问题）")
                print("  📝 这可能解释了为什么点击没有反应")
            else:
                print("  ❓ 页面内容异常")
        elif response.status_code == 302:
            print(f"  ✅ 页面正确重定向: {response.headers.get('Location', '未知')}")
        else:
            print(f"  ❌ 页面访问异常，状态码: {response.status_code}")
        
        # 2. 测试登录后的访问
        print("\n📋 步骤2: 测试登录后访问")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("  ✅ 登录请求成功")
            
            # 再次访问刷单管理页面
            response2 = session.get(taobao_url, timeout=10)
            
            print(f"  登录后访问状态码: {response2.status_code}")
            
            if response2.status_code == 200:
                if "淘宝刷单管理" in response2.text or "刷单管理" in response2.text:
                    print("  ✅ 登录后可以正常访问刷单管理页面")
                    
                    # 检查页面是否有JavaScript错误
                    if "console.error" in response2.text:
                        print("  ⚠️ 页面可能包含JavaScript错误")
                    
                    # 检查是否有必要的资源
                    if "bootstrap" in response2.text.lower():
                        print("  ✅ 页面包含Bootstrap资源")
                    else:
                        print("  ⚠️ 页面缺少Bootstrap资源（可能影响功能）")
                        
                else:
                    print("  ❌ 登录后仍无法正确显示刷单管理页面")
            else:
                print(f"  ❌ 登录后访问失败，状态码: {response2.status_code}")
        else:
            print(f"  ❌ 登录失败，状态码: {login_response.status_code}")
        
        # 3. 检查路由是否存在
        print("\n📋 步骤3: 检查其他页面作为对比")
        home_response = session.get(urljoin(BASE_URL, '/'), timeout=10)
        print(f"  主页访问状态码: {home_response.status_code}")
        
        trial_response = session.get(urljoin(BASE_URL, '/trial-courses'), timeout=10)
        print(f"  试听课管理访问状态码: {trial_response.status_code}")
        
        # 4. 总结分析
        print("\n📊 问题分析:")
        if response.status_code == 200 and "刷单管理" in response.text:
            print("  🎯 可能的问题: 刷单管理路由缺少认证装饰器")
            print("  📝 建议: 添加 @login_required_custom 装饰器")
        elif response2.status_code == 200 and "刷单管理" in response2.text:
            print("  🎯 页面本身可以访问，问题可能在前端JavaScript")
            print("  📝 建议: 检查浏览器控制台错误")
        else:
            print("  🎯 需要进一步调试页面访问问题")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    test_taobao_orders_access()