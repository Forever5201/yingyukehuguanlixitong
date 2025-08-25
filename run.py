from app import create_app, db
from app.models import Config, CourseRefund
import os
import sqlite3

def check_and_initialize_database():
    """启动前检查并初始化数据库"""
    db_path = 'instance/database.sqlite'
    
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    
    # 创建应用以获取上下文
    app = create_app()
    
    with app.app_context():
        # 如果数据库不存在或缺少表，创建它们
        try:
            # 尝试查询config表
            Config.query.first()
        except Exception as e:
            if "no such table" in str(e):
                print("检测到数据库表不存在，正在创建...")
                try:
                    # 创建所有表
                    db.create_all()
                    print("✓ 数据库表创建成功")
                    
                    # 创建默认配置
                    default_configs = [
                        ('new_course_shareholder_a', '50'),
                        ('new_course_shareholder_b', '50'),
                        ('renewal_shareholder_a', '40'),
                        ('renewal_shareholder_b', '60'),
                        ('trial_cost', '30'),
                        ('course_cost', '30'),
                        ('taobao_fee_rate', '0.6'),
                    ]
                    
                    for key, value in default_configs:
                        config = Config(key=key, value=value)
                        db.session.add(config)
                    
                    db.session.commit()
                    print("✓ 默认配置创建成功")
                except Exception as create_error:
                    print(f"创建数据库时出错: {create_error}")
                    raise

        # 单独检查并创建缺失的 course_refund 表
        try:
            CourseRefund.query.first()
        except Exception as e:
            if "no such table" in str(e):
                try:
                    print("检测到缺失表 course_refund，正在创建...")
                    CourseRefund.__table__.create(db.engine)
                    print("✓ course_refund 表创建成功")
                except Exception as ce:
                    print(f"创建 course_refund 表失败: {ce}")
                    raise
    
    # 检查特定字段更新（保留原有逻辑）
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(taobao_order)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}
            
            # 检查 taobao_fee 字段
            if columns and 'taobao_fee' not in columns:
                print("检测到数据库结构需要更新，添加 taobao_fee 字段...")
                cursor.execute("ALTER TABLE taobao_order ADD COLUMN taobao_fee FLOAT DEFAULT 0")
                conn.commit()
                print("数据库结构更新完成！")
            
            # 兜底检查：如果 course_refund 表仍不存在，提示信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='course_refund'")
            if cursor.fetchone() is None:
                print("警告: 未检测到 course_refund 表。请运行迁移或重启后由自动创建逻辑处理。")
            
        except Exception as e:
            # 忽略表不存在的错误
            if "no such table" not in str(e):
                print(f"数据库检查过程中出现错误: {e}")
        finally:
            conn.close()

# 启动前检查数据库
check_and_initialize_database()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)