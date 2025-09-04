#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户登录功能的脚本
"""

import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.models import User
from app.services.auth_service import AuthService

def test_login_functionality():
    """测试登录功能"""
    print("🔐 测试用户登录功能...")
    
    app = create_app()
    
    with app.test_request_context():
        print("\n=== 测试登录服务 ===")
        
        # 获取测试用户
        test_user = User.query.filter_by(username='17844540733').first()
        if not test_user:
            print("❌ 测试用户不存在")
            return False
        
        print(f"✓ 找到测试用户: {test_user.username}")
        
        # 测试登录功能
        success, message, user = AuthService.authenticate_user('17844540733', 'yuan971035088')
        
        print(f"\n登录测试结果:")
        print(f"  成功: {success}")
        print(f"  消息: {message}")
        print(f"  用户: {user.username if user else 'None'}")
        
        if success:
            print("✅ 登录功能正常工作！")
            
            # 测试API访问
            with app.test_client() as client:
                # 模拟登录后的请求
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(user.id)
                    sess['_fresh'] = True
                
                print("\n=== 测试API访问（模拟登录状态）===")
                response = client.get('/api/shareholders')
                print(f"API shareholders 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ API在登录状态下正常工作！")
                    try:
                        data = response.get_json()
                        print(f"API响应: {data}")
                    except:
                        print("API响应处理中...")
                else:
                    print(f"⚠️  API仍返回状态码: {response.status_code}")
        else:
            print("❌ 登录功能有问题")
            return False
    
    return True

def provide_user_instructions():
    """为用户提供操作指导"""
    print("\n" + "="*60)
    print("📋 用户操作指导")
    print("="*60)
    
    print("\n🎯 问题总结:")
    print("  401 UNAUTHORIZED 错误的根本原因是：")
    print("  👤 用户当前没有登录到系统")
    print("  🔄 应用重启导致之前的登录会话失效")
    
    print("\n✅ 解决步骤:")
    print("  1. 打开浏览器访问: http://localhost:5000/login")
    print("  2. 使用以下账户登录:")
    print("     用户名: 17844540733")
    print("     密码: yuan971035088")
    print("  3. 登录成功后，再访问报表中心页面")
    print("  4. 点击股东卡片测试分红功能")
    
    print("\n🔍 验证方法:")
    print("  登录后，在浏览器开发者工具Console中运行:")
    print("  fetch('/api/shareholders').then(r => r.json()).then(console.log)")
    print("  如果返回股东数据而不是401错误，说明问题已解决")
    
    print("\n💡 技术说明:")
    print("  - Flask-Login使用基于session的认证机制")
    print("  - 应用重启会使所有session失效")
    print("  - 这是正常的安全设计，不是bug")
    print("  - 用户需要重新登录来建立新的认证会话")

if __name__ == '__main__':
    print("🚀 开始测试登录功能...")
    
    success = test_login_functionality()
    
    if success:
        provide_user_instructions()
    else:
        print("\n❌ 登录功能测试失败，请检查系统配置")