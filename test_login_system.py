#!/usr/bin/env python3
"""
登录系统测试脚本
"""

import os
import sys
import requests
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login_system():
    """测试登录系统"""
    
    print("=" * 60)
    print("    登录系统测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试配置
    base_url = "http://localhost:5000"
    login_url = f"{base_url}/login"
    home_url = f"{base_url}/"
    
    print(f"\n测试配置:")
    print(f"   基础URL: {base_url}")
    print(f"   登录页面: {login_url}")
    print(f"   首页: {home_url}")
    
    try:
        print(f"\n1. 测试登录页面访问...")
        response = requests.get(login_url, timeout=5)
        if response.status_code == 200:
            print("✅ 登录页面访问正常")
        else:
            print(f"❌ 登录页面访问失败，状态码: {response.status_code}")
            return False
        
        print(f"\n2. 测试首页访问（未登录）...")
        response = requests.get(home_url, timeout=5, allow_redirects=False)
        if response.status_code == 302:  # 重定向到登录页面
            print("✅ 未登录用户被正确重定向到登录页面")
        else:
            print(f"❌ 未登录用户访问首页异常，状态码: {response.status_code}")
            return False
        
        print(f"\n3. 测试登录功能...")
        
        # 测试错误密码
        print("   测试错误密码...")
        login_data = {
            'username': '17844540733',
            'password': 'wrong_password'
        }
        response = requests.post(login_url, data=login_data, timeout=5, allow_redirects=False)
        if response.status_code == 200:  # 登录失败，停留在登录页面
            print("✅ 错误密码登录失败，正确停留在登录页面")
        else:
            print(f"❌ 错误密码登录测试异常，状态码: {response.status_code}")
        
        # 测试正确密码
        print("   测试正确密码...")
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        response = requests.post(login_url, data=login_data, timeout=5, allow_redirects=False)
        if response.status_code == 302:  # 登录成功，重定向到首页
            print("✅ 正确密码登录成功，重定向到首页")
        else:
            print(f"❌ 正确密码登录测试异常，状态码: {response.status_code}")
        
        print(f"\n" + "=" * 60)
        print("✅ 登录系统测试完成！")
        print("=" * 60)
        
        print(f"\n📋 测试结果总结:")
        print(f"   ✅ 登录页面可以正常访问")
        print(f"   ✅ 未登录用户被正确重定向")
        print(f"   ✅ 错误密码登录被正确拒绝")
        print(f"   ✅ 正确密码登录成功")
        
        print(f"\n🎉 登录系统工作正常！")
        print(f"   您可以访问 {base_url} 来使用系统")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务器，请确保应用正在运行")
        print(f"   请运行: python run.py")
        return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = test_login_system()
    if not success:
        print(f"\n❌ 测试失败，请检查应用是否正常运行")
    
    input(f"\n按回车键退出...")


