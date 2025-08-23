#!/usr/bin/env python3
"""测试Python环境和导入"""

import sys
import os

print("=" * 60)
print("Python 环境测试")
print("=" * 60)

# 显示Python版本
print(f"\nPython 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")

# 测试基本导入
print("\n测试基本导入...")
try:
    import os
    import secrets
    print("✓ 标准库导入成功")
except Exception as e:
    print(f"✗ 标准库导入失败: {e}")

# 测试config.py
print("\n测试 config.py...")
try:
    import config
    print("✓ config.py 导入成功")
    print(f"  - SECRET_KEY 类型: {type(config.Config.SECRET_KEY)}")
    print(f"  - 数据库URI: {config.Config.SQLALCHEMY_DATABASE_URI[:50]}...")
except Exception as e:
    print(f"✗ config.py 导入失败: {e}")
    print("\n尝试手动编译...")
    try:
        import py_compile
        py_compile.compile('config.py')
        print("✓ config.py 编译成功")
    except Exception as ce:
        print(f"✗ config.py 编译失败: {ce}")

# 测试Flask
print("\n测试 Flask...")
try:
    import flask
    print(f"✓ Flask 版本: {flask.__version__}")
except ImportError:
    print("✗ Flask 未安装，请运行: pip install flask")

# 测试SQLAlchemy
print("\n测试 SQLAlchemy...")
try:
    import sqlalchemy
    print(f"✓ SQLAlchemy 版本: {sqlalchemy.__version__}")
except ImportError:
    print("✗ SQLAlchemy 未安装，请运行: pip install sqlalchemy")

# 测试应用导入
print("\n测试应用导入...")
try:
    from app import create_app
    print("✓ 应用导入成功")
    app = create_app()
    print("✓ 应用创建成功")
except Exception as e:
    print(f"✗ 应用导入/创建失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)