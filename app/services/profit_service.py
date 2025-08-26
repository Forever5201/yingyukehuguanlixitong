"""
利润计算服务 - 集中管理所有利润相关的业务逻辑

功能：
1. 课程利润计算（支持退费）
2. 股东利润分配计算
3. 员工提成计算
4. 利润报表生成
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, func
from ..models import db, Course, Customer, Config, CourseRefund, Employee, CommissionConfig
import logging

logger = logging.getLogger(__name__)


class ProfitService:
    """利润计算服务类"""
    
    @staticmethod
    def safe_float(value, default=0):
        """安全转换为浮点数"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value, default=0):
        """安全转换为整数"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def calculate_course_profit(cls, course: Course, include_refund: bool = True) -> Dict:
        """
        计算单个课程的利润
        
        Args:
            course: 课程对象
            include_refund: 是否包含退费计算
            
        Returns:
            包含收入、成本、利润等信息的字典
        """
        try:
            # 基础计算
            sessions = cls.safe_int(course.sessions, 0)
            price = cls.safe_float(course.price, 0)
            original_revenue = sessions * price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝':
                fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
                fee = original_revenue * fee_rate
            
            # 原始成本
            cost = cls.safe_float(course.cost, 0)
            
            # 处理退费
            actual_revenue = original_revenue
            actual_cost = cost
            refund_info = None
            
            if include_refund and not course.is_trial:
                refund_result = cls._calculate_refund_impact(course, sessions, original_revenue, cost)
                actual_revenue = refund_result['actual_revenue']
                actual_cost = refund_result['actual_cost']
                refund_info = refund_result['refund_info']
            
            # 计算利润
            profit = actual_revenue - actual_cost - fee
            
            return {
                'original_revenue': original_revenue,
                'actual_revenue': actual_revenue,
                'cost': actual_cost,
                'fee': fee,
                'profit': profit,
                'has_refund': refund_info is not None,
                'refund_info': refund_info
            }
            
        except Exception as e:
            logger.error(f"计算课程利润失败 (course_id={course.id}): {str(e)}")
            return {
                'original_revenue': 0,
                'actual_revenue': 0,
                'cost': 0,
                'fee': 0,
                'profit': 0,
                'has_refund': False,
                'refund_info': None
            }
    
    @classmethod
    def _calculate_refund_impact(cls, course: Course, sessions: int, revenue: float, cost: float) -> Dict:
        """计算退费对利润的影响"""
        refunds = CourseRefund.query.filter_by(
            course_id=course.id,
            status='completed'
        ).all()
        
        if not refunds:
            return {
                'actual_revenue': revenue,
                'actual_cost': cost,
                'refund_info': None
            }
        
        total_refunded_sessions = sum(r.refund_sessions for r in refunds)
        total_refunded_amount = sum(r.refund_amount for r in refunds)
        
        # 实际收入 = 原始收入 - 退费金额
        actual_revenue = revenue - total_refunded_amount
        
        # 成本按比例调整
        actual_sessions = sessions - total_refunded_sessions
        if sessions > 0:
            # 分离固定成本和变动成本
            other_cost = cls.safe_float(course.other_cost, 0)  # 固定成本
            course_cost = cost - other_cost  # 变动成本
            
            # 变动成本按比例，固定成本不变
            actual_cost = (course_cost * actual_sessions / sessions) + other_cost
        else:
            actual_cost = cost  # 全部退费时保留成本
        
        return {
            'actual_revenue': actual_revenue,
            'actual_cost': actual_cost,
            'refund_info': {
                'sessions': total_refunded_sessions,
                'amount': total_refunded_amount,
                'count': len(refunds)
            }
        }
    
    @classmethod
    def calculate_shareholder_distribution(cls, profit: float, is_renewal: bool = False) -> Dict:
        """
        计算股东利润分配（统一分配比例，不区分课程类型）
        
        Args:
            profit: 利润金额
            is_renewal: 是否为续课（保留参数以兼容旧代码，但不再使用）
            
        Returns:
            股东分配信息
        """
        try:
            # 获取统一的分配比例配置
            config_a_key = 'shareholder_a_ratio'
            config_b_key = 'shareholder_b_ratio'
            default_a = 50
            default_b = 50
            
            # 查询配置
            configs = Config.query.filter(Config.key.in_([config_a_key, config_b_key])).all()
            config_dict = {c.key: cls.safe_float(c.value) for c in configs}
            
            ratio_a = config_dict.get(config_a_key, default_a) / 100
            ratio_b = config_dict.get(config_b_key, default_b) / 100
            
            # 确保比例和为1
            if ratio_a + ratio_b != 1:
                ratio_b = 1 - ratio_a
            
            return {
                'shareholder_a': profit * ratio_a,
                'shareholder_b': profit * ratio_b,
                'ratio_a': ratio_a * 100,
                'ratio_b': ratio_b * 100
            }
            
        except Exception as e:
            logger.error(f"计算股东分配失败: {str(e)}")
            # 使用默认分配
            return {
                'shareholder_a': profit * 0.5,
                'shareholder_b': profit * 0.5,
                'ratio_a': 50,
                'ratio_b': 50
            }
    
    @classmethod
    def calculate_employee_commission(cls, employee_id: int, courses: List[Course]) -> Dict:
        """
        计算员工提成
        
        Args:
            employee_id: 员工ID
            courses: 员工负责的课程列表
            
        Returns:
            提成信息
        """
        try:
            # 获取员工提成配置
            commission_config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
            if not commission_config:
                return {
                    'trial_commission': 0,
                    'new_commission': 0,
                    'renewal_commission': 0,
                    'total_commission': 0,
                    'base_salary': 0
                }
            
            trial_commission = 0
            new_commission = 0
            renewal_commission = 0
            
            for course in courses:
                profit_info = cls.calculate_course_profit(course)
                
                if commission_config.commission_type == 'profit':
                    base_amount = profit_info['profit']
                else:  # sales
                    base_amount = profit_info['actual_revenue']
                
                if course.is_trial:
                    trial_commission += base_amount * (commission_config.trial_rate / 100)
                elif course.is_renewal:
                    renewal_commission += base_amount * (commission_config.renewal_rate / 100)
                else:
                    new_commission += base_amount * (commission_config.new_course_rate / 100)
            
            return {
                'trial_commission': trial_commission,
                'new_commission': new_commission,
                'renewal_commission': renewal_commission,
                'total_commission': trial_commission + new_commission + renewal_commission,
                'base_salary': cls.safe_float(commission_config.base_salary)
            }
            
        except Exception as e:
            logger.error(f"计算员工提成失败 (employee_id={employee_id}): {str(e)}")
            return {
                'trial_commission': 0,
                'new_commission': 0,
                'renewal_commission': 0,
                'total_commission': 0,
                'base_salary': 0
            }
    
    @classmethod
    def generate_profit_report(cls, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> Dict:
        """
        生成利润报表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            利润报表数据
        """
        try:
            # 构建查询
            query = db.session.query(Course, Customer).join(
                Customer, Course.customer_id == Customer.id
            )
            
            if start_date:
                query = query.filter(Course.created_at >= start_date)
            if end_date:
                query = query.filter(Course.created_at <= end_date)
            
            courses = query.all()
            
            # 统计数据
            total_revenue = 0
            total_cost = 0
            total_fee = 0  # 新增总手续费
            total_profit = 0
            trial_profit = 0
            new_course_profit = 0
            renewal_profit = 0
            
            for course, customer in courses:
                profit_info = cls.calculate_course_profit(course)
                
                total_revenue += profit_info['actual_revenue']
                total_cost += profit_info['cost']
                total_fee += profit_info['fee']  # 单独统计手续费
                total_profit += profit_info['profit']
                
                if course.is_trial:
                    trial_profit += profit_info['profit']
                elif course.is_renewal:
                    renewal_profit += profit_info['profit']
                else:
                    new_course_profit += profit_info['profit']
            
            # 计算股东分配
            new_distribution = cls.calculate_shareholder_distribution(new_course_profit, False)
            renewal_distribution = cls.calculate_shareholder_distribution(renewal_profit, True)
            
            return {
                'summary': {
                    'total_revenue': total_revenue,
                    'total_cost': total_cost + total_fee,  # 总成本包含手续费
                    'total_fee': total_fee,  # 单独返回手续费
                    'total_profit': total_profit,
                    'course_count': len(courses)
                },
                'profit_by_type': {
                    'trial': trial_profit,
                    'new_course': new_course_profit,
                    'renewal': renewal_profit
                },
                'shareholder_distribution': {
                    'new_course': new_distribution,
                    'renewal': renewal_distribution,
                    'total': {
                        'shareholder_a': new_distribution['shareholder_a'] + renewal_distribution['shareholder_a'],
                        'shareholder_b': new_distribution['shareholder_b'] + renewal_distribution['shareholder_b']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"生成利润报表失败: {str(e)}")
            raise