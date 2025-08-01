from app import create_app
import os
import sqlite3

def check_and_migrate_database():
    """启动前检查并迁移数据库结构"""
    db_path = 'instance/database.sqlite'
    
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，将在首次启动时创建...")
        return
    
    # 检查是否需要添加新字段
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(taobao_order)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        # 检查 taobao_fee 字段
        if 'taobao_fee' not in columns:
            print("检测到数据库结构需要更新，添加 taobao_fee 字段...")
            cursor.execute("ALTER TABLE taobao_order ADD COLUMN taobao_fee FLOAT DEFAULT 0")
            conn.commit()
            print("数据库结构更新完成！")
        
    except Exception as e:
        print(f"数据库检查过程中出现错误: {e}")
    finally:
        conn.close()

# 启动前检查数据库
check_and_migrate_database()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)