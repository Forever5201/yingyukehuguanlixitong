#!/usr/bin/env python3
"""
安全修复脚本 - 自动修复代码中的严重安全问题
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """备份文件"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✓ 已备份: {backup_path}")
    return backup_path

def fix_exception_handling(content):
    """修复裸露的except语句"""
    # 修复 safe_float 和 safe_int 中的裸露except
    pattern = r'except:\s*\n\s*return default'
    replacement = 'except (ValueError, TypeError):\n        return default'
    
    fixed_content = re.sub(pattern, replacement, content)
    
    # 修复其他裸露的except（保守修复）
    pattern2 = r'except:\s*\n\s*pass'
    replacement2 = 'except Exception:\n        pass'
    
    fixed_content = re.sub(pattern2, replacement2, fixed_content)
    
    return fixed_content

def fix_sql_injection(content):
    """修复SQL注入风险"""
    # 在debug_tables函数前添加白名单
    whitelist_code = '''
# 允许的表名白名单（防止SQL注入）
ALLOWED_TABLES = ['config', 'employee', 'customer', 'course', 'taobao_order', 'commission_config']
'''
    
    # 找到 debug_tables 函数
    if '@main_bp.route(\'/api/debug/tables\')' in content or '@app.route(\'/api/debug/tables\')' in content:
        # 在函数中添加验证
        pattern = r'(result = db\.session\.execute\(f\'SELECT COUNT\(\*\) FROM {table}\'\))'
        replacement = '''if table not in ALLOWED_TABLES:
                raise ValueError(f"Invalid table name: {table}")
            result = db.session.execute(f'SELECT COUNT(*) FROM {table}')'''
        
        content = re.sub(pattern, replacement, content)
        
        # 添加白名单定义
        if 'ALLOWED_TABLES' not in content:
            # 在文件顶部的导入后添加
            import_end = content.find('\n\n', content.find('import '))
            if import_end > 0:
                content = content[:import_end] + '\n' + whitelist_code + content[import_end:]
    
    return content

def fix_config_security():
    """修复配置文件的安全问题"""
    config_path = 'config.py'
    
    if not os.path.exists(config_path):
        print(f"⚠️  配置文件不存在: {config_path}")
        return
    
    backup_file(config_path)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有 secrets 导入
    if 'import secrets' not in content:
        # 在 os 导入后添加 secrets 导入
        content = content.replace('import os', 'import os\nimport secrets')
    
    # 修复 SECRET_KEY
    old_secret_key = "SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'"
    new_secret_key = "SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)"
    
    if old_secret_key in content:
        content = content.replace(old_secret_key, new_secret_key)
        print("✓ 修复了 SECRET_KEY 硬编码问题")
    
    # 添加会话安全配置
    if 'SESSION_COOKIE_SECURE' not in content:
        session_config = '''
    # 会话安全配置
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 上传大小限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
'''
        # 在类定义的末尾添加
        class_end = content.rfind('}')
        if class_end > 0:
            content = content[:class_end] + session_config + '\n' + content[class_end:]
        else:
            content += session_config
        
        print("✓ 添加了会话安全配置")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 配置文件已更新: {config_path}")

def fix_routes_security():
    """修复路由文件的安全问题"""
    routes_path = 'app/routes.py'
    
    if not os.path.exists(routes_path):
        print(f"⚠️  路由文件不存在: {routes_path}")
        return
    
    backup_file(routes_path)
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复异常处理
    content = fix_exception_handling(content)
    print("✓ 修复了异常处理问题")
    
    # 修复SQL注入
    content = fix_sql_injection(content)
    print("✓ 修复了SQL注入风险")
    
    with open(routes_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 路由文件已更新: {routes_path}")

def fix_models_deprecation():
    """修复模型中的弃用警告"""
    models_path = 'app/models.py'
    
    if not os.path.exists(models_path):
        print(f"⚠️  模型文件不存在: {models_path}")
        return
    
    backup_file(models_path)
    
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加 timezone 导入
    if 'from datetime import datetime, timezone' not in content:
        content = content.replace(
            'from datetime import datetime',
            'from datetime import datetime, timezone'
        )
    
    # 替换 datetime.utcnow
    content = content.replace(
        'default=datetime.utcnow',
        'default=lambda: datetime.now(timezone.utc)'
    )
    
    print("✓ 修复了 datetime.utcnow 弃用警告")
    
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 模型文件已更新: {models_path}")

def create_env_template():
    """创建环境变量模板"""
    env_template = '''# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-use-secrets.token_hex(32)

# 数据库配置
DATABASE_URL=sqlite:///instance/database.sqlite

# 日志级别
LOG_LEVEL=INFO

# Redis URL (用于缓存和限流)
# REDIS_URL=redis://localhost:6379/0
'''
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✓ 创建了环境变量模板: .env.template")
    
    # 检查 .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore = f.read()
        
        if '.env' not in gitignore:
            with open('.gitignore', 'a', encoding='utf-8') as f:
                f.write('\n# 环境变量\n.env\n.env.local\n')
            print("✓ 更新了 .gitignore")

def main():
    """主函数"""
    print("=" * 60)
    print("安全修复脚本")
    print("=" * 60)
    
    print("\n⚠️  此脚本将修改您的代码文件，请确保已经提交或备份了所有更改！")
    
    response = input("\n是否继续？(y/N): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    print("\n开始修复...\n")
    
    # 1. 修复配置文件
    print("1. 修复配置文件安全问题")
    fix_config_security()
    
    # 2. 修复路由文件
    print("\n2. 修复路由文件安全问题")
    fix_routes_security()
    
    # 3. 修复模型文件
    print("\n3. 修复模型文件弃用警告")
    fix_models_deprecation()
    
    # 4. 创建环境变量模板
    print("\n4. 创建环境变量模板")
    create_env_template()
    
    print("\n" + "=" * 60)
    print("✅ 安全修复完成！")
    print("\n后续步骤：")
    print("1. 创建 .env 文件并设置 SECRET_KEY")
    print("2. 运行测试确保功能正常")
    print("3. 考虑实施其他优化建议")
    print("=" * 60)

if __name__ == '__main__':
    main()