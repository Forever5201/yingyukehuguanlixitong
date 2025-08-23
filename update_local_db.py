"""
本地数据库更新脚本
用于更新现有数据库结构，添加新字段
"""
import sqlite3
import os

def update_database():
    db_path = os.path.join('instance', 'database.sqlite')
    
    if not os.path.exists(db_path):
        print("错误：找不到数据库文件 instance/database.sqlite")
        print("请先运行 python init_database.py 创建数据库")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("开始更新数据库结构...")
    
    # 获取现有的course表列
    cursor.execute("PRAGMA table_info(course)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    print(f"现有列: {existing_columns}")
    
    # 需要添加的列
    columns_to_add = [
        ('custom_trial_cost', 'FLOAT'),
        ('assigned_employee_id', 'INTEGER'),
        ('is_renewal', 'BOOLEAN DEFAULT 0'),
        ('renewal_from_course_id', 'INTEGER'),
        ('custom_course_cost', 'FLOAT'),
        ('snapshot_course_cost', 'FLOAT DEFAULT 0'),
        ('snapshot_fee_rate', 'FLOAT DEFAULT 0'),
        ('meta', 'TEXT')
    ]
    
    # 添加缺失的列
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                sql = f"ALTER TABLE course ADD COLUMN {column_name} {column_type}"
                cursor.execute(sql)
                print(f"✓ 已添加列: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ 添加列 {column_name} 时出错: {e}")
    
    # 检查并创建commission_config表
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
        print("✓ 已创建commission_config表")
    
    # 添加默认配置数据（如果不存在）
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        configs = [
            ('trial_cost', '100'),
            ('course_cost', '200'),
            ('taobao_fee_rate', '0.6'),
            ('new_course_shareholder_a', '50'),
            ('new_course_shareholder_b', '50'),
            ('renewal_shareholder_a', '40'),
            ('renewal_shareholder_b', '60'),
            ('shareholder_a_name', '股东A'),
            ('shareholder_b_name', '股东B')
        ]
        
        for key, value in configs:
            cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (key, value))
        print("✓ 已添加默认配置")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("\n数据库更新完成！")
    print("现在可以正常运行程序了。")

if __name__ == "__main__":
    update_database()