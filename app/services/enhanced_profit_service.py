"""
增强版利润计算服务 - 包含刷单成本和详细报表
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, func
from ..models import db, Course, Customer, Config, CourseRefund, Employee, CommissionConfig, TaobaoOrder
from .profit_service import ProfitService
from .operational_cost_service import OperationalCostService
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
        生成综合利润报表（刷单独立核算，不计入课程利润）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            综合利润报表数据
        """
        try:
            # 1. 获取基础利润报表（仅课程）
            base_report = cls.generate_profit_report(start_date, end_date)
            
            # 2. 计算刷单统计（独立核算，不计入课程成本）
            taobao_stats = cls.calculate_taobao_order_cost(start_date, end_date)
            
            # 3. 计算员工成本
            employee_cost = cls.calculate_employee_cost(start_date, end_date)
            
            # 4. 计算运营成本
            operational_cost = OperationalCostService.allocate_operational_costs_to_courses(start_date, end_date)
            
            # 5. 课程总收入（不包含刷单）
            total_revenue = base_report['summary']['total_revenue']
            
            # 6. 计算收入明细
            revenue_detail = cls.calculate_revenue_detail(start_date, end_date)
            
            # 6.5. 计算课程成本明细
            course_cost_detail = cls.calculate_course_cost_detail(start_date, end_date)
            
            # 7. 课程总成本（不包含刷单费用）
            # 课程成本 = 课程基础成本 + 课程手续费 + 员工成本 + 运营成本
            course_cost_without_fee = base_report['summary']['total_cost'] - base_report.get('total_fee', 0)
            total_fee_courses = base_report['summary']['total_fee']  # 仅课程手续费
            total_cost = (course_cost_without_fee +          # 课程成本（不含手续费）
                         total_fee_courses +                 # 课程手续费（不含刷单手续费）
                         employee_cost['total_cost'] +       # 员工成本
                         operational_cost['total_operational_cost'])  # 运营成本
            
            # 8. 计算课程净利润（不含刷单）
            net_profit = total_revenue - total_cost
            
            # 9. 刷单独立核算（佣金和手续费都是支出）
            # 刷单成本 = 佣金支出 + 手续费支出
            taobao_cost = taobao_stats['total_commission'] + taobao_stats['total_fee']
            
            # 10. 股东分配（仅基于课程利润，刷单单独结算）
            distribution_ratios = cls.calculate_shareholder_distribution(100)
            shareholder_a_net_profit = net_profit * (distribution_ratios['ratio_a'] / 100)
            shareholder_b_net_profit = net_profit * (distribution_ratios['ratio_b'] / 100)
            
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
                    'course_cost_detail': course_cost_detail,  # 课程成本明细
                    'total_fee': total_fee_courses,  # 仅课程手续费（不含刷单）
                    'employee_salary': employee_cost['total_salary'],
                    'employee_commission': employee_cost['total_commission'],
                    'operational_cost': operational_cost['total_operational_cost'],
                    'total_cost': total_cost  # 不含刷单费用
                },
                'profit': {
                    'gross_profit': base_report['summary']['total_profit'],  # 毛利润
                    'net_profit': net_profit,  # 课程净利润（不含刷单）
                    'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                },
                'shareholder_distribution': {
                    'shareholder_a_net_profit': shareholder_a_net_profit,
                    'shareholder_b_net_profit': shareholder_b_net_profit,
                    'total_distributed': shareholder_a_net_profit + shareholder_b_net_profit
                },
                # 刷单独立统计（与课程利润分开）
                'taobao_separate': {
                    'order_count': taobao_stats['order_count'],
                    'total_amount': taobao_stats['total_amount'],  # 刷单总金额（垫付，会返还）
                    'total_commission': taobao_stats['total_commission'],  # 佣金支出
                    'total_fee': taobao_stats['total_fee'],  # 手续费支出
                    'total_cost': taobao_cost,  # 刷单总成本 = 佣金 + 手续费
                    'settled_amount': taobao_stats['settled_amount'],
                    'unsettled_amount': taobao_stats['unsettled_amount']
                },
                'operational_cost_detail': operational_cost,
                'statistics': {
                    'course_count': base_report['summary']['course_count'],
                    'taobao_order_count': taobao_stats['order_count'],
                    'employee_count': employee_cost['employee_count']
                }
            }
            
        except Exception as e:
            logger.error(f"生成综合利润报表失败: {str(e)}")
            raise
    
    @classmethod
    def calculate_employee_cost(cls, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """
        计算员工成本（按时间范围计算底薪）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            员工成本统计
        """
        try:
            # 获取所有员工
            employees = Employee.query.all()
            
            # 计算月数（用于底薪计算）
            if start_date and end_date:
                # 计算跨越的月数
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
            else:
                months = 1  # 默认1个月
            
            total_salary = 0
            total_commission = 0
            
            for employee in employees:
                # 获取员工配置
                commission_config = CommissionConfig.query.filter_by(employee_id=employee.id).first()
                if commission_config:
                    # 基本工资按月数计算
                    total_salary += cls.safe_float(commission_config.base_salary, 0) * months
                
                # 计算该员工的提成（基于时间范围内的课程）
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
                'employee_count': len(employees),
                'months': months  # 返回计算的月数，便于调试
            }
            
        except Exception as e:
            logger.error(f"计算员工成本失败: {str(e)}")
            return {
                'total_salary': 0,
                'total_commission': 0,
                'total_cost': 0,
                'employee_count': 0,
                'months': 1
            }
    
    @classmethod
    def calculate_course_cost_detail(cls, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict:
        """
        计算课程成本明细（按试听课、新课、续课分类）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            课程成本明细数据
        """
        try:
            query = Course.query
            if start_date:
                query = query.filter(Course.created_at >= start_date)
            if end_date:
                query = query.filter(Course.created_at <= end_date)
            
            courses = query.all()
            
            trial_cost = 0
            new_course_cost = 0
            renewal_cost = 0
            
            for course in courses:
                # 获取课程基础成本（course.cost 已经包含 other_cost，不要重复计算）
                base_cost = cls.safe_float(course.cost, 0)
                
                if course.is_trial:
                    # 试听课成本
                    trial_cost += base_cost
                else:
                    # 正课成本（course.cost 已经包含 other_cost）
                    if course.is_renewal:
                        renewal_cost += base_cost
                    else:
                        new_course_cost += base_cost
            
            total_course_cost = trial_cost + new_course_cost + renewal_cost
            
            return {
                'trial_cost': trial_cost,
                'new_course_cost': new_course_cost, 
                'renewal_cost': renewal_cost,
                'total_course_cost': total_course_cost
            }
            
        except Exception as e:
            logger.error(f"计算课程成本明细失败: {str(e)}")
            return {
                'trial_cost': 0,
                'new_course_cost': 0,
                'renewal_cost': 0,
                'total_course_cost': 0
            }

    @classmethod
    def calculate_revenue_detail(cls, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """
        计算收入明细（使用统一的ProfitService计算，确保与其他报表一致）
        
        返回的收入是扣除退费后的实际收入
        """
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
            total_fee = 0
            
            for course in courses:
                # 使用统一的利润计算方法
                profit_info = cls.calculate_course_profit(course, include_refund=True)
                
                if course.is_trial:
                    # 试听课：退费状态的收入已经在calculate_course_profit中处理为0
                    if course.trial_status != 'refunded':
                        trial_revenue += profit_info['actual_revenue']
                        total_fee += profit_info['fee']
                else:
                    # 正课：使用实际收入（已扣除退费）
                    if course.is_renewal:
                        renewal_revenue += profit_info['actual_revenue']
                    else:
                        new_course_revenue += profit_info['actual_revenue']
                    total_fee += profit_info['fee']
                    
                    # 统计退费金额
                    if profit_info['has_refund'] and profit_info['refund_info']:
                        refund_amount += profit_info['refund_info']['amount']
            
            total_revenue = trial_revenue + new_course_revenue + renewal_revenue
            
            return {
                'trial_revenue': trial_revenue,
                'new_course_revenue': new_course_revenue,
                'renewal_revenue': renewal_revenue,
                'total_revenue': total_revenue,
                'refund_amount': refund_amount,
                'net_revenue': total_revenue,  # 已经是扣除退费后的收入
                'total_fee': total_fee
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