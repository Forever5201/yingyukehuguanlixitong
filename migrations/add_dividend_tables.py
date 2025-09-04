"""
添加股东分红记录管理表
迁移脚本
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Index

# revision identifiers
revision = 'add_dividend_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """添加分红记录相关表"""
    
    # 创建股东分红记录表
    op.create_table(
        'dividend_record',
        sa.Column('id', sa.Integer(), primary_key=True),
        
        # 基本信息
        sa.Column('shareholder_name', sa.String(100), nullable=False),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        
        # 分红金额信息
        sa.Column('calculated_profit', sa.Float(), nullable=False),
        sa.Column('actual_dividend', sa.Float(), nullable=False),
        sa.Column('dividend_date', sa.Date(), nullable=False),
        
        # 分红状态
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('payment_method', sa.String(50)),
        
        # 备注信息
        sa.Column('remarks', sa.Text()),
        sa.Column('operator_name', sa.String(100)),
        
        # 快照信息
        sa.Column('snapshot_total_profit', sa.Float()),
        sa.Column('snapshot_profit_ratio', sa.Float()),
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.current_timestamp()),
    )
    
    # 创建分红汇总表
    op.create_table(
        'dividend_summary',
        sa.Column('id', sa.Integer(), primary_key=True),
        
        # 股东信息
        sa.Column('shareholder_name', sa.String(100), nullable=False, unique=True),
        
        # 汇总信息
        sa.Column('total_calculated', sa.Float(), default=0),
        sa.Column('total_paid', sa.Float(), default=0),
        sa.Column('total_pending', sa.Float(), default=0),
        
        # 统计信息
        sa.Column('record_count', sa.Integer(), default=0),
        sa.Column('last_dividend_date', sa.Date()),
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.current_timestamp()),
    )
    
    # 创建索引
    op.create_index('idx_dividend_date', 'dividend_record', ['dividend_date'])
    op.create_index('idx_dividend_period', 'dividend_record', ['period_year', 'period_month'])
    op.create_index('idx_dividend_shareholder', 'dividend_record', ['shareholder_name'])
    op.create_index('idx_dividend_status', 'dividend_record', ['status'])
    
    # 创建唯一约束
    op.create_unique_constraint(
        'uq_dividend_record',
        'dividend_record',
        ['shareholder_name', 'period_year', 'period_month', 'dividend_date']
    )
    
    # 初始化股东汇总记录
    op.execute("""
        INSERT INTO dividend_summary (shareholder_name) 
        VALUES ('股东A'), ('股东B')
    """)


def downgrade():
    """删除分红记录相关表"""
    
    # 删除索引
    op.drop_index('idx_dividend_date', 'dividend_record')
    op.drop_index('idx_dividend_period', 'dividend_record')
    op.drop_index('idx_dividend_shareholder', 'dividend_record')
    op.drop_index('idx_dividend_status', 'dividend_record')
    
    # 删除约束
    op.drop_constraint('uq_dividend_record', 'dividend_record', type_='unique')
    
    # 删除表
    op.drop_table('dividend_summary')
    op.drop_table('dividend_record')