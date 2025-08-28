#!/usr/bin/env python3
"""
创建用户表的数据库迁移脚本
"""

import os
import sys
from datetime import datetime, timezone

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from app.services.auth_service import AuthService

def create_user_table():
    """创建用户表并添加默认用户"""
    
    print("=" * 60)
    print("    用户表创建和初始化")
    print("=" * 60)
    
    try:
        # 创建应用上下文
        app = create_app()
        
        with app.app_context():
            print("1. 检查数据库连接...")
            
            # 检查数据库是否可连接
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("SELECT 1"))
                print("✅ 数据库连接正常")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
            
            print("\n2. 创建用户表...")
            
            # 创建用户表
            try:
                db.create_all()
                print("✅ 用户表创建成功")
            except Exception as e:
                if "already exists" in str(e):
                    print("✅ 用户表已存在")
                else:
                    print(f"❌ 用户表创建失败: {e}")
                    return False
            
            print("\n3. 创建默认管理员用户...")
            
            # 创建默认用户
            if AuthService.create_default_user():
                print("✅ 默认管理员用户创建成功")
                print("   用户名: 17844540733")
                print("   密码: yuan971035088")
            else:
                print("✅ 默认用户已存在或创建失败")
            
            print("\n4. 验证用户表...")
            
            # 验证用户表
            try:
                user_count = User.query.count()
                print(f"✅ 用户表验证成功，当前有 {user_count} 个用户")
                
                # 显示用户列表
                users = User.query.all()
                for user in users:
                    print(f"   - {user.username} ({user.role}) - {'激活' if user.is_active else '禁用'}")
                    
            except Exception as e:
                print(f"❌ 用户表验证失败: {e}")
                return False
            
            print("\n" + "=" * 60)
            print("✅ 用户表创建和初始化完成！")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

if __name__ == "__main__":
    success = create_user_table()
    if success:
        print("\n🎉 现在您可以启动应用并使用登录功能了！")
        print("   访问地址: http://localhost:5000")
        print("   登录信息: 用户名 17844540733，密码 yuan971035088")
    else:
        print("\n❌ 初始化失败，请检查错误信息")
    
    input("\n按回车键退出...")
