"""
课程服务适配器 - 现有逻辑和新架构之间的桥梁

这个适配器允许我们逐步迁移功能，而不影响现有系统的运行。
通过包装现有的数据库操作，添加统一的错误处理和事务管理。
"""

import logging
from typing import List, Dict, Optional, Any
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .. import db
from ..models import Course, Customer, Employee, Config, CommissionConfig
from .course_service import CourseService

logger = logging.getLogger(__name__)

class ServiceException(Exception):
    """服务层异常基类"""
    pass

class ValidationException(ServiceException):
    """数据验证异常"""
    pass

class BusinessLogicException(ServiceException):
    """业务逻辑异常"""
    pass

@contextmanager
def db_transaction():
    """数据库事务上下文管理器"""
    try:
        yield
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"数据库事务错误: {str(e)}")
        raise ServiceException(f"数据库操作失败: {str(e)}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"未知错误: {str(e)}")
        raise

class CourseServiceAdapter:
    """
    课程服务适配器
    
    功能：
    1. 包装现有的数据库操作逻辑
    2. 添加统一的错误处理
    3. 提供事务保护
    4. 逐步迁移到新的服务层架构
    """
    
    @staticmethod
    def get_trial_courses(
        status: Optional[str] = None,
        employee_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取试听课列表（包装现有逻辑）
        
        Args:
            status: 试听课状态过滤
            employee_id: 员工ID过滤
            start_date: 开始日期过滤
            end_date: 结束日期过滤
            
        Returns:
            包含课程列表和统计信息的字典
        """
        try:
            # 构建查询
            query = db.session.query(Course, Customer)\
                .join(Customer, Course.customer_id == Customer.id)\
                .filter(Course.is_trial == True)
            
            # 应用过滤条件
            if status:
                query = query.filter(Course.trial_status == status)
            
            if employee_id:
                query = query.filter(Course.assigned_employee_id == employee_id)
            
            if start_date:
                query = query.filter(Course.created_at >= start_date)
            
            if end_date:
                query = query.filter(Course.created_at <= end_date)
            
            # 执行查询
            courses_with_customers = query.order_by(Course.created_at.desc()).all()
            
            # 获取配置
            configs = CourseServiceAdapter._get_configs(['trial_cost', 'taobao_fee_rate'])
            trial_cost = float(configs.get('trial_cost', 0))
            fee_rate = float(configs.get('taobao_fee_rate', 0)) / 100
            
            # 格式化数据
            formatted_courses = []
            total_revenue = 0
            total_cost = 0
            status_counts = {}
            
            for course, customer in courses_with_customers:
                # 计算单个课程数据
                revenue = float(course.trial_price or 0)
                cost = float(course.cost or trial_cost)
                fee = revenue * fee_rate if course.source == '淘宝' else 0
                profit = revenue - cost - fee
                
                total_revenue += revenue
                total_cost += cost
                
                # 统计状态
                status = course.trial_status or 'registered'
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # 获取员工信息
                employee = Employee.query.get(course.assigned_employee_id) if course.assigned_employee_id else None
                
                formatted_courses.append({
                    'id': course.id,
                    'customer_id': customer.id,
                    'customer_name': customer.name,
                    'customer_phone': customer.phone,
                    'customer_grade': customer.grade,
                    'customer_region': customer.region,
                    'trial_price': revenue,
                    'source': course.source,
                    'trial_status': status,
                    'cost': cost,
                    'fee': fee,
                    'profit': profit,
                    'assigned_employee_id': course.assigned_employee_id,
                    'assigned_employee_name': employee.name if employee else None,
                    'created_at': course.created_at.isoformat() if course.created_at else None
                })
            
            # 返回结果
            return {
                'success': True,
                'data': {
                    'courses': formatted_courses,
                    'statistics': {
                        'total_count': len(formatted_courses),
                        'total_revenue': total_revenue,
                        'total_cost': total_cost,
                        'total_profit': total_revenue - total_cost,
                        'status_distribution': status_counts
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"获取试听课列表失败: {str(e)}")
            raise ServiceException(f"获取试听课列表失败: {str(e)}")
    
    @staticmethod
    def create_trial_course(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建试听课（包装现有逻辑，添加验证和事务）
        """
        try:
            with db_transaction():
                # 数据验证
                CourseServiceAdapter._validate_trial_course_data(data)
                
                # 处理客户信息
                customer_id = data.get('customer_id')
                if not customer_id:
                    # 创建新客户
                    customer = CourseServiceAdapter._create_customer_from_data(data)
                    customer_id = customer.id
                else:
                    # 验证客户存在
                    customer = Customer.query.get(customer_id)
                    if not customer:
                        raise ValidationException("客户不存在")
                
                # 检查是否已有试听课
                existing_trial = Course.query.filter_by(
                    customer_id=customer_id,
                    is_trial=True
                ).first()
                
                if existing_trial:
                    raise BusinessLogicException(f"学员 {customer.name} 已有试听课记录")
                
                # 获取成本配置
                trial_cost_config = Config.query.filter_by(key='trial_cost').first()
                trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
                
                # 创建试听课
                new_trial = Course(
                    name='试听课',
                    customer_id=customer_id,
                    is_trial=True,
                    trial_price=float(data['trial_price']),
                    source=data['source'],
                    cost=trial_cost,
                    trial_status='registered',
                    assigned_employee_id=data.get('assigned_employee_id')
                )
                
                db.session.add(new_trial)
                db.session.flush()
                
                return {
                    'success': True,
                    'data': {
                        'course_id': new_trial.id,
                        'customer_id': customer_id,
                        'message': '试听课创建成功'
                    }
                }
                
        except (ValidationException, BusinessLogicException) as e:
            raise
        except Exception as e:
            logger.error(f"创建试听课失败: {str(e)}")
            raise ServiceException(f"创建试听课失败: {str(e)}")
    
    @staticmethod
    def _validate_trial_course_data(data: Dict[str, Any]) -> None:
        """验证试听课数据"""
        # 必填字段验证
        if not data.get('trial_price'):
            raise ValidationException("试听价格不能为空")
        
        if not data.get('source'):
            raise ValidationException("渠道来源不能为空")
        
        # 如果没有customer_id，需要验证新客户信息
        if not data.get('customer_id'):
            if not data.get('customer_phone'):
                raise ValidationException("客户电话不能为空")
    
    @staticmethod
    def _create_customer_from_data(data: Dict[str, Any]) -> Customer:
        """从数据创建新客户"""
        phone = data['customer_phone'].strip()
        name = data.get('customer_name', '').strip()
        
        # 如果姓名为空，使用手机号后4位
        if not name:
            name = f"学员{phone[-4:]}"
        
        # 检查手机号是否已存在
        existing = Customer.query.filter_by(phone=phone).first()
        if existing:
            raise BusinessLogicException(f"手机号 {phone} 已存在")
        
        # 创建客户
        customer = Customer(
            name=name,
            phone=phone,
            gender=data.get('customer_gender'),
            grade=data.get('customer_grade'),
            region=data.get('customer_region')
        )
        
        db.session.add(customer)
        db.session.flush()
        
        return customer
    
    @staticmethod
    def _get_configs(keys: List[str]) -> Dict[str, str]:
        """批量获取配置"""
        configs = Config.query.filter(Config.key.in_(keys)).all()
        return {c.key: c.value for c in configs}
    
    @staticmethod
    def convert_trial_to_formal(
        trial_id: int,
        formal_course_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        试听课转正课（包装现有逻辑）
        
        这是一个复杂的业务流程，需要特别注意事务一致性
        """
        try:
            with db_transaction():
                # 获取试听课
                trial_course = Course.query.filter_by(
                    id=trial_id,
                    is_trial=True
                ).first()
                
                if not trial_course:
                    raise ValidationException("试听课不存在")
                
                if trial_course.converted_to_course:
                    raise BusinessLogicException("该试听课已经转化为正课")
                
                if not trial_course.assigned_employee_id:
                    raise BusinessLogicException("试听课未分配员工，无法转正")
                
                # 创建正课
                formal_course = Course(
                    customer_id=trial_course.customer_id,
                    course_type=formal_course_data['course_type'],
                    sessions=int(formal_course_data['sessions']),
                    gift_sessions=int(formal_course_data.get('gift_sessions', 0)),
                    price=float(formal_course_data['price']),
                    payment_channel=formal_course_data['payment_channel'],
                    assigned_employee_id=trial_course.assigned_employee_id,
                    converted_from_trial=trial_id,
                    is_trial=False,
                    cost=float(formal_course_data.get('cost', 0)),
                    other_cost=float(formal_course_data.get('other_cost', 0))
                )
                
                db.session.add(formal_course)
                db.session.flush()
                
                # 更新试听课状态
                trial_course.converted_to_course = formal_course.id
                trial_course.trial_status = 'converted'
                
                return {
                    'success': True,
                    'data': {
                        'formal_course_id': formal_course.id,
                        'message': '试听课转正成功'
                    }
                }
                
        except (ValidationException, BusinessLogicException) as e:
            raise
        except Exception as e:
            logger.error(f"试听课转正失败: {str(e)}")
            raise ServiceException(f"试听课转正失败: {str(e)}")