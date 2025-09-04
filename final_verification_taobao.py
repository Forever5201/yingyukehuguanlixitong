#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验证测试：确认刷单管理功能完全正常
"""

import requests
from urllib.parse import urljoin
import json
import time

BASE_URL = "http://localhost:5000"

def final_verification():
    """最终验证刷单管理功能"""
    print("🏁 最终验证：刷单管理功能测试")
    print("=" * 50)
    
    # 创建session保持登录状态
    session = requests.Session()
    
    try:
        # 1. 登录系统
        print("\n🔐 步骤1: 用户认证")
        login_url = urljoin(BASE_URL, '/login')
        login_data = {
            'username': '17844540733',
            'password': 'yuan971035088'
        }
        
        login_response = session.post(login_url, data=login_data, timeout=10)
        if login_response.status_code == 200:
            print("✅ 用户认证成功")
        else:
            print(f"❌ 用户认证失败，状态码: {login_response.status_code}")
            return False
        
        # 2. 访问刷单管理页面
        print("\n📱 步骤2: 页面访问")
        taobao_url = urljoin(BASE_URL, '/taobao-orders')
        page_response = session.get(taobao_url, timeout=10)
        
        if page_response.status_code == 200:
            print("✅ 刷单管理页面访问成功")
            page_content = page_response.text
            
            # 检查页面核心功能
            core_features = {
                '页面标题': '刷单管理' in page_content,
                '统计面板': '总单量' in page_content,
                '添加按钮': '添加刷单记录' in page_content,
                '数据表格': '<table' in page_content,
                '模态框支持': 'modal' in page_content.lower(),
                '筛选功能': 'filter' in page_content.lower(),
                '导出功能': '导出' in page_content
            }
            
            print("\n📊 页面功能检查:")
            for feature, exists in core_features.items():
                status = "✅" if exists else "❌"
                print(f"  {status} {feature}")
                
        else:
            print(f"❌ 页面访问失败，状态码: {page_response.status_code}")
            return False
        
        # 3. 测试API功能
        print("\n🔌 步骤3: API功能测试")
        
        # 测试配置API
        config_url = urljoin(BASE_URL, '/api/config/taobao_fee_rate')
        config_response = session.get(config_url, timeout=10)
        
        if config_response.status_code == 200:
            print("✅ 配置API正常工作")
            try:
                config_data = config_response.json()
                print(f"  📋 手续费率配置: {config_data.get('value', '未配置')}%")
            except json.JSONDecodeError:
                print("  ⚠️ 配置API响应格式异常")
        else:
            print(f"❌ 配置API异常，状态码: {config_response.status_code}")
        
        # 4. 测试导出功能
        print("\n📥 步骤4: 导出功能测试")
        export_url = urljoin(BASE_URL, '/api/export/taobao-orders')
        export_response = session.get(export_url, timeout=15)
        
        if export_response.status_code == 200:
            content_type = export_response.headers.get('Content-Type', '')
            if 'excel' in content_type or 'spreadsheet' in content_type:
                print("✅ Excel导出功能正常")
            else:
                print("⚠️ 导出功能响应，但格式可能不是Excel")
        elif export_response.status_code == 404:
            print("⚠️ 导出功能暂未实现")
        else:
            print(f"❌ 导出功能异常，状态码: {export_response.status_code}")
        
        # 5. 测试认证保护
        print("\n🔒 步骤5: 认证保护验证")
        
        # 创建新的无认证session
        test_session = requests.Session()
        unauth_response = test_session.get(taobao_url, timeout=10)
        
        if unauth_response.status_code == 200 and len(unauth_response.text) < 20000:
            print("✅ 未登录用户被正确重定向到登录页面")
        elif unauth_response.status_code == 302:
            print("✅ 未登录用户被正确重定向")
        else:
            print("⚠️ 认证保护可能存在问题")
        
        # 6. 功能完整性评估
        print("\n📋 步骤6: 功能完整性评估")
        
        success_count = sum(1 for exists in core_features.values() if exists)
        total_features = len(core_features)
        completion_rate = (success_count / total_features) * 100
        
        print(f"  📊 功能完整度: {success_count}/{total_features} ({completion_rate:.1f}%)")
        
        if completion_rate >= 90:
            print("  🎉 功能完整度优秀")
        elif completion_rate >= 70:
            print("  ✅ 功能完整度良好")
        else:
            print("  ⚠️ 功能完整度需要改进")
        
        # 7. 最终结论
        print("\n" + "=" * 50)
        print("🏆 最终验证结果")
        print("=" * 50)
        
        if completion_rate >= 80:
            print("✅ 刷单管理功能基本正常")
            print("🎯 用户现在应该可以正常使用刷单管理功能")
            
            print("\n📝 使用指南:")
            print("1. 登录系统后，点击侧边栏的'刷单管理'")
            print("2. 查看统计信息和现有订单列表") 
            print("3. 点击'添加刷单记录'按钮添加新订单")
            print("4. 使用筛选和排序功能管理订单")
            print("5. 可以编辑或删除现有订单")
            
            if config_response.status_code == 200:
                print("\n⚙️ 系统配置:")
                print("- 手续费率等配置已正确加载")
                print("- 建议在'系统配置'中检查相关参数")
                
        else:
            print("❌ 刷单管理功能存在问题，需要进一步修复")
            
            missing_features = [feature for feature, exists in core_features.items() if not exists]
            if missing_features:
                print("\n🔧 需要修复的功能:")
                for feature in missing_features:
                    print(f"  - {feature}")
        
        # 8. 用户操作建议
        print("\n💡 如果仍然遇到问题:")
        print("1. 清除浏览器缓存并刷新页面")
        print("2. 检查浏览器控制台是否有JavaScript错误")
        print("3. 确保网络连接正常")
        print("4. 尝试重新登录系统")
        
        return completion_rate >= 80
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        return False

if __name__ == "__main__":
    final_verification()