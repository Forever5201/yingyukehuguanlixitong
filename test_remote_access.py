#!/usr/bin/env python3
"""
远程访问测试脚本
用于测试系统是否可以从外部访问
"""

import requests
import socket
import subprocess
import sys
import os
from datetime import datetime

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到外部地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"获取本机IP失败: {e}")
        return "127.0.0.1"

def get_public_ip():
    """获取公网IP地址"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except Exception as e:
        print(f"获取公网IP失败: {e}")
        return None

def test_local_access():
    """测试本地访问"""
    print("=" * 50)
    print("测试本地访问")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ 本地访问正常")
            return True
        else:
            print(f"❌ 本地访问异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 本地访问失败: {e}")
        return False

def test_network_access():
    """测试网络访问"""
    print("\n" + "=" * 50)
    print("测试网络访问")
    print("=" * 50)
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"本机IP: {local_ip}")
    print(f"公网IP: {public_ip}")
    
    # 测试本机IP访问
    try:
        response = requests.get(f'http://{local_ip}:5000', timeout=5)
        if response.status_code == 200:
            print(f"✅ 本机IP访问正常: http://{local_ip}:5000")
        else:
            print(f"❌ 本机IP访问异常: http://{local_ip}:5000")
    except Exception as e:
        print(f"❌ 本机IP访问失败: {e}")
    
    # 测试公网IP访问
    if public_ip:
        try:
            response = requests.get(f'http://{public_ip}:5000', timeout=10)
            if response.status_code == 200:
                print(f"✅ 公网IP访问正常: http://{public_ip}:5000")
            else:
                print(f"❌ 公网IP访问异常: http://{public_ip}:5000")
        except Exception as e:
            print(f"❌ 公网IP访问失败: {e}")

def check_port_status():
    """检查端口状态"""
    print("\n" + "=" * 50)
    print("检查端口状态")
    print("=" * 50)
    
    try:
        # 检查5000端口是否被监听
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':5000' in result.stdout:
            print("✅ 端口5000正在监听")
        else:
            print("❌ 端口5000未监听")
    except Exception as e:
        print(f"检查端口状态失败: {e}")

def generate_access_info():
    """生成访问信息"""
    print("\n" + "=" * 50)
    print("访问信息汇总")
    print("=" * 50)
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("📋 访问地址列表:")
    print(f"   本地访问: http://localhost:5000")
    print(f"   本机IP:   http://{local_ip}:5000")
    if public_ip:
        print(f"   公网IP:   http://{public_ip}:5000")
    
    print("\n📝 访问说明:")
    print("   1. 本地访问: 只能在服务器本机访问")
    print("   2. 本机IP: 同一网络内的其他设备可以访问")
    print("   3. 公网IP: 互联网上的任何设备都可以访问")
    
    print("\n⚠️  注意事项:")
    print("   - 确保防火墙已开放5000端口")
    print("   - 云服务器需要在安全组中开放5000端口")
    print("   - 建议配置域名和HTTPS以提高安全性")

def main():
    """主函数"""
    print("=" * 60)
    print("    客户管理系统 - 远程访问测试工具")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查Flask应用是否运行
    if not test_local_access():
        print("\n❌ Flask应用未运行，请先启动应用:")
        print("   python run.py")
        return
    
    # 检查端口状态
    check_port_status()
    
    # 测试网络访问
    test_network_access()
    
    # 生成访问信息
    generate_access_info()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()


