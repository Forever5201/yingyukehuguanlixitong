#!/usr/bin/env python3
"""
自动数据库迁移脚本
在git pull后自动检测并应用数据库结构更新
"""
import sqlite3
import os
import sys
import shutil
from datetime import datetime
import hashlib
import json

class DatabaseMigrator:
    def __init__(self):
        self.db_path = os.path.join('instance', 'database.sqlite')
        self.migration_log_path = os.path.join('instance', '.migration_history.json')
        self.schema_path = 'schema.sql'
        
    def get_schema_hash(self):
        """获取schema.sql文件的hash值"""
        if os.path.exists(self.schema_path):
            with open(self.schema_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        return None
    
    def load_migration_history(self):
        """加载迁移历史"""
        if os.path.exists(self.migration_log_path):
            with open(self.migration_log_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_migration_history(self, history):
        """保存迁移历史"""
        os.makedirs('instance', exist_ok=True)
        with open(self.migration_log_path, 'w') as f:
            json.dump(history, f, indent=2)
    
    def needs_migration(self):
        """检查是否需要迁移"""
        if not os.path.exists(self.db_path):
            print("⚠️  数据库不存在，将创建新数据库")
            return 'create'
        
        current_hash = self.get_schema_hash()
        history = self.load_migration_history()
        last_hash = history.get('last_schema_hash')
        
        if current_hash != last_hash:
            print("📊 检测到数据库结构更新")
            return 'update'
        
        return None
    
    def create_database(self):
        """创建新数据库"""
        print("🔨 创建新数据库...")
        os.makedirs('instance', exist_ok=True)
        
        # 运行init_database.py
        if os.path.exists('init_database.py'):
            os.system(f'{sys.executable} init_database.py')
        else:
            # 直接从schema.sql创建
            conn = sqlite3.connect(self.db_path)
            with open(self.schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.close()
        
        # 记录schema hash
        history = {'last_schema_hash': self.get_schema_hash(), 'migrations': []}
        self.save_migration_history(history)
        print("✅ 数据库创建成功")
    
    def migrate_database(self):
        """迁移现有数据库"""
        # 创建备份
        backup_path = os.path.join('instance', f'auto_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite')
        shutil.copy2(self.db_path, backup_path)
        print(f"💾 已创建备份: {backup_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # 获取所有表的当前结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            changes_made = []
            
            # 检查course表的列
            cursor.execute("PRAGMA table_info(course)")
            existing_columns = {col[1] for col in cursor.fetchall()}
            
            required_columns = {
                'custom_trial_cost': 'FLOAT',
                'assigned_employee_id': 'INTEGER',
                'is_renewal': 'BOOLEAN DEFAULT 0',
                'renewal_from_course_id': 'INTEGER',
                'custom_course_cost': 'FLOAT',
                'snapshot_course_cost': 'FLOAT DEFAULT 0',
                'snapshot_fee_rate': 'FLOAT DEFAULT 0',
                'meta': 'TEXT'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE course ADD COLUMN {col_name} {col_type}")
                    changes_made.append(f"添加列 course.{col_name}")
            
            # 检查commission_config表
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
                changes_made.append("创建表 commission_config")
            
            # 添加新的配置项
            new_configs = [
                ('new_course_shareholder_a', '50'),
                ('new_course_shareholder_b', '50'),
                ('renewal_shareholder_a', '40'),
                ('renewal_shareholder_b', '60'),
                ('shareholder_a_name', '股东A'),
                ('shareholder_b_name', '股东B')
            ]
            
            for key, value in new_configs:
                cursor.execute("SELECT 1 FROM config WHERE key = ?", (key,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, value))
                    changes_made.append(f"添加配置 {key}")
            
            cursor.execute("COMMIT")
            
            # 更新迁移历史
            history = self.load_migration_history()
            history['last_schema_hash'] = self.get_schema_hash()
            history.setdefault('migrations', []).append({
                'date': datetime.now().isoformat(),
                'changes': changes_made,
                'backup': backup_path
            })
            self.save_migration_history(history)
            
            if changes_made:
                print("✅ 数据库迁移成功！")
                print("📝 更新内容：")
                for change in changes_made:
                    print(f"   - {change}")
            else:
                print("✅ 数据库已是最新版本")
                
        except Exception as e:
            cursor.execute("ROLLBACK")
            print(f"❌ 迁移失败: {e}")
            print(f"💾 您的数据是安全的，备份位于: {backup_path}")
            raise
        finally:
            conn.close()
    
    def run(self):
        """执行迁移"""
        print("=" * 50)
        print("🔄 自动数据库迁移工具")
        print("=" * 50)
        
        action = self.needs_migration()
        
        if action == 'create':
            self.create_database()
        elif action == 'update':
            self.migrate_database()
        else:
            print("✅ 数据库已是最新版本，无需迁移")
        
        # 清理旧备份（保留最近5个）
        self.cleanup_old_backups()
    
    def cleanup_old_backups(self):
        """清理旧的备份文件，只保留最近5个"""
        if not os.path.exists('instance'):
            return
            
        backups = [f for f in os.listdir('instance') if f.startswith('auto_backup_')]
        backups.sort(reverse=True)
        
        # 保留最近5个备份
        for old_backup in backups[5:]:
            os.remove(os.path.join('instance', old_backup))
            print(f"🗑️  清理旧备份: {old_backup}")

if __name__ == "__main__":
    try:
        migrator = DatabaseMigrator()
        migrator.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)