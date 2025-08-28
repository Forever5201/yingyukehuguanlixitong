from . import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))  # 联系电话
    email = db.Column(db.String(100))  # 邮箱地址

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    grade = db.Column(db.String(50))
    region = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True, nullable=False)
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