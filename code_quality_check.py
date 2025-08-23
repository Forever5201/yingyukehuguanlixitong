#!/usr/bin/env python3
"""
代码质量检查脚本
检查修复后的代码质量和潜在问题
"""

import os
import re
import sys

def check_code_quality():
    """检查代码质量"""
    issues = []
    
    # 检查文件列表
    files_to_check = [
        ('config.py', check_config_file),
        ('app/routes.py', check_routes_file),
        ('app/models.py', check_models_file),
        ('app/__init__.py', check_init_file)
    ]
    
    print("=" * 60)
    print("代码质量检查")
    print("=" * 60)
    
    for filepath, check_func in files_to_check:
        if os.path.exists(filepath):
            print(f"\n检查 {filepath}...")
            file_issues = check_func(filepath)
            if file_issues:
                issues.extend(file_issues)
                for issue in file_issues:
                    print(f"  ⚠️  {issue}")
            else:
                print("  ✅ 没有发现问题")
        else:
            print(f"\n⚠️  文件不存在: {filepath}")
            issues.append(f"文件不存在: {filepath}")
    
    # 检查环境配置
    print("\n检查环境配置...")
    env_issues = check_environment()
    if env_issues:
        issues.extend(env_issues)
        for issue in env_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ 环境配置正确")
    
    # 总结
    print("\n" + "=" * 60)
    if issues:
        print(f"❌ 发现 {len(issues)} 个问题需要关注")
        print("\n问题汇总：")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("✅ 代码质量检查通过！")
    
    return len(issues) == 0

def check_config_file(filepath):
    """检查配置文件"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查安全配置
    if 'import secrets' not in content:
        issues.append("缺少 secrets 模块导入")
    
    if "'a-hard-to-guess-string'" in content:
        issues.append("仍然存在硬编码的 SECRET_KEY")
    
    if 'SESSION_COOKIE_SECURE' not in content:
        issues.append("缺少会话安全配置")
    
    # 检查语法错误（缺少逗号）
    engine_options_match = re.search(r'SQLALCHEMY_ENGINE_OPTIONS\s*=\s*{([^}]+)}', content, re.DOTALL)
    if engine_options_match:
        options_content = engine_options_match.group(1)
        lines = options_content.strip().split('\n')
        for i, line in enumerate(lines[:-1]):  # 检查除最后一行外的所有行
            if line.strip() and not line.strip().endswith(','):
                issues.append(f"SQLALCHEMY_ENGINE_OPTIONS 中可能缺少逗号: {line.strip()}")
    
    return issues

def check_routes_file(filepath):
    """检查路由文件"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查裸露的except
    if re.search(r'except:\s*$', content, re.MULTILINE):
        issues.append("存在裸露的 except 语句")
    
    # 检查是否有安全转换函数
    if 'def safe_float' not in content:
        issues.append("缺少 safe_float 函数")
    
    if 'def safe_int' not in content:
        issues.append("缺少 safe_int 函数")
    
    # 检查异常处理是否正确
    if 'except (ValueError, TypeError):' not in content:
        issues.append("safe_float/safe_int 可能没有使用正确的异常处理")
    
    # 检查SQL注入防护（如果有动态SQL）
    if re.search(r'execute.*f["\'].*{.*}', content):
        if 'ALLOWED_TABLES' not in content:
            issues.append("存在动态SQL但缺少白名单验证")
    
    return issues

def check_models_file(filepath):
    """检查模型文件"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查datetime导入
    if 'from datetime import datetime, timezone' not in content:
        issues.append("缺少 timezone 导入")
    
    # 检查是否还有 datetime.utcnow
    if 'datetime.utcnow' in content:
        issues.append("仍然存在已弃用的 datetime.utcnow")
    
    # 检查是否使用了正确的时区
    if 'datetime.now(timezone.utc)' not in content:
        issues.append("可能没有使用 timezone.utc")
    
    return issues

def check_init_file(filepath):
    """检查初始化文件"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有Flask-SQLAlchemy导入
    if 'from flask_sqlalchemy import SQLAlchemy' not in content:
        issues.append("缺少 Flask-SQLAlchemy 导入")
    
    # 检查是否有create_app函数
    if 'def create_app' not in content:
        issues.append("缺少 create_app 工厂函数")
    
    return issues

def check_environment():
    """检查环境配置"""
    issues = []
    
    # 检查.env.template
    if not os.path.exists('.env.template'):
        issues.append("缺少 .env.template 文件")
    
    # 检查.gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore = f.read()
        if '.env' not in gitignore:
            issues.append(".gitignore 未包含 .env")
        if '*.backup_*' not in gitignore and 'backup_' not in gitignore:
            issues.append(".gitignore 未包含备份文件模式")
    else:
        issues.append("缺少 .gitignore 文件")
    
    # 检查instance目录
    if not os.path.exists('instance'):
        issues.append("缺少 instance 目录")
    
    return issues

def main():
    """主函数"""
    success = check_code_quality()
    
    print("\n" + "=" * 60)
    print("建议的后续步骤：")
    print("1. 创建 .env 文件：python create_env.py")
    print("2. 初始化数据库：python fix_database_now.py")
    print("3. 运行应用：python run.py")
    print("4. 运行测试：python test_all_fixed.py")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())