#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_export_api():
    """测试导出API"""
    url = 'http://127.0.0.1:5000/api/export/taobao-orders'
    
    print(f"正在测试导出API: {url}")
    
    try:
        # 发送请求
        response = requests.get(url, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            print(f"内容类型: {content_type}")
            
            # 检查文件大小
            content_length = len(response.content)
            print(f"文件大小: {content_length} bytes")
            
            if content_length > 0:
                # 保存文件进行验证
                filename = f"test_export_{int(time.time())}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"文件已保存为: {filename}")
                print("✅ 导出API测试成功！")
            else:
                print("❌ 文件内容为空")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_export_api()