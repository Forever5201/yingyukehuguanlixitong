#!/usr/bin/env python3
"""
测试您的服务器访问 - 117.72.145.165:5000
"""

import requests
import time
from datetime import datetime

def test_access():
    """测试访问您的服务器"""
    
    server_ip = "117.72.145.165"
    port = "5000"
    url = f"http://{server_ip}:{port}"
    
    print("=" * 60)
    print("    测试您的客户管理系统远程访问")
    print("=" * 60)
    print(f"服务器IP: {server_ip}")
    print(f"访问地址: {url}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        print("正在测试连接...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 连接成功！")
            print(f"   状态码: {response.status_code}")
            print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
            print(f"   页面大小: {len(response.content)} bytes")
            
            # 检查是否是正确的页面
            if "客户管理系统" in response.text or "Customer Management" in response.text:
                print("✅ 页面内容正确 - 这是您的客户管理系统")
            else:
                print("⚠️  页面内容可能不正确")
            
            print("\n🎉 您可以通过以下方式访问:")
            print(f"   🖥️  电脑浏览器: {url}")
            print(f"   📱 手机浏览器: {url}")
            print(f"   📱 平板电脑: {url}")
            
        elif response.status_code == 404:
            print("❌ 页面未找到 (404)")
            print("   可能原因: 应用未在5000端口运行")
            
        elif response.status_code == 500:
            print("❌ 服务器内部错误 (500)")
            print("   可能原因: 应用运行异常")
            
        else:
            print(f"❌ 访问异常 (状态码: {response.status_code})")
            
    except requests.exceptions.ConnectTimeout:
        print("❌ 连接超时")
        print("   可能原因:")
        print("   1. 防火墙未开放5000端口")
        print("   2. 应用未启动")
        print("   3. 云服务器安全组未配置")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接被拒绝")
        print("   可能原因:")
        print("   1. 应用未在0.0.0.0:5000监听")
        print("   2. 防火墙阻止连接")
        print("   3. 端口未开放")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        
    print("\n" + "=" * 60)
    print("访问建议:")
    print("1. 确保应用正在运行: python run.py")
    print("2. 检查防火墙设置，开放5000端口")
    print("3. 如果是云服务器，检查安全组配置")
    print("4. 确保应用监听在 0.0.0.0:5000 而不是 127.0.0.1:5000")
    print("=" * 60)

if __name__ == "__main__":
    test_access()


