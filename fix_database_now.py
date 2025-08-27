#!/usr/bin/env python3
"""
快速修复数据库问题
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    print("=" * 60)
    print("快速修复数据库")
    print("=" * 60)
    
    # 备份现有数据库
    db_path = 'instance/database.sqlite'
    if os.path.exists(db_path):
        import shutil
        backup_path = f'{db_path}.backup'
        shutil.copy2(db_path, backup_path)
        print(f"✓ 已备份数据库到: {backup_path}")
    
    # 导入必要的模块
    from app import create_app, db
    from app.models import Config, Employee, Customer, Course, TaobaoOrder, CommissionConfig
    
    app = create_app()
    
    with app.app_context():
        print("\n正在创建缺失的表...")
        
        try:
            # 创建所有表
            db.create_all()
            print("✓ 表结构创建/更新成功")
            
            # 检查config表是否有数据
            config_count = Config.query.count()
            
            if config_count == 0:
                print("\n创建默认配置...")
                configs = [
                    Config(key='shareholder_a_ratio', value='50'),
                    Config(key='shareholder_b_ratio', value='50'),
                    Config(key='shareholder_a_name', value='股东A'),
                    Config(key='shareholder_b_name', value='股东B'),
                    Config(key='trial_cost', value='30'),
                    Config(key='course_cost', value='30'),
                    Config(key='taobao_fee_rate', value='0.6'),
                ]
                
                for config in configs:
                    db.session.add(config)
                
                db.session.commit()
                print("✓ 默认配置创建成功")
            else:
                print(f"✓ 配置表已有 {config_count} 条记录")
            
            # 验证所有表
            print("\n验证数据库表:")
            tables = ['config', 'employee', 'customer', 'course', 'taobao_order', 'commission_config']
            
            for table in tables:
                try:
                    from sqlalchemy import text
                    result = db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    count = result.scalar()
                    print(f"  ✓ {table:<20} - {count} 条记录")
                except Exception as e:
                    print(f"  ✗ {table:<20} - 错误: {e}")
            
            print("\n✅ 数据库修复完成！")
            print("\n现在可以重新运行应用了:")
            print("  python run.py")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 修复失败: {e}")
            print("\n如果问题持续，请尝试:")
            print("1. 删除 instance/database.sqlite 文件")
            print("2. 运行 python init_database.py")
            return False


if __name__ == '__main__':
    success = fix_database()
    sys.exit(0 if success else 1)