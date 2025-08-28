"""
业绩统计服务 - 管理员工业绩相关的所有计算逻辑

功能：
1. 员工业绩统计
2. 业绩排名计算
3. 业绩趋势分析
4. 转化率计算
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_, func, case
from ..models import db, Course, Customer, Employee, CommissionConfig
from .profit_service import ProfitService
import logging

logger = logging.getLogger(__name__)


class PerformanceService:
    """业绩统计服务类"""
    
    @classmethod
    def calculate_employee_performance(cls, employee_id: int, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict:
        """
        计算员工业绩详情
        
        Args:
            employee_id: 员工ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            员工业绩数据
        """
        try:
            # 获取员工信息
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError(f"员工不存在 (ID: {employee_id})")
            
            # 构建基础查询
            query = db.session.query(Course, Customer).join(
                Customer, Course.customer_id == Customer.id
            ).filter(Course.assigned_employee_id == employee_id)
            
            if start_date:
                query = query.filter(Course.created_at >= start_date)
            if end_date:
                query = query.filter(Course.created_at <= end_date)
            
            courses = query.all()
            
            # 统计各类业绩
            trial_stats = cls._calculate_trial_performance(courses)
            formal_stats = cls._calculate_formal_performance(courses)
            conversion_stats = cls._calculate_conversion_rate(courses)
            
            # 计算提成
            commission_info = ProfitService.calculate_employee_commission(
                employee_id, [course for course, _ in courses]
            )
            
            return {
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'phone': employee.phone,
                    'email': employee.email
                },
                'trial_courses': trial_stats,
                'formal_courses': formal_stats,
                'conversion': conversion_stats,
                'commission': commission_info,
                'total_revenue': trial_stats['revenue'] + formal_stats['revenue'],
                'total_profit': trial_stats['profit'] + formal_stats['profit']
            }
            
        except Exception as e:
            logger.error(f"计算员工业绩失败 (employee_id={employee_id}): {str(e)}")
            raise
    
    @classmethod
    def _calculate_trial_performance(cls, courses: List[Tuple[Course, Customer]]) -> Dict:
        """计算试听课业绩"""
        trial_courses = [(c, cust) for c, cust in courses if c.is_trial]
        
        total_count = len(trial_courses)
        registered = sum(1 for c, _ in trial_courses if c.trial_status == 'registered')
        scheduled = sum(1 for c, _ in trial_courses if c.trial_status == 'scheduled')
        completed = sum(1 for c, _ in trial_courses if c.trial_status == 'completed')
        converted = sum(1 for c, _ in trial_courses if c.trial_status == 'converted')
        
        total_revenue = 0
        total_profit = 0
        
        for course, _ in trial_courses:
            profit_info = ProfitService.calculate_course_profit(course)
            total_revenue += profit_info['actual_revenue']
            total_profit += profit_info['profit']
        
        return {
            'count': total_count,
            'registered': registered,
            'scheduled': scheduled,
            'completed': completed,
            'converted': converted,
            'revenue': total_revenue,
            'profit': total_profit,
            'conversion_rate': (converted / completed * 100) if completed > 0 else 0
        }
    
    @classmethod
    def _calculate_formal_performance(cls, courses: List[Tuple[Course, Customer]]) -> Dict:
        """计算正课业绩"""
        formal_courses = [(c, cust) for c, cust in courses if not c.is_trial]
        
        new_courses = [(c, cust) for c, cust in formal_courses if not c.is_renewal]
        renewal_courses = [(c, cust) for c, cust in formal_courses if c.is_renewal]
        
        # 计算新课业绩
        new_revenue = 0
        new_profit = 0
        for course, _ in new_courses:
            profit_info = ProfitService.calculate_course_profit(course)
            new_revenue += profit_info['actual_revenue']
            new_profit += profit_info['profit']
        
        # 计算续课业绩
        renewal_revenue = 0
        renewal_profit = 0
        for course, _ in renewal_courses:
            profit_info = ProfitService.calculate_course_profit(course)
            renewal_revenue += profit_info['actual_revenue']
            renewal_profit += profit_info['profit']
        
        return {
            'total_count': len(formal_courses),
            'new_count': len(new_courses),
            'renewal_count': len(renewal_courses),
            'new_revenue': new_revenue,
            'new_profit': new_profit,
            'renewal_revenue': renewal_revenue,
            'renewal_profit': renewal_profit,
            'total_revenue': new_revenue + renewal_revenue,
            'total_profit': new_profit + renewal_profit
        }
    
    @classmethod
    def _calculate_conversion_rate(cls, courses: List[Tuple[Course, Customer]]) -> Dict:
        """计算转化率"""
        # 找出所有试听课
        trial_courses = {c.id: c for c, _ in courses if c.is_trial}
        
        # 找出转化的试听课
        converted_trials = set()
        for course, _ in courses:
            if not course.is_trial and course.converted_from_trial:
                converted_trials.add(course.converted_from_trial)
        
        completed_trials = sum(1 for c in trial_courses.values() 
                             if c.trial_status == 'completed')
        
        return {
            'total_trials': len(trial_courses),
            'completed_trials': completed_trials,
            'converted_count': len(converted_trials),
            'conversion_rate': (len(converted_trials) / completed_trials * 100) 
                             if completed_trials > 0 else 0
        }
    
    @classmethod
    def get_performance_ranking(cls, period: str = 'month') -> List[Dict]:
        """
        获取员工业绩排名
        
        Args:
            period: 统计周期 ('month', 'quarter', 'year')
            
        Returns:
            排名列表
        """
        try:
            # 计算时间范围
            now = datetime.now()
            if period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0)
            elif period == 'quarter':
                quarter_month = ((now.month - 1) // 3) * 3 + 1
                start_date = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0)
            else:  # year
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
            
            # 获取所有员工
            employees = Employee.query.all()
            ranking_data = []
            
            for employee in employees:
                performance = cls.calculate_employee_performance(
                    employee.id, start_date, now
                )
                
                ranking_data.append({
                    'rank': 0,  # 稍后计算
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'total_revenue': performance['total_revenue'],
                    'total_profit': performance['total_profit'],
                    'trial_count': performance['trial_courses']['count'],
                    'formal_count': performance['formal_courses']['total_count'],
                    'conversion_rate': performance['conversion']['conversion_rate'],
                    'commission': performance['commission']['total_commission']
                })
            
            # 按收入排序并设置排名
            ranking_data.sort(key=lambda x: x['total_revenue'], reverse=True)
            for i, item in enumerate(ranking_data):
                item['rank'] = i + 1
            
            return ranking_data
            
        except Exception as e:
            logger.error(f"获取业绩排名失败: {str(e)}")
            return []
    
    @classmethod
    def get_performance_trend(cls, employee_id: int, months: int = 6) -> Dict:
        """
        获取员工业绩趋势
        
        Args:
            employee_id: 员工ID
            months: 统计月数
            
        Returns:
            趋势数据
        """
        try:
            trend_data = []
            now = datetime.now()
            
            for i in range(months):
                # 计算每个月的时间范围
                end_date = now.replace(day=1) - timedelta(days=1) if i > 0 else now
                start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1) if i > 0 else now.replace(day=1)
                
                if i > 0:
                    # 往前推月份
                    for _ in range(i - 1):
                        end_date = start_date - timedelta(days=1)
                        start_date = end_date.replace(day=1)
                
                # 获取该月业绩
                performance = cls.calculate_employee_performance(
                    employee_id, start_date, end_date
                )
                
                trend_data.append({
                    'month': start_date.strftime('%Y-%m'),
                    'revenue': performance['total_revenue'],
                    'profit': performance['total_profit'],
                    'trial_count': performance['trial_courses']['count'],
                    'formal_count': performance['formal_courses']['total_count'],
                    'conversion_rate': performance['conversion']['conversion_rate']
                })
            
            # 反转数据，使其按时间正序
            trend_data.reverse()
            
            return {
                'employee_id': employee_id,
                'months': months,
                'trend': trend_data
            }
            
        except Exception as e:
            logger.error(f"获取业绩趋势失败 (employee_id={employee_id}): {str(e)}")
            raise