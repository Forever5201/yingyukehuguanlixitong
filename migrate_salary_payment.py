"""
工资支付管理数据模型迁移脚本

创建 SalaryPayment 表用于记录员工工资和提成发放记录
"""

from app import create_app
from app.models import db
from datetime import datetime
import os
from sqlalchemy import text

def create_salary_payment_table():
    """创建工资支付表"""
    try:
        app = create_app()
        with app.app_context():
            # 创建工资支付表
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS salary_payment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    payment_month VARCHAR(7) NOT NULL,  -- 格式: 2025-09
                    base_salary FLOAT DEFAULT 0,        -- 基本工资
                    commission_amount FLOAT DEFAULT 0,  -- 提成金额
                    bonus FLOAT DEFAULT 0,              -- 奖金
                    deduction FLOAT DEFAULT 0,          -- 扣款
                    total_amount FLOAT NOT NULL,        -- 实发金额
                    payment_date DATE,                  -- 发放日期
                    payment_method VARCHAR(50),         -- 发放方式
                    notes TEXT,                         -- 备注
                    status VARCHAR(20) DEFAULT 'pending', -- pending/paid/cancelled
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employee (id),
                    UNIQUE (employee_id, payment_month)  -- 每个员工每月只能有一条记录
                )
            """))
            
            print("✓ salary_payment 表创建成功")
            
            # 创建索引
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_salary_payment_employee_id ON salary_payment (employee_id)"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_salary_payment_month ON salary_payment (payment_month)"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_salary_payment_status ON salary_payment (status)"))
            
            db.session.commit()
            print("✓ 索引创建成功")
            
    except Exception as e:
        print(f"✗ 创建工资支付表失败: {str(e)}")
        raise

if __name__ == '__main__':
    print("=== 创建工资支付管理表 ===")
    create_salary_payment_table()
    print("=== 迁移完成 ===")