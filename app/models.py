from . import db
from datetime import datetime

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    grade = db.Column(db.String(50))
    region = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    source = db.Column(db.String(50)) # 渠道来源
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    customers = db.relationship('Customer', backref='employee', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='courses', lazy=True)
    
    # 试听课信息
    is_trial = db.Column(db.Boolean, default=False)
    trial_price = db.Column(db.Float)  # 试听课售价
    source = db.Column(db.String(50))  # 渠道来源（淘宝、视频号、抖音、小红书）
    
    # 正课信息
    course_type = db.Column(db.String(50))  # 课程类型（单词课、语法课、阅读课、拼读课）
    sessions = db.Column(db.Integer)  # 购买节数
    price = db.Column(db.Float)  # 课程售价
    cost = db.Column(db.Float)  # 课程成本
    gift_sessions = db.Column(db.Integer, default=0)  # 赠课节数
    other_cost = db.Column(db.Float, default=0)  # 其他成本
    
    # 转化信息
    converted_from_trial = db.Column(db.Integer, db.ForeignKey('course.id'))  # 从哪个试听课转化而来
    converted_to_course = db.Column(db.Integer, db.ForeignKey('course.id'))  # 转化为哪个正课
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaobaoOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    level = db.Column(db.String(50))
    amount = db.Column(db.Float)
    commission = db.Column(db.Float)  # 佣金金额
    taobao_fee = db.Column(db.Float, default=0)  # 淘宝手续费
    evaluated = db.Column(db.Boolean, default=False)
    order_time = db.Column(db.DateTime)
    settled = db.Column(db.Boolean, default=False)  # 结算状态
    settled_at = db.Column(db.DateTime)  # 结算时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)