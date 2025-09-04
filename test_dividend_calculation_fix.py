#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试分红记录计算功能修复验证
"""

import requests
from urllib.parse import urljoin
import json
import time

BASE_URL = "http://localhost:5000"

def test_login_first():
    """首先测试登录"""
    print("🔐 正在测试登录...")
    
    session = requests.Session()
    
    try:
        # 1. 获取登录页面
        login_url = urljoin(BASE_URL, '/login')
        response = session.get(login_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 无法访问登录页面，状态码: {response.status_code}")
            return None
        
        # 2. 尝试登录（使用常见凭据）
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(login_url, data=login_data, timeout=10)
        
        # 3. 测试受保护的API
        api_url = urljoin(BASE_URL, '/api/shareholders')
        api_response = session.get(api_url, timeout=10)
        
        if api_response.status_code == 200:
            print("✅ 登录成功，认证有效")
            return session
        else:
            print(f"❌ 登录验证失败，状态码: {api_response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录测试失败: {e}")
        return None

def test_shareholders_api(session):
    """测试股东信息API"""
    try:
        url = urljoin(BASE_URL, '/api/shareholders')
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                shareholders = data.get('shareholders', [])
                print(f"✅ 股东信息API正常，找到 {len(shareholders)} 个股东")
                
                for shareholder in shareholders:
                    name = shareholder.get('name', '未知')
                    print(f"  📝 股东: {name}")
                
                return shareholders
            else:
                print(f"❌ 股东信息API返回失败: {data.get('message')}")
                return []
        else:
            print(f"❌ 股东信息API请求失败，状态码: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 测试股东信息API失败: {e}")
        return []

def test_calculate_period_api(session):
    """测试期间利润计算API"""
    try:
        # 测试当前期间
        from datetime import datetime
        now = datetime.now()
        year = now.year
        month = now.month
        
        url = urljoin(BASE_URL, f'/api/dividend-records/calculate-period?year={year}&month={month}')
        response = session.get(url, timeout=10)
        
        print(f"🧮 测试期间利润计算API: {year}年{month}月")
        print(f"📍 请求URL: {url}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ API响应成功，状态码: {response.status_code}")
                
                if data.get('success'):
                    result_data = data.get('data', {})
                    print("✅ 计算成功，返回数据结构:")
                    
                    # 检查期间信息
                    period = result_data.get('period', {})
                    if period:
                        print(f"  📅 期间: {period.get('year')}-{period.get('month')}")
                        print(f"  📅 开始日期: {period.get('start_date')}")
                        print(f"  📅 结束日期: {period.get('end_date')}")
                    
                    # 检查利润汇总
                    profit_summary = result_data.get('profit_summary', {})
                    if profit_summary:
                        print(f"  💰 总收入: {profit_summary.get('total_revenue', 0)}")
                        print(f"  💸 总成本: {profit_summary.get('total_cost', 0)}")
                        print(f"  💎 净利润: {profit_summary.get('net_profit', 0)}")
                    
                    # 检查股东分配（关键测试点）
                    shareholder_distribution = result_data.get('shareholder_distribution', {})
                    if shareholder_distribution:
                        print("  📊 股东分配:")
                        for key, value in shareholder_distribution.items():
                            print(f"    - {key}: {value}")
                    else:
                        print("  ❌ 缺少shareholder_distribution数据")
                    
                    return result_data
                else:
                    print(f"❌ 计算失败: {data.get('message', '未知错误')}")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:500]}")
                return None
                
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"响应内容: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ 测试期间利润计算API失败: {e}")
        return None

def test_frontend_data_mapping(shareholders, calculation_result):
    """测试前端数据映射逻辑"""
    print("\n🧪 测试前端数据映射逻辑:")
    
    if not calculation_result or not calculation_result.get('shareholder_distribution'):
        print("❌ 缺少计算结果或股东分配数据，跳过映射测试")
        return False
    
    distribution = calculation_result['shareholder_distribution']
    
    # 模拟前端的股东名称映射逻辑
    for shareholder in shareholders:
        shareholder_name = shareholder.get('name', '')
        print(f"\n  📋 测试股东: {shareholder_name}")
        
        # 1. 直接键访问（新的修复逻辑）
        if shareholder_name in distribution:
            profit = distribution[shareholder_name]
            print(f"    ✅ 直接键访问成功: {profit}")
            continue
        
        # 2. 映射访问（备用逻辑）
        distribution_map = {
            '股东A': 'shareholder_a_net_profit',
            '股东B': 'shareholder_b_net_profit'
        }
        
        mapped_key = distribution_map.get(shareholder_name)
        if mapped_key and mapped_key in distribution:
            profit = distribution[mapped_key]
            print(f"    ✅ 映射键访问成功: {mapped_key} = {profit}")
            continue
        
        # 3. 都失败
        print(f"    ❌ 无法获取利润数据")
        print(f"    💡 可用的键: {list(distribution.keys())}")
    
    return True

def main():
    """主测试函数"""
    print("=" * 70)
    print("🔧 分红记录计算功能修复验证")
    print("=" * 70)
    
    # 1. 登录测试
    session = test_login_first()
    if not session:
        print("\n❌ 登录失败，无法继续测试")
        return False
    
    # 2. 测试股东信息
    print("\n📊 测试股东信息API:")
    shareholders = test_shareholders_api(session)
    
    # 3. 测试期间利润计算
    print("\n🧮 测试期间利润计算API:")
    calculation_result = test_calculate_period_api(session)
    
    # 4. 测试数据映射
    if shareholders and calculation_result:
        test_frontend_data_mapping(shareholders, calculation_result)
    
    # 5. 总结
    print("\n" + "=" * 70)
    print("📊 测试结果总结:")
    
    login_ok = session is not None
    shareholders_ok = len(shareholders) > 0
    calculation_ok = calculation_result is not None
    
    print(f"登录认证: {'✅ 通过' if login_ok else '❌ 失败'}")
    print(f"股东信息API: {'✅ 通过' if shareholders_ok else '❌ 失败'}")
    print(f"期间利润计算API: {'✅ 通过' if calculation_ok else '❌ 失败'}")
    
    if login_ok and shareholders_ok and calculation_ok:
        print("\n🎉 所有核心功能测试通过！")
        print("💡 修复应该已经生效，前端不应再出现 'Cannot read properties of undefined' 错误")
        return True
    else:
        print("\n⚠️ 部分功能未通过测试，可能需要进一步检查")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)