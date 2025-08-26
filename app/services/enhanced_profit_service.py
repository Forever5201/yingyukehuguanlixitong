"""
增强版利润计算服务 - 包含刷单成本和详细报表
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, func
from ..models import db, Course, Customer, Config, CourseRefund, Employee, CommissionConfig, TaobaoOrder
from .profit_service import ProfitService
import logging

logger = logging.getLogger(__name__)


class EnhancedProfitService(ProfitService):
    """增强版利润计算服务"""
    
    @classmethod
    def calculate_taobao_order_cost(cls, start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict:
        """
        计算刷单成本
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            刷单成本统计
        """
        try:
            query = TaobaoOrder.query
            
            if start_date:
                query = query.filter(TaobaoOrder.created_at >= start_date)
            if end_date:
                query = query.filter(TaobaoOrder.created_at <= end_date)
            
            orders = query.all()
            
            total_amount = 0  # 刷单总金额
            total_commission = 0  # 总佣金
            total_fee = 0  # 总手续费
            settled_amount = 0  # 已结算金额
            unsettled_amount = 0  # 未结算金额
            
            for order in orders:
                amount = cls.safe_float(order.amount)
                commission = cls.safe_float(order.commission)
                fee = cls.safe_float(order.taobao_fee)
                
                total_amount += amount
                total_commission += commission
                total_fee += fee
                
                if order.settled:
                    settled_amount += amount
                else:
                    unsettled_amount += amount
            
            return {
                'total_amount': total_amount,  # 刷单金额（会在收入和成本中抵消）
                'total_commission': total_commission,  # 佣金成本
                'total_fee': total_fee,  # 手续费成本
                'total_cost': total_commission + total_fee,  # 实际成本
                'settled_amount': settled_amount,
                'unsettled_amount': unsettled_amount,
                'order_count': len(orders)
            }
            
        except Exception as e:
            logger.error(f"计算刷单成本失败: {str(e)}")
            return {
                'total_amount': 0,
                'total_commission': 0,
                'total_fee': 0,
                'total_cost': 0,
                'settled_amount': 0,
                'unsettled_amount': 0,
                'order_count': 0
            }
    
    @classmethod
    def generate_comprehensive_profit_report(cls, start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None) -> Dict:
        """
        生成综合利润报表（包含刷单）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            综合利润报表数据
        """
        try:
            # 1. 获取基础利润报表
            base_report = cls.generate_profit_report(start_date, end_date)
            
            # 2. 计算刷单成本
            taobao_cost = cls.calculate_taobao_order_cost(start_date, end_date)
            
            # 3. 计算员工成本
            employee_cost = cls.calculate_employee_cost(start_date, end_date)
            
            # 4. 重新计算总收入和总成本
            # 总收入 = 课程收入 + 刷单金额
            total_revenue = base_report['summary']['total_revenue'] + taobao_cost['total_amount']
            
            # 5. 计算试听课收入和正课收入的详细分类
            revenue_detail = cls.calculate_revenue_detail(start_date, end_date)
            
            # 6. 总成本 = 课程成本（不含手续费） + 所有手续费 + 刷单金额 + 刷单佣金 + 刷单手续费 + 员工成本
            # 从base_report中减去已计算的手续费，避免重复
            course_cost_without_fee = base_report['summary']['total_cost'] - base_report.get('total_fee', 0)
            total_cost = (course_cost_without_fee +          # 课程成本（不含手续费）
                         revenue_detail['total_fee'] +        # 所有课程手续费
                         taobao_cost['total_amount'] +        # 刷单金额作为成本
                         taobao_cost['total_cost'] +          # 刷单佣金和手续费
                         employee_cost['total_cost'])          # 员工成本
            
            # 7. 计算净利润
            net_profit = total_revenue - total_cost
            
            # 7. 重新计算股东分配（基于净利润中的新课和续课部分）
            # 计算新课和续课的净利润比例
            new_course_ratio = base_report['profit_by_type']['new_course'] / base_report['summary']['total_profit'] if base_report['summary']['total_profit'] > 0 else 0.5
            renewal_ratio = base_report['profit_by_type']['renewal'] / base_report['summary']['total_profit'] if base_report['summary']['total_profit'] > 0 else 0.5
            
            # 扣除刷单成本后的可分配利润
            distributable_profit = net_profit
            new_course_net_profit = distributable_profit * new_course_ratio
            renewal_net_profit = distributable_profit * renewal_ratio
            
            # 计算股东分配
            new_distribution = cls.calculate_shareholder_distribution(new_course_net_profit, False)
            renewal_distribution = cls.calculate_shareholder_distribution(renewal_net_profit, True)
            
            return {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d') if start_date else '开始',
                    'end_date': end_date.strftime('%Y-%m-%d') if end_date else '至今'
                },
                'revenue': {
                    'trial_revenue': revenue_detail['trial_revenue'],
                    'new_course_revenue': revenue_detail['new_course_revenue'],
                    'renewal_revenue': revenue_detail['renewal_revenue'],
                    'course_revenue': base_report['summary']['total_revenue'],
                    'taobao_revenue': taobao_cost['total_amount'],  # 刷单金额计入收入
                    'total_revenue': total_revenue,
                    'refund_amount': revenue_detail['refund_amount']
                },
                'cost': {
                    'course_cost': course_cost_without_fee,  # 课程成本（不含手续费）
                    'total_fee': revenue_detail['total_fee'],  # 所有手续费总和
                    'taobao_order_amount': taobao_cost['total_amount'],  # 刷单金额计入成本
                    'taobao_commission': taobao_cost['total_commission'],
                    'taobao_fee': taobao_cost['total_fee'],
                    'employee_salary': employee_cost['total_salary'],
                    'employee_commission': employee_cost['total_commission'],
                    'total_cost': total_cost
                },
                'profit': {
                    'gross_profit': base_report['summary']['total_profit'],  # 毛利润
                    'net_profit': net_profit,  # 净利润
                    'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0  # 净利率
                },
                'shareholder_distribution': {
                    'new_course': {
                        'profit': new_course_net_profit,
                        'shareholder_a': new_distribution['shareholder_a'],
                        'shareholder_b': new_distribution['shareholder_b'],
                        'ratio_a': new_distribution['ratio_a'],
                        'ratio_b': new_distribution['ratio_b']
                    },
                    'renewal': {
                        'profit': renewal_net_profit,
                        'shareholder_a': renewal_distribution['shareholder_a'],
                        'shareholder_b': renewal_distribution['shareholder_b'],
                        'ratio_a': renewal_distribution['ratio_a'],
                        'ratio_b': renewal_distribution['ratio_b']
                    },
                    'total': {
                        'shareholder_a': new_distribution['shareholder_a'] + renewal_distribution['shareholder_a'],
                        'shareholder_b': new_distribution['shareholder_b'] + renewal_distribution['shareholder_b'],
                        'total_distributed': new_distribution['shareholder_a'] + renewal_distribution['shareholder_a'] + 
                                           new_distribution['shareholder_b'] + renewal_distribution['shareholder_b']
                    }
                },
                'statistics': {
                    'course_count': base_report['summary']['course_count'],
                    'taobao_order_count': taobao_cost['order_count'],
                    'employee_count': employee_cost['employee_count']
                }
            }
            
        except Exception as e:
            logger.error(f"生成综合利润报表失败: {str(e)}")
            raise
    
    @classmethod
    def calculate_employee_cost(cls, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """计算员工成本"""
        try:
            # 获取所有员工
            employees = Employee.query.all()
            
            total_salary = 0
            total_commission = 0
            
            for employee in employees:
                # 获取员工配置
                commission_config = CommissionConfig.query.filter_by(employee_id=employee.id).first()
                if commission_config:
                    # 基本工资（按月计算，这里简化处理）
                    total_salary += cls.safe_float(commission_config.base_salary, 0)
                
                # 计算该员工的提成
                courses = Course.query.filter_by(assigned_employee_id=employee.id)
                if start_date:
                    courses = courses.filter(Course.created_at >= start_date)
                if end_date:
                    courses = courses.filter(Course.created_at <= end_date)
                
                commission_info = cls.calculate_employee_commission(employee.id, courses.all())
                total_commission += commission_info.get('total_commission', 0)
            
            return {
                'total_salary': total_salary,
                'total_commission': total_commission,
                'total_cost': total_salary + total_commission,
                'employee_count': len(employees)
            }
            
        except Exception as e:
            logger.error(f"计算员工成本失败: {str(e)}")
            return {
                'total_salary': 0,
                'total_commission': 0,
                'total_cost': 0,
                'employee_count': 0
            }
    
    @classmethod
    def calculate_revenue_detail(cls, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """计算收入明细"""
        try:
            query = Course.query
            if start_date:
                query = query.filter(Course.created_at >= start_date)
            if end_date:
                query = query.filter(Course.created_at <= end_date)
            
            courses = query.all()
            
            trial_revenue = 0
            new_course_revenue = 0
            renewal_revenue = 0
            refund_amount = 0
            total_fee = 0  # 总手续费
            
            for course in courses:
                if course.is_trial:
                    trial_revenue += cls.safe_float(course.trial_price, 0)
                    # 试听课也可能有手续费
                    if course.payment_channel == '淘宝':
                        trial_price = cls.safe_float(course.trial_price, 0)
                        fee_rate = cls.safe_float(course.snapshot_fee_rate, 0.006)
                        total_fee += trial_price * fee_rate
                else:
                    revenue = cls.safe_float(course.sessions, 0) * cls.safe_float(course.price, 0)
                    if course.is_renewal:
                        renewal_revenue += revenue
                    else:
                        new_course_revenue += revenue
                    
                    # 正课和续课的手续费
                    if course.payment_channel == '淘宝':
                        fee_rate = cls.safe_float(course.snapshot_fee_rate, 0.006)
                        total_fee += revenue * fee_rate
                
                # 计算退费（修正公式）
                if course.refunds:
                    for refund in course.refunds:
                        # 退费金额 = 退费节数 × 课程售价 - 退费手续费
                        refund_sessions = cls.safe_float(refund.refund_sessions, 0)
                        course_price = cls.safe_float(course.price, 0)
                        refund_fee = cls.safe_float(refund.refund_fee, 0)
                        
                        # 正确的退费金额计算
                        calculated_refund_amount = refund_sessions * course_price - refund_fee
                        refund_amount += calculated_refund_amount
                        
                        # 退费手续费也计入总手续费
                        total_fee += refund_fee
            
            return {
                'trial_revenue': trial_revenue,
                'new_course_revenue': new_course_revenue,
                'renewal_revenue': renewal_revenue,
                'total_revenue': trial_revenue + new_course_revenue + renewal_revenue,
                'refund_amount': refund_amount,
                'net_revenue': trial_revenue + new_course_revenue + renewal_revenue - refund_amount,
                'total_fee': total_fee  # 新增总手续费
            }
            
        except Exception as e:
            logger.error(f"计算收入明细失败: {str(e)}")
            return {
                'trial_revenue': 0,
                'new_course_revenue': 0,
                'renewal_revenue': 0,
                'total_revenue': 0,
                'refund_amount': 0,
                'net_revenue': 0,
                'total_fee': 0
            }