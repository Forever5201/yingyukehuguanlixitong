#!/usr/bin/env python3
"""
数据库初始化脚本
用于在新环境中一键创建数据库表结构（不包含数据）
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_database():
    """创建数据库表结构"""
    
    # 创建 Flask 应用
    app = Flask(__name__)
    
    # 配置数据库
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "database.sqlite")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db = SQLAlchemy()
    db.init_app(app)
    
    # 确保 instance 目录存在
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
    with app.app_context():
        # 导入模型（这会注册所有表结构）
        try:
            from app.models import Customer, Employee, Course, TaobaoOrder, Config
            
            # 创建所有表
            db.create_all()
            
            print("✅ 数据库表结构创建成功！")
            print(f"📁 数据库文件位置: {os.path.join(basedir, 'instance', 'database.sqlite')}")
            
            # 检查创建的表
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"🗄️  已创建的表: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建数据库表结构失败: {e}")
            return False

def init_from_schema():
    """从 schema.sql 文件初始化数据库（备用方法）"""
    import sqlite3
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'database.sqlite')
    schema_path = os.path.join(basedir, 'schema.sql')
    
    # 确保 instance 目录存在
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
    try:
        # 检查 schema.sql 是否存在
        if not os.path.exists(schema_path):
            print(f"❌ 找不到 schema.sql 文件: {schema_path}")
            return False
            
        # 连接数据库并执行 schema
        conn = sqlite3.connect(db_path)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        print("✅ 从 schema.sql 创建数据库表结构成功！")
        print(f"📁 数据库文件位置: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 从 schema.sql 创建数据库失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 开始初始化数据库...")
    print("=" * 50)
    
    # 首先尝试使用 Flask-SQLAlchemy 模型创建
    success = create_database()
    
    # 如果失败，尝试使用 schema.sql
    if not success:
        print("\n⚠️  尝试使用备用方法（schema.sql）...")
        success = init_from_schema()
    
    if success:
        print("\n🎉 数据库初始化完成！")
        print("💡 现在可以运行 python run.py 启动应用了")
    else:
        print("\n💥 数据库初始化失败，请检查错误信息")
        sys.exit(1)