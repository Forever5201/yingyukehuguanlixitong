#!/usr/bin/env python3
"""
验证安全修复是否成功
"""

import os
import sys
import re

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_file_content(filepath, pattern, should_exist=True):
    """检查文件内容"""
    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if should_exist:
        if re.search(pattern, content):
            return True, "✓ 已修复"
        else:
            return False, "✗ 未找到预期的修复"
    else:
        if re.search(pattern, content):
            return False, "✗ 仍然存在问题"
        else:
            return True, "✓ 问题已修复"

def verify_config():
    """验证配置文件修复"""
    print("\n1. 验证配置文件 (config.py)")
    print("-" * 40)
    
    # 检查 secrets 导入
    success, msg = check_file_content('config.py', r'import secrets')
    print(f"  secrets 导入: {msg}")
    
    # 检查 SECRET_KEY 修复
    success, msg = check_file_content('config.py', r"SECRET_KEY.*secrets\.token_hex\(32\)")
    print(f"  SECRET_KEY 修复: {msg}")
    
    # 检查旧的硬编码不存在
    success, msg = check_file_content('config.py', r"'a-hard-to-guess-string'", should_exist=False)
    print(f"  硬编码移除: {msg}")
    
    # 检查会话安全配置
    success, msg = check_file_content('config.py', r'SESSION_COOKIE_SECURE')
    print(f"  会话安全配置: {msg}")

def verify_routes():
    """验证路由文件修复"""
    print("\n2. 验证路由文件 (app/routes.py)")
    print("-" * 40)
    
    # 检查异常处理修复
    success, msg = check_file_content('app/routes.py', r'except \(ValueError, TypeError\):')
    print(f"  异常处理修复: {msg}")
    
    # 检查裸露的except不存在
    success, msg = check_file_content('app/routes.py', r'except:\s*\n\s*return default', should_exist=False)
    print(f"  裸露except移除: {msg}")
    
    # 检查SQL注入防护
    success, msg = check_file_content('app/routes.py', r'ALLOWED_TABLES')
    print(f"  SQL注入防护: {msg}")

def verify_models():
    """验证模型文件修复"""
    print("\n3. 验证模型文件 (app/models.py)")
    print("-" * 40)
    
    # 检查 timezone 导入
    success, msg = check_file_content('app/models.py', r'from datetime import datetime, timezone')
    print(f"  timezone 导入: {msg}")
    
    # 检查 datetime.utcnow 替换
    success, msg = check_file_content('app/models.py', r'datetime\.now\(timezone\.utc\)')
    print(f"  datetime.now(timezone.utc): {msg}")
    
    # 检查旧的 utcnow 不存在
    success, msg = check_file_content('app/models.py', r'datetime\.utcnow\(\)', should_exist=False)
    print(f"  datetime.utcnow 移除: {msg}")

def verify_env_template():
    """验证环境变量模板"""
    print("\n4. 验证环境变量模板")
    print("-" * 40)
    
    if os.path.exists('.env.template'):
        print("  ✓ .env.template 已创建")
        
        # 检查 .gitignore
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                if '.env' in f.read():
                    print("  ✓ .gitignore 已更新")
                else:
                    print("  ⚠️  .gitignore 未包含 .env")
    else:
        print("  ✗ .env.template 未创建")

def test_imports():
    """测试修复后的导入"""
    print("\n5. 测试导入")
    print("-" * 40)
    
    try:
        from app import create_app
        print("  ✓ 应用可以正常导入")
        
        # 测试创建应用
        app = create_app()
        print("  ✓ 应用可以正常创建")
        
        # 检查配置
        if hasattr(app.config, 'SESSION_COOKIE_SECURE'):
            print("  ✓ 会话安全配置已加载")
        
        # 测试数据库
        with app.app_context():
            from app import db
            from app.models import Config
            try:
                # 使用正确的 text() 包装
                from sqlalchemy import text
                result = db.session.execute(text("SELECT 1"))
                print("  ✓ 数据库连接正常")
            except Exception as e:
                print(f"  ⚠️  数据库连接问题: {e}")
                
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")

def check_backups():
    """检查备份文件"""
    print("\n6. 备份文件")
    print("-" * 40)
    
    backup_patterns = [
        'config.py.backup_*',
        'app/routes.py.backup_*',
        'app/models.py.backup_*'
    ]
    
    import glob
    backup_count = 0
    for pattern in backup_patterns:
        backups = glob.glob(pattern)
        backup_count += len(backups)
        if backups:
            for backup in backups[-1:]:  # 只显示最新的
                print(f"  ✓ {backup}")
    
    if backup_count > 0:
        print(f"\n  共找到 {backup_count} 个备份文件")

def main():
    """主函数"""
    print("=" * 60)
    print("安全修复验证")
    print("=" * 60)
    
    # 验证各个修复
    verify_config()
    verify_routes()
    verify_models()
    verify_env_template()
    test_imports()
    check_backups()
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("\n建议后续步骤：")
    print("1. 创建 .env 文件并设置环境变量")
    print("2. 运行 python fix_database_now.py 验证数据库")
    print("3. 运行 python run.py 启动应用")
    print("4. 运行测试套件确保功能正常")
    print("=" * 60)

if __name__ == '__main__':
    main()