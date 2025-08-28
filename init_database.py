#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建所有必要的表结构和初始配置数据
"""

import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Config, Employee, Customer, Course, TaobaoOrder, CommissionConfig


def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 检查数据库文件
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"\n数据库路径: {db_path}")
        
        # 创建所有表
        print("\n创建数据库表结构...")
        try:
            db.create_all()
            print("✓ 表结构创建成功")
        except Exception as e:
            print(f"✗ 创建表结构失败: {e}")
            return False
        
        # 检查并创建必要的配置项
        print("\n检查配置项...")
        default_configs = [
            ('shareholder_a_ratio', '50', '股东A分配比例'),
            ('shareholder_b_ratio', '50', '股东B分配比例'),
            ('shareholder_a_name', '股东A', '股东A名称'),
            ('shareholder_b_name', '股东B', '股东B名称'),
            ('trial_cost', '30', '试听课成本'),
            ('course_cost', '30', '正课成本'),
            ('taobao_fee_rate', '0.6', '淘宝费率(百分比)'),
        ]
        
        created_count = 0
        for key, value, description in default_configs:
            config = Config.query.filter_by(key=key).first()
            if not config:
                config = Config(key=key, value=value)
                db.session.add(config)
                created_count += 1
                print(f"  ✓ 创建配置: {key} = {value} ({description})")
            else:
                print(f"  - 配置已存在: {key} = {config.value}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✓ 成功创建 {created_count} 个配置项")
        else:
            print("\n✓ 所有配置项已存在")
        
        # 显示表信息
        print("\n数据库表信息:")
        print("-" * 40)
        
        # 获取所有表名
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        for table in sorted(tables):
            # 获取表的行数
            if table == 'employee':
                count = Employee.query.count()
            elif table == 'customer':
                count = Customer.query.count()
            elif table == 'course':
                count = Course.query.count()
            elif table == 'config':
                count = Config.query.count()
            elif table == 'taobao_order':
                count = TaobaoOrder.query.count()
            elif table == 'commission_config':
                count = CommissionConfig.query.count()
            else:
                count = '?'
            
            print(f"  {table:<20} {count:>5} 条记录")
        
        print("\n✅ 数据库初始化完成！")
        return True


def check_database_health():
    """检查数据库健康状态"""
    print("\n" + "=" * 60)
    print("数据库健康检查")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 测试查询
            config_count = Config.query.count()
            print(f"✓ 配置表可访问，包含 {config_count} 条记录")
            
            # 测试关键配置
            required_keys = ['shareholder_a_ratio', 'shareholder_b_ratio', 'trial_cost']
            missing_keys = []
            
            for key in required_keys:
                config = Config.query.filter_by(key=key).first()
                if not config:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"⚠️  缺少必要的配置项: {', '.join(missing_keys)}")
                return False
            else:
                print("✓ 所有必要的配置项都存在")
            
            return True
            
        except Exception as e:
            print(f"✗ 数据库访问失败: {e}")
            return False


if __name__ == '__main__':
    # 运行初始化
    success = init_database()
    
    if success:
        # 运行健康检查
        check_database_health()
        
        print("\n" + "=" * 60)
        print("初始化完成！您现在可以运行应用了:")
        print("python run.py")
        print("=" * 60)
    else:
        print("\n✗ 初始化失败，请检查错误信息")
        sys.exit(1)