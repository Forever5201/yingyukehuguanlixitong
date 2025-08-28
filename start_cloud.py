#!/usr/bin/env python3
"""
云端启动脚本 - 确保应用可以远程访问
"""

import os
import socket
from datetime import datetime

# 导入应用
from app import create_app, db
from app.models import Config, CourseRefund, CommissionConfig
import sqlite3

def get_server_info():
    """获取服务器信息"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return hostname, local_ip

def check_and_initialize_database():
    """启动前检查并初始化数据库"""
    db_path = 'instance/database.sqlite'
    
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    
    # 创建应用以获取上下文
    app = create_app()
    
    with app.app_context():
        try:
            Config.query.first()
        except Exception as e:
            if "no such table" in str(e):
                print("检测到数据库表不存在，正在创建...")
                try:
                    db.create_all()
                    print("✓ 数据库表创建成功")
                    
                    # 创建默认配置
                    default_configs = [
                        ('new_course_shareholder_a', '50'),
                        ('new_course_shareholder_b', '50'),
                        ('renewal_shareholder_a', '40'),
                        ('renewal_shareholder_b', '60'),
                        ('trial_cost', '30'),
                        ('course_cost', '30'),
                        ('taobao_fee_rate', '0.6'),
                    ]
                    
                    for key, value in default_configs:
                        config = Config(key=key, value=value)
                        db.session.add(config)
                    
                    db.session.commit()
                    print("✓ 默认配置创建成功")
                except Exception as create_error:
                    print(f"创建数据库时出错: {create_error}")
                    raise
    
    return app

def main():
    """主启动函数"""
    print("=" * 60)
    print("    客户管理系统 - 云端启动")
    print("=" * 60)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取服务器信息
    hostname, local_ip = get_server_info()
    print(f"服务器主机名: {hostname}")
    print(f"服务器内网IP: {local_ip}")
    print(f"公网IP: 117.72.145.165")
    
    # 初始化数据库
    print("\n正在初始化数据库...")
    app = check_and_initialize_database()
    
    # 启动信息
    print("\n" + "=" * 60)
    print("    启动成功！访问地址:")
    print("=" * 60)
    print(f"🌐 远程访问: http://117.72.145.165:5000")
    print(f"🏠 内网访问: http://{local_ip}:5000")
    print(f"💻 本地访问: http://localhost:5000")
    print("=" * 60)
    print("💡 提示:")
    print("  - 按 Ctrl+C 停止服务器")
    print("  - 确保防火墙已开放5000端口")
    print("  - 确保云服务器安全组已配置")
    print("=" * 60)
    
    # 启动应用
    try:
        print("\n🚀 正在启动Flask应用...")
        app.run(
            host='0.0.0.0',  # 监听所有接口
            port=5000,       # 端口5000
            debug=False      # 生产环境关闭debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == '__main__':
    main()


