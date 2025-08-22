"""
课程服务层 - 统一的课程业务逻辑处理

根据软件开发规范，将分散的业务逻辑集中到服务层，
实现单一职责原则和数据一致性保证。
"""

from typing import List, Dict, Optional, Tuple
import logging
from flask import current_app
from .. import db
from ..models import Course, Customer, Config
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

class CourseService:
    """课程服务类 - 统一的课程业务逻辑处理"""
    
    @staticmethod
    def get_courses(course_type: Optional[str] = None,
                   status: Optional[str] = None,
                   include_customer: bool = True) -> List[Tuple]:
        """
        统一的课程查询接口
        
        Args:
            course_type: 课程类型 ('trial', 'formal', None表示所有类型)
            status: 课程状态
            include_customer: 是否包含客户信息
            
        Returns:
            课程列表，格式为 [(Course, Customer)] 或 [Course]
        """
        try:
            # 总是查询Course和Customer的连接，确保数据完整性
            query = db.session.query(Course, Customer).join(Customer, Course.customer_id == Customer.id)
            
            # 课程类型过滤
            if course_type == 'trial':
                query = query.filter(Course.is_trial == True)
            elif course_type == 'formal':
                query = query.filter(Course.is_trial == False)
            
            # 状态过滤
            if status:
                query = query.filter(Course.trial_status == status)
            
            # 添加排序，确保有created_at字段
            if hasattr(Course, 'created_at'):
                query = query.order_by(Course.created_at.desc())
            else:
                query = query.order_by(Course.id.desc())
            
            results = query.all()
            
            # 如果不需要customer信息，只返回Course对象
            if not include_customer:
                return [course for course, customer in results]
            
            return results
            
        except Exception as e:
            logger.error(f"查询课程失败: {str(e)}")
            # 返回空列表而不是抛出异常，让上层处理
            return []
    
    @staticmethod
    def calculate_performance(courses: List[Tuple], 
                            separate_by_type: bool = False) -> Dict:
        """
        统一的业绩计算逻辑
        
        Args:
            courses: 课程列表
            separate_by_type: 是否按类型分别计算
            
        Returns:
            业绩统计数据
        """
        try:
            # 获取手续费率配置
            taobao_fee_rate = CourseService._get_taobao_fee_rate()
            
            if separate_by_type:
                return CourseService._calculate_performance_by_type(courses, taobao_fee_rate)
            else:
                return CourseService._calculate_total_performance(courses, taobao_fee_rate)
                
        except Exception as e:
            logger.error(f"计算业绩失败: {str(e)}")
            raise
    
    @staticmethod
    def _get_taobao_fee_rate() -> float:
        """获取淘宝手续费率"""
        config = Config.query.filter_by(key='taobao_fee_rate').first()
        return float(config.value) / 100 if config else 0.006
    
    @staticmethod
    def _calculate_total_performance(courses: List[Tuple], fee_rate: float) -> Dict:
        """计算总体业绩"""
        total_revenue = 0
        total_cost = 0
        total_fees = 0
        trial_count = 0
        formal_count = 0
        
        for item in courses:
            # 正确处理SQLAlchemy Row对象
            if hasattr(item, '_fields') and len(item) >= 1:
                course = item[0]
            elif isinstance(item, (tuple, list)) and len(item) >= 1:
                course = item[0]
            else:
                course = item
            
            # 收入计算
            if course.is_trial:
                revenue = float(course.trial_price or 0)
                trial_count += 1
            else:
                revenue = float(course.price or 0)
                formal_count += 1
            
            total_revenue += revenue
            
            # 成本计算
            cost = float(course.cost or 0)
            if not course.is_trial:
                cost += float(course.other_cost or 0)
            total_cost += cost
            
            # 手续费计算
            if course.payment_channel == '淘宝' or course.source == '淘宝':
                total_fees += revenue * fee_rate
        
        return {
            'total_count': len(courses),
            'trial_count': trial_count,
            'formal_count': formal_count,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_fees': total_fees,
            'total_profit': total_revenue - total_cost
        }
    
    @staticmethod
    def _calculate_performance_by_type(courses: List[Tuple], fee_rate: float) -> Dict:
        """按类型分别计算业绩"""
        trial_courses = []
        formal_courses = []
        
        for item in courses:
            # 正确处理SQLAlchemy Row对象
            if hasattr(item, '_fields') and len(item) >= 1:
                course = item[0]
            elif isinstance(item, (tuple, list)) and len(item) >= 1:
                course = item[0]
            else:
                course = item
                
            if course.is_trial:
                trial_courses.append(item)
            else:
                formal_courses.append(item)
        
        # 分别计算试听课和正式课的业绩
        trial_performance = CourseService._calculate_total_performance(trial_courses, fee_rate)
        formal_performance = CourseService._calculate_total_performance(formal_courses, fee_rate)
        
        # 直接计算总收入和总成本
        total_revenue = trial_performance['total_revenue'] + formal_performance['total_revenue']
        total_cost = trial_performance['total_cost'] + formal_performance['total_cost']
        
        # 更新试听课和正式课的利润计算（不扣除手续费）
        trial_performance['total_profit'] = trial_performance['total_revenue'] - trial_performance['total_cost']
        formal_performance['total_profit'] = formal_performance['total_revenue'] - formal_performance['total_cost']
        
        return {
            'trial': trial_performance,
            'formal': formal_performance,
            'total': {
                'total_count': len(courses),
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_fees': trial_performance['total_fees'] + formal_performance['total_fees'],
                'total_profit': total_revenue - total_cost
            }
        }
    
    @staticmethod
    def get_status_mapping() -> Dict[str, str]:
        """获取状态映射"""
        return {
            'registered': '已报名试听课',
            'not_registered': '未报名试听课',
            'refunded': '试听后退费',
            'converted': '试听后转正课',
            'no_action': '试听后无操作'
        }
    
    @staticmethod
    def format_course_data(courses: List[Tuple], 
                          include_customer_details: bool = False) -> List[Dict]:
        """
        格式化课程数据
        
        Args:
            courses: 课程列表
            include_customer_details: 是否包含详细客户信息
            
        Returns:
            格式化后的课程数据列表
        """
        try:
            status_mapping = CourseService.get_status_mapping()
            taobao_fee_rate = CourseService._get_taobao_fee_rate()
            formatted_courses = []
            
            for item in courses:
                # SQLAlchemy返回Row对象，需要正确解包
                try:
                    if hasattr(item, '_fields') and len(item) >= 2:
                        # SQLAlchemy Row对象
                        course, customer = item[0], item[1]
                    elif isinstance(item, (tuple, list)) and len(item) >= 2:
                        # 普通tuple或list
                        course, customer = item[0], item[1]
                    else:
                        logger.warning(f"课程数据格式异常: {type(item)}")
                        continue
                except Exception as e:
                    logger.warning(f"解包课程数据失败: {str(e)}")
                    continue
                
                # 基础数据
                course_data = {
                    'id': course.id,
                    'customer_name': customer.name,
                    'customer_phone': customer.phone,
                    'course_type': '试听课' if course.is_trial else '正式课'
                }
                
                # 安全地添加创建时间
                if hasattr(course, 'created_at') and course.created_at:
                    course_data['created_at'] = course.created_at.isoformat()
                else:
                    course_data['created_at'] = None
                
                # 价格和状态
                if course.is_trial:
                    course_data.update({
                        'price': float(course.trial_price or 0),
                        'status': status_mapping.get(course.trial_status or 'registered', 
                                                   course.trial_status or 'registered'),
                        'status_key': course.trial_status or 'registered'
                    })
                else:
                    price = float(course.price or 0)
                    sessions = course.sessions or 1
                    course_data.update({
                        'price': price,
                        'sessions': sessions,
                        'price_per_session': price / sessions if sessions > 0 else 0
                    })
                
                # 详细客户信息
                if include_customer_details:
                    course_data.update({
                        'customer_gender': customer.gender,
                        'customer_grade': customer.grade,
                        'customer_region': customer.region,
                        'experience_status': '有经验' if customer.has_tutoring_experience else '无经验'
                    })
                
                # 手续费计算
                revenue = course_data['price']
                if course.payment_channel == '淘宝' or course.source == '淘宝':
                    course_data['fees'] = revenue * taobao_fee_rate
                else:
                    course_data['fees'] = 0
                
                # 来源信息
                course_data['source'] = course.source or course.payment_channel or '未知'
                
                formatted_courses.append(course_data)
            
            return formatted_courses
            
        except Exception as e:
            logger.error(f"格式化课程数据失败: {str(e)}")
            raise