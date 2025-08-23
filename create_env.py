#!/usr/bin/env python3
"""
创建安全的 .env 文件
"""

import secrets
import os

def create_env_file():
    """创建 .env 文件"""
    
    # 生成安全的 SECRET_KEY
    secret_key = secrets.token_hex(32)
    
    env_content = f"""# Flask配置
FLASK_ENV=development
SECRET_KEY={secret_key}

# 数据库配置
DATABASE_URL=sqlite:///instance/database.sqlite

# 日志级别
LOG_LEVEL=INFO

# Redis URL (用于缓存和限流)
# REDIS_URL=redis://localhost:6379/0

# 其他配置
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
"""
    
    # 检查是否已存在
    if os.path.exists('.env'):
        response = input(".env 文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # 写入文件
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✓ .env 文件已创建")
    print(f"✓ SECRET_KEY: {secret_key}")
    print("\n⚠️  请妥善保管 SECRET_KEY，不要提交到版本控制系统！")
    
    # 确保 .gitignore 包含 .env
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore = f.read()
        
        if '.env' not in gitignore:
            with open('.gitignore', 'a', encoding='utf-8') as f:
                f.write('\n# 环境变量\n.env\n.env.local\n')
            print("✓ 已更新 .gitignore")

if __name__ == '__main__':
    print("=" * 60)
    print("创建安全的环境配置文件")
    print("=" * 60)
    create_env_file()