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
            # 总收入 = 课程收入（不包含刷单金额）
            total_revenue = base_report['summary']['total_revenue']
            
            # 5. 计算试听课收入和正课收入的详细分类
            revenue_detail = cls.calculate_revenue_detail(start_date, end_date)
            
            # 6. 总成本 = 课程成本（不含手续费） + 所有手续费 + 刷单佣金 + 刷单手续费 + 员工成本
            # 从base_report中减去已计算的手续费，避免重复
            course_cost_without_fee = base_report['summary']['total_cost'] - base_report.get('total_fee', 0)
            total_cost = (course_cost_without_fee +          # 课程成本（不含手续费）
                         revenue_detail['total_fee'] +        # 所有课程手续费
                         taobao_cost['total_cost'] +          # 刷单佣金和手续费
                         employee_cost['total_cost'])          # 员工成本
            
            # 7. 计算净利润
            net_profit = total_revenue - total_cost
            
            # 7. 重新计算股东分配
            # 获取新课和续课的毛利润（来自base_report）
            new_course_gross_profit = base_report['profit_by_type'].get('new_course', 0)
            renewal_gross_profit = base_report['profit_by_type'].get('renewal', 0)
            
            # 获取分配比例
            new_distribution_ratios = cls.calculate_shareholder_distribution(100, False)  # 获取比例
            renewal_distribution_ratios = cls.calculate_shareholder_distribution(100, True)  # 获取比例
            
            # 计算每个股东的收入份额
            shareholder_a_revenue_share = (
                new_course_gross_profit * (new_distribution_ratios['ratio_a'] / 100) +
                renewal_gross_profit * (renewal_distribution_ratios['ratio_a'] / 100)
            )
            shareholder_b_revenue_share = (
                new_course_gross_profit * (new_distribution_ratios['ratio_b'] / 100) +
                renewal_gross_profit * (renewal_distribution_ratios['ratio_b'] / 100)
            )
            
            # 计算需要分担的额外成本（试听课亏损、刷单成本、员工成本等）
            trial_loss = -base_report['profit_by_type'].get('trial', 0)  # 试听课通常是亏损的
            additional_costs = (
                trial_loss +
                taobao_cost['total_cost'] +  # 刷单佣金和手续费（不含刷单金额，因为已在收入中抵消）
                employee_cost['total_cost']   # 员工成本
            )
            
            # 每个股东分担50%的额外成本
            cost_per_shareholder = additional_costs * 0.5
            
            # 计算每个股东的净利润
            shareholder_a_net_profit = shareholder_a_revenue_share - cost_per_shareholder
            shareholder_b_net_profit = shareholder_b_revenue_share - cost_per_shareholder
            
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
                    'total_revenue': total_revenue,
                    'refund_amount': revenue_detail['refund_amount']
                },
                'cost': {
                    'course_cost': course_cost_without_fee,  # 课程成本（不含手续费）
                    'total_fee': revenue_detail['total_fee'],  # 总手续费（试听+正课+续课）
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
                    'shareholder_a_net_profit': shareholder_a_net_profit,
                    'shareholder_b_net_profit': shareholder_b_net_profit,
                    'total_distributed': shareholder_a_net_profit + shareholder_b_net_profit
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
                
                # 计算退费
                if course.refunds:
                    for refund in course.refunds:
                        # 在利润报表中，退费金额应该是实际退给客户的金额
                        # 退费手续费是从退款中扣除的，不是成本
                        refund_total = cls.safe_float(refund.refund_amount, 0)
                        refund_fee = cls.safe_float(refund.refund_fee, 0)
                        actual_refund = refund_total - refund_fee  # 实际退款金额
                        
                        refund_amount += actual_refund  # 累加实际退款金额
                        
                        # 注意：退费手续费不应计入总手续费（成本）
                        # 因为退费手续费是企业从退款中扣留的收入，不是成本
            
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