#!/usr/bin/env python
"""
系统诊断工具
检查客户管理系统的所有依赖和配置
"""
import sys
import os

print("="*60)
print("客户管理系统诊断工具")
print("="*60)
print()

# 1. 检查Python版本
print("1. Python 版本检查:")
print(f"   当前版本: {sys.version}")
if sys.version_info < (3, 6):
    print("   ❌ 需要 Python 3.6 或更高版本")
else:
    print("   ✅ Python 版本符合要求")
print()

# 2. 检查必要的包
print("2. 依赖包检查:")
required_packages = {
    'flask': 'Flask',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask_migrate': 'Flask-Migrate',
    'pandas': 'pandas',
    'openpyxl': 'openpyxl',
    'xlsxwriter': 'XlsxWriter'
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"   ✅ {package} 已安装")
    except ImportError:
        print(f"   ❌ {package} 未安装")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   缺失的包: {', '.join(missing_packages)}")
    print(f"   请运行: pip install {' '.join(missing_packages)}")
print()

# 3. 检查项目结构
print("3. 项目结构检查:")
required_dirs = ['app', 'app/templates', 'app/static', 'instance']
required_files = ['run.py', 'config.py', 'app/__init__.py', 'app/models.py', 'app/routes.py']

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"   ✅ 目录 {dir_path} 存在")
    else:
        print(f"   ❌ 目录 {dir_path} 缺失")

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ 文件 {file_path} 存在")
    else:
        print(f"   ❌ 文件 {file_path} 缺失")
print()

# 4. 检查数据库
print("4. 数据库检查:")
db_path = 'instance/database.sqlite'
if os.path.exists(db_path):
    size = os.path.getsize(db_path) / 1024  # KB
    print(f"   ✅ 数据库文件存在 ({size:.2f} KB)")
    
    # 检查数据库表
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   ✅ 数据库包含 {len(tables)} 个表:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"      - {table[0]}: {count} 条记录")
        conn.close()
    except Exception as e:
        print(f"   ❌ 数据库检查失败: {e}")
else:
    print("   ⚠️  数据库文件不存在，将在首次启动时创建")
print()

# 5. 测试应用创建
print("5. 应用初始化测试:")
try:
    from app import create_app
    app = create_app()
    print("   ✅ 应用创建成功")
    
    # 检查配置
    print("   配置信息:")
    print(f"      - SECRET_KEY: {'已设置' if app.config.get('SECRET_KEY') else '未设置'}")
    print(f"      - 数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '未设置')}")
except Exception as e:
    print(f"   ❌ 应用创建失败: {e}")
print()

# 6. 总结
print("="*60)
print("诊断总结:")
if missing_packages:
    print("❌ 系统存在问题，请先安装缺失的依赖包")
    print("   运行: install_all_deps.bat (Windows) 或 pip install -r requirements.txt")
else:
    print("✅ 系统检查通过，可以正常启动")
    print("   运行: start.bat (Windows) 或 python run.py")
print("="*60)