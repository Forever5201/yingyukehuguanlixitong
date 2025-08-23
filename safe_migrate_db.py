"""
安全的数据库迁移脚本
保留所有现有数据，只添加新的表结构
"""
import sqlite3
import os
import shutil
from datetime import datetime

def safe_migrate_database():
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("错误：找不到数据库文件 instance/database.sqlite")
        return False
    
    # 1. 创建备份
    backup_path = os.path.join('instance', f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite')
    shutil.copy2(db_path, backup_path)
    print(f"✓ 已创建数据库备份: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 2. 开启事务
        cursor.execute("BEGIN TRANSACTION")
        
        print("\n正在检查并更新表结构...")
        
        # 3. 获取现有的course表列
        cursor.execute("PRAGMA table_info(course)")
        existing_columns = {column[1] for column in cursor.fetchall()}
        
        # 4. 需要添加的course表列
        course_columns_to_add = {
            'custom_trial_cost': 'FLOAT',
            'assigned_employee_id': 'INTEGER',
            'is_renewal': 'BOOLEAN DEFAULT 0',
            'renewal_from_course_id': 'INTEGER',
            'custom_course_cost': 'FLOAT',
            'snapshot_course_cost': 'FLOAT DEFAULT 0',
            'snapshot_fee_rate': 'FLOAT DEFAULT 0',
            'meta': 'TEXT'
        }
        
        # 5. 添加缺失的列
        added_columns = []
        for column_name, column_type in course_columns_to_add.items():
            if column_name not in existing_columns:
                sql = f"ALTER TABLE course ADD COLUMN {column_name} {column_type}"
                cursor.execute(sql)
                added_columns.append(column_name)
                print(f"✓ 添加列: course.{column_name}")
        
        if not added_columns:
            print("✓ course表结构已是最新")
        
        # 6. 检查并创建commission_config表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commission_config'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE commission_config (
                    id INTEGER NOT NULL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    commission_type VARCHAR(20) DEFAULT 'profit',
                    trial_rate FLOAT DEFAULT 0,
                    new_course_rate FLOAT DEFAULT 0,
                    renewal_rate FLOAT DEFAULT 0,
                    base_salary FLOAT DEFAULT 0,
                    created_at DATETIME,
                    updated_at DATETIME,
                    UNIQUE (employee_id),
                    FOREIGN KEY(employee_id) REFERENCES employee (id)
                )
            """)
            print("✓ 创建表: commission_config")
        else:
            print("✓ commission_config表已存在")
        
        # 7. 检查并添加必要的配置项（不覆盖现有配置）
        new_configs = [
            ('new_course_shareholder_a', '50'),
            ('new_course_shareholder_b', '50'),
            ('renewal_shareholder_a', '40'),
            ('renewal_shareholder_b', '60'),
            ('shareholder_a_name', '股东A'),
            ('shareholder_b_name', '股东B')
        ]
        
        added_configs = []
        for key, default_value in new_configs:
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, default_value))
                added_configs.append(key)
        
        if added_configs:
            print(f"✓ 添加配置项: {', '.join(added_configs)}")
        
        # 8. 提交事务
        cursor.execute("COMMIT")
        print("\n✅ 数据库迁移成功完成！")
        print(f"✅ 您的所有数据都已保留")
        print(f"✅ 备份文件位于: {backup_path}")
        
        # 9. 显示数据统计
        cursor.execute("SELECT COUNT(*) FROM customer")
        customer_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM course WHERE is_trial = 1")
        trial_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM course WHERE is_trial = 0")
        formal_count = cursor.fetchone()[0]
        
        print(f"\n数据统计:")
        print(f"- 客户数量: {customer_count}")
        print(f"- 试听课数量: {trial_count}")
        print(f"- 正课数量: {formal_count}")
        
        return True
        
    except Exception as e:
        # 如果出错，回滚事务
        cursor.execute("ROLLBACK")
        print(f"\n❌ 迁移失败: {e}")
        print(f"❌ 数据库已回滚到原始状态")
        print(f"❌ 备份文件位于: {backup_path}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("安全数据库迁移工具")
    print("=" * 50)
    print("此工具将:")
    print("1. 备份您的数据库")
    print("2. 保留所有现有数据")
    print("3. 只添加新的列和表")
    print("4. 不会删除或修改任何现有数据")
    print("=" * 50)
    
    response = input("\n是否继续？(y/n): ")
    if response.lower() == 'y':
        safe_migrate_database()
    else:
        print("已取消操作")