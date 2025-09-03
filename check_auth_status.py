#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查用户认证状态的脚本
"""

import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.models import User
from flask import session
from flask_login import current_user

def check_auth_status():
    """检查认证状态"""
    print("🔍 检查用户认证状态...")
    
    app = create_app()
    
    with app.test_request_context():
        print("\n=== Flask应用配置检查 ===")
        print(f"SECRET_KEY 是否设置: {bool(app.secret_key)}")
        print(f"SECRET_KEY 长度: {len(app.secret_key) if app.secret_key else 0}")
        print(f"SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY', '未设置')}")
        print(f"Login Manager view: {app.login_manager.login_view}")
        
        print("\n=== 数据库用户检查 ===")
        users = User.query.all()
        if users:
            for user in users:
                print(f"用户: {user.username}, ID: {user.id}, 活跃: {user.is_active}")
        else:
            print("❌ 数据库中没有用户")
        
        print("\n=== 当前认证状态 ===")
        print(f"current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"current_user 类型: {type(current_user)}")
        print(f"session 内容: {dict(session)}")
    
    # 模拟登录状态检查
    with app.test_request_context():
        # 模拟有session的情况
        with app.test_client() as client:
            print("\n=== 模拟登录检查 ===")
            
            # 尝试访问登录页面
            response = client.get('/login')
            print(f"登录页面状态码: {response.status_code}")
            
            # 尝试直接访问需要认证的API
            response = client.get('/api/shareholders')
            print(f"API shareholders 状态码: {response.status_code}")
            
            if response.status_code == 401:
                print("✓ API正确返回401未授权状态")
                try:
                    data = response.get_json()
                    print(f"API响应: {data}")
                except:
                    print("API响应不是JSON格式")
            
    print("\n=== 问题诊断 ===")
    
    # 检查问题可能的原因
    issues = []
    
    if not app.secret_key:
        issues.append("❌ SECRET_KEY 未设置")
    
    if not users:
        issues.append("❌ 数据库中没有用户账户")
    
    if issues:
        print("发现的问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✓ 基本配置正常")
    
    print("\n💡 解决方案:")
    print("1. 确保用户已登录到系统")
    print("2. 检查浏览器是否保存了有效的session cookie")
    print("3. 如果在不同设备上，需要重新登录")
    print("4. 访问 http://localhost:5000/login 进行登录")

if __name__ == '__main__':
    check_auth_status()