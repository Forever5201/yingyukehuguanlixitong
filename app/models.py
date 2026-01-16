from . import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Index

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))  # 联系电话或微信号
    email = db.Column(db.String(100))  # 邮箱地址
    salary = db.Column(db.Float, default=0)  # 月薪

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    grade = db.Column(db.String(50))
    region = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True, nullable=False)  # 联系电话或微信号
    source = db.Column(db.String(50)) # 渠道来源
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    has_tutoring_experience = db.Column(db.String(10)) # 是否参加过英语课外辅导
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    employee = db.relationship('Employee', backref='customers', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 课程信息
    name = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    is_trial = db.Column(db.Boolean, default=False)
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # 分配的员工ID
    customer = db.relationship('Customer', backref='courses', lazy=True)
    
    # 试听课信息
    trial_price = db.Column(db.Float)  # 试听价格
    source = db.Column(db.String(50))  # 渠道来源（淘宝、视频号、抖音、小红书）
    trial_status = db.Column(db.String(20), default='registered')  # 试听课状态
    refund_amount = db.Column(db.Float, default=0)  # 退费金额
    refund_fee = db.Column(db.Float, default=0)  # 退费手续费
    refund_channel = db.Column(db.String(50))  # 退款渠道（微信、淘宝、支付宝等）
    custom_trial_cost = db.Column(db.Float)  # 自定义试听课成本
    
    # 正课信息
    course_type = db.Column(db.String(100))  # 课程类型（如：数学、英语）
    sessions = db.Column(db.Integer)  # 购买节数
    price = db.Column(db.Float)  # 单节售价
    gift_sessions = db.Column(db.Integer, default=0)  # 赠送节数
    other_cost = db.Column(db.Float, default=0)  # 其他成本
    cost = db.Column(db.Float, default=0)  # 基础成本（课时成本 + 其他成本）
    payment_channel = db.Column(db.String(50))  # 支付渠道（如：淘宝、微信）
    is_renewal = db.Column(db.Boolean, default=False)  # 是否为续课
    renewal_from_course_id = db.Column(db.Integer, db.ForeignKey('course.id'))  # 续课来源课程ID
    
    # 转化信息
    converted_from_trial = db.Column(db.Integer, db.ForeignKey('course.id'))  # 从哪个试听课转化而来
    converted_to_course = db.Column(db.Integer, db.ForeignKey('course.id'))  # 转化为哪个正课
    
    # 快照字段
    snapshot_course_cost = db.Column(db.Float, default=0)  # 转正时的单节成本快照
    snapshot_fee_rate = db.Column(db.Float, default=0)  # 转正时的手续费率快照(小数)
    meta = db.Column(db.Text)  # 扩展信息JSON
    custom_course_cost = db.Column(db.Float)  # 自定义正课单节成本
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    assigned_employee = db.relationship('Employee', backref='assigned_courses', foreign_keys=[assigned_employee_id])

class TaobaoOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    level = db.Column(db.String(50))
    # 刷单商品名称（来自系统配置，可为空以兼容历史数据）
    product_name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    commission = db.Column(db.Float)  # 佣金金额
    taobao_fee = db.Column(db.Float, default=0)  # 淘宝手续费
    evaluated = db.Column(db.Boolean, default=False)
    order_time = db.Column(db.DateTime)
    settled = db.Column(db.Boolean, default=False)  # 结算状态
    settled_at = db.Column(db.DateTime)  # 结算时间
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

class CommissionConfig(db.Model):
    """员工提成配置表"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), unique=True)
    commission_type = db.Column(db.String(20), default='profit')  # profit或sales
    trial_rate = db.Column(db.Float, default=0)  # 试听课提成比例
    new_course_rate = db.Column(db.Float, default=0)  # 新课提成比例
    renewal_rate = db.Column(db.Float, default=0)  # 续课提成比例
    base_salary = db.Column(db.Float, default=0)  # 底薪
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    employee = db.relationship('Employee', backref='commission_config', uselist=False)

class CourseRefund(db.Model):
    """课程退费记录表"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    refund_sessions = db.Column(db.Integer, nullable=False)  # 退费节数
    refund_amount = db.Column(db.Float, nullable=False)  # 退费金额
    refund_reason = db.Column(db.String(200))  # 退费原因
    refund_channel = db.Column(db.String(50))  # 退费渠道
    refund_fee = db.Column(db.Float, default=0)  # 退费手续费
    refund_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 退费日期
    status = db.Column(db.String(20), default='completed')  # 状态：completed/cancelled
    operator_name = db.Column(db.String(100))  # 操作员姓名
    remark = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    course = db.relationship('Course', backref='refunds', lazy=True)

class OperationalCost(db.Model):
    """运营成本记录表"""
    id = db.Column(db.Integer, primary_key=True)
    
    # 成本类型
    cost_type = db.Column(db.String(50), nullable=False)  # 房租、水电、设备、营销等
    cost_name = db.Column(db.String(100), nullable=False)  # 具体成本名称
    amount = db.Column(db.Float, nullable=False)  # 成本金额
    
    # 时间信息
    cost_date = db.Column(db.Date, nullable=False)  # 成本发生日期
    billing_period = db.Column(db.String(20))  # 计费周期（月/季/年）
    
    # 成本分配
    allocation_method = db.Column(db.String(20), default='proportional')  # 分配方式：proportional/equal
    allocated_to_courses = db.Column(db.Boolean, default=True)  # 是否分配到课程
    
    # 备注信息
    description = db.Column(db.Text)  # 详细描述
    invoice_number = db.Column(db.String(50))  # 发票号
    supplier = db.Column(db.String(100))  # 供应商
    payment_recipient = db.Column(db.String(100))  # 支付对象（钱支付给谁）
    
    # 状态
    status = db.Column(db.String(20), default='active')  # 状态：active/archived
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<OperationalCost {self.cost_type}:{self.cost_name} - ¥{self.amount}>'


class User(db.Model, UserMixin):
    """用户认证模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(20), default='admin')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class DividendRecord(db.Model):
    """股东分红记录表"""
    __tablename__ = 'dividend_record'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    shareholder_name = db.Column(db.String(100), nullable=False)  # 股东名称
    period_year = db.Column(db.Integer, nullable=False)           # 分红年份
    period_month = db.Column(db.Integer, nullable=False)          # 分红月份
    
    # 分红金额信息
    calculated_profit = db.Column(db.Float, nullable=False)       # 系统计算应分利润
    actual_dividend = db.Column(db.Float, nullable=False)         # 实际分红金额
    dividend_date = db.Column(db.Date, nullable=False)            # 分红日期
    
    # 分红状态
    status = db.Column(db.String(20), default='pending')          # pending/paid/cancelled
    payment_method = db.Column(db.String(50))                     # 支付方式
    
    # 备注信息
    remarks = db.Column(db.Text)                                  # 分红备注
    operator_name = db.Column(db.String(100))                     # 操作员
    
    # 快照信息（记录分红时的系统状态）
    snapshot_total_profit = db.Column(db.Float)                   # 当期总利润快照
    snapshot_profit_ratio = db.Column(db.Float)                   # 分红比例快照
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 创建复合唯一约束
    __table_args__ = (
        db.UniqueConstraint('shareholder_name', 'period_year', 'period_month', 'dividend_date', 
                           name='uq_dividend_record'),
        Index('idx_dividend_date', 'dividend_date'),
        Index('idx_dividend_period', 'period_year', 'period_month'),
        Index('idx_dividend_shareholder', 'shareholder_name'),
        Index('idx_dividend_status', 'status'),
    )
    
    def __repr__(self):
        return f'<DividendRecord {self.shareholder_name} {self.period_year}-{self.period_month:02d} ¥{self.actual_dividend}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'shareholder_name': self.shareholder_name,
            'period_year': self.period_year,
            'period_month': self.period_month,
            'calculated_profit': self.calculated_profit,
            'actual_dividend': self.actual_dividend,
            'dividend_date': self.dividend_date.isoformat() if self.dividend_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'remarks': self.remarks,
            'operator_name': self.operator_name,
            'snapshot_total_profit': self.snapshot_total_profit,
            'snapshot_profit_ratio': self.snapshot_profit_ratio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalaryPayment(db.Model):
    """员工工资支付记录表"""
    __tablename__ = 'salary_payment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    payment_month = db.Column(db.String(7), nullable=False)  # 格式: 2025-09
    
    # 工资组成
    base_salary = db.Column(db.Float, default=0)        # 基本工资
    commission_amount = db.Column(db.Float, default=0)  # 提成金额
    bonus = db.Column(db.Float, default=0)              # 奖金
    deduction = db.Column(db.Float, default=0)          # 扣款
    total_amount = db.Column(db.Float, nullable=False)  # 实发金额
    
    # 发放信息
    payment_date = db.Column(db.Date)                   # 发放日期
    payment_method = db.Column(db.String(50))           # 发放方式
    notes = db.Column(db.Text)                          # 备注
    
    # 状态
    status = db.Column(db.String(20), default='pending')  # pending/paid/cancelled
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    employee = db.relationship('Employee', backref='salary_payments', lazy=True)
    
    # 索引和约束
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'payment_month', name='uq_salary_payment'),
        Index('idx_salary_payment_employee', 'employee_id'),
        Index('idx_salary_payment_month', 'payment_month'),
        Index('idx_salary_payment_status', 'status'),
    )
    
    def __repr__(self):
        return f'<SalaryPayment {self.employee.name if self.employee else "Unknown"} {self.payment_month} ￥{self.total_amount}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'payment_month': self.payment_month,
            'base_salary': self.base_salary,
            'commission_amount': self.commission_amount,
            'bonus': self.bonus,
            'deduction': self.deduction,
            'total_amount': self.total_amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DividendSummary(db.Model):
    """股东分红汇总表"""
    __tablename__ = 'dividend_summary'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 股东信息
    shareholder_name = db.Column(db.String(100), nullable=False, unique=True)
    
    # 汇总信息
    total_calculated = db.Column(db.Float, default=0)              # 累计应分利润
    total_paid = db.Column(db.Float, default=0)                    # 累计已分红
    total_pending = db.Column(db.Float, default=0)                 # 累计待分红
    
    # 统计信息
    record_count = db.Column(db.Integer, default=0)                # 分红记录数
    last_dividend_date = db.Column(db.Date)                        # 最后分红日期
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<DividendSummary {self.shareholder_name} 已分红:¥{self.total_paid} 待分红:¥{self.total_pending}>'
    
    @property
    def unpaid_amount(self):
        """未分红金额"""
        return self.total_calculated - self.total_paid
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'shareholder_name': self.shareholder_name,
            'total_calculated': self.total_calculated,
            'total_paid': self.total_paid,
            'total_pending': self.total_pending,
            'unpaid_amount': self.unpaid_amount,
            'record_count': self.record_count,
            'last_dividend_date': self.last_dividend_date.isoformat() if self.last_dividend_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }