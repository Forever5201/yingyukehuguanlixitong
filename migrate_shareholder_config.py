"""
股东分配配置迁移脚本
将旧的分开的新课/续课配置迁移为统一的配置
"""

from app import create_app, db
from app.models import Config

def migrate_shareholder_config():
    """迁移股东分配配置"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("开始迁移股东分配配置")
        print("=" * 50)
        
        # 1. 读取旧配置
        old_configs = {}
        config_keys = [
            'new_course_shareholder_a',
            'new_course_shareholder_b',
            'renewal_shareholder_a',
            'renewal_shareholder_b'
        ]
        
        for key in config_keys:
            config = Config.query.filter_by(key=key).first()
            if config:
                old_configs[key] = float(config.value)
                print(f"找到旧配置: {key} = {config.value}")
        
        # 2. 确定新配置值
        # 如果有旧配置，使用新课的比例作为统一比例（因为新课通常是主要业务）
        # 如果没有旧配置，使用默认值50:50
        new_ratio_a = old_configs.get('new_course_shareholder_a', 50)
        new_ratio_b = old_configs.get('new_course_shareholder_b', 50)
        
        # 确保比例和为100
        if new_ratio_a + new_ratio_b != 100:
            new_ratio_b = 100 - new_ratio_a
        
        print(f"\n新配置值:")
        print(f"shareholder_a_ratio = {new_ratio_a}")
        print(f"shareholder_b_ratio = {new_ratio_b}")
        
        # 3. 创建或更新新配置
        try:
            # 股东A比例
            config_a = Config.query.filter_by(key='shareholder_a_ratio').first()
            if config_a:
                config_a.value = str(new_ratio_a)
                print(f"\n更新 shareholder_a_ratio = {new_ratio_a}")
            else:
                config_a = Config(key='shareholder_a_ratio', value=str(new_ratio_a))
                db.session.add(config_a)
                print(f"\n创建 shareholder_a_ratio = {new_ratio_a}")
            
            # 股东B比例
            config_b = Config.query.filter_by(key='shareholder_b_ratio').first()
            if config_b:
                config_b.value = str(new_ratio_b)
                print(f"更新 shareholder_b_ratio = {new_ratio_b}")
            else:
                config_b = Config(key='shareholder_b_ratio', value=str(new_ratio_b))
                db.session.add(config_b)
                print(f"创建 shareholder_b_ratio = {new_ratio_b}")
            
            # 提交更改
            db.session.commit()
            print("\n✅ 新配置已保存")
            
            # 4. 可选：删除旧配置
            print("\n是否删除旧配置？")
            print("旧配置包括:")
            for key in config_keys:
                if key in old_configs:
                    print(f"  - {key} = {old_configs[key]}")
            
            delete_old = input("\n删除旧配置？(y/n): ").lower().strip()
            if delete_old == 'y':
                for key in config_keys:
                    config = Config.query.filter_by(key=key).first()
                    if config:
                        db.session.delete(config)
                        print(f"删除: {key}")
                
                db.session.commit()
                print("\n✅ 旧配置已删除")
            else:
                print("\n保留旧配置")
            
            print("\n" + "=" * 50)
            print("配置迁移完成！")
            print("=" * 50)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_shareholder_config()