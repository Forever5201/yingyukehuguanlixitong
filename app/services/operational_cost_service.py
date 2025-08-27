"""
运营成本管理服务 - 处理房租、水电等运营成本的记录、分配和计算
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy import and_, func
from ..models import db, OperationalCost, Course
import logging

logger = logging.getLogger(__name__)


class OperationalCostService:
    """运营成本管理服务类"""
    
    @staticmethod
    def safe_float(value, default=0):
        """安全转换为浮点数"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_date(value, default=None):
        """安全转换为日期"""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass
        return default or date.today()
    
    @classmethod
    def create_operational_cost(cls, cost_data: Dict) -> Tuple[bool, str, Optional[OperationalCost]]:
        """
        创建运营成本记录
        
        Args:
            cost_data: 成本数据字典
            
        Returns:
            (成功标志, 消息, 成本对象)
        """
        try:
            # 验证必填字段
            required_fields = ['cost_type', 'cost_name', 'amount', 'cost_date']
            for field in required_fields:
                if not cost_data.get(field):
                    return False, f'缺少必填字段: {field}', None
            
            # 创建成本记录
            cost = OperationalCost(
                cost_type=cost_data['cost_type'],
                cost_name=cost_data['cost_name'],
                amount=cls.safe_float(cost_data['amount']),
                cost_date=cls.safe_date(cost_data['cost_date']),
                billing_period=cost_data.get('billing_period', 'month'),
                allocation_method=cost_data.get('allocation_method', 'proportional'),
                allocated_to_courses=cost_data.get('allocated_to_courses', True),
                description=cost_data.get('description', ''),
                invoice_number=cost_data.get('invoice_number', ''),
                supplier=cost_data.get('supplier', ''),
                payment_recipient=cost_data.get('payment_recipient', ''),
                status=cost_data.get('status', 'active')
            )
            
            db.session.add(cost)
            db.session.commit()
            
            return True, '运营成本创建成功', cost
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建运营成本失败: {str(e)}")
            return False, f'创建失败: {str(e)}', None
    
    @classmethod
    def update_operational_cost(cls, cost_id: int, cost_data: Dict) -> Tuple[bool, str]:
        """
        更新运营成本记录
        
        Args:
            cost_id: 成本记录ID
            cost_data: 更新的成本数据
            
        Returns:
            (成功标志, 消息)
        """
        try:
            cost = OperationalCost.query.get(cost_id)
            if not cost:
                return False, '成本记录不存在'
            
            # 更新字段
            if 'cost_type' in cost_data:
                cost.cost_type = cost_data['cost_type']
            if 'cost_name' in cost_data:
                cost.cost_name = cost_data['cost_name']
            if 'amount' in cost_data:
                cost.amount = cls.safe_float(cost_data['amount'])
            if 'cost_date' in cost_data:
                cost.cost_date = cls.safe_date(cost_data['cost_date'])
            if 'billing_period' in cost_data:
                cost.billing_period = cost_data['billing_period']
            if 'allocation_method' in cost_data:
                cost.allocation_method = cost_data['allocation_method']
            if 'allocated_to_courses' in cost_data:
                cost.allocated_to_courses = cost_data['allocated_to_courses']
            if 'description' in cost_data:
                cost.description = cost_data['description']
            if 'invoice_number' in cost_data:
                cost.invoice_number = cost_data['invoice_number']
            if 'supplier' in cost_data:
                cost.supplier = cost_data['supplier']
            if 'payment_recipient' in cost_data:
                cost.payment_recipient = cost_data['payment_recipient']
            if 'status' in cost_data:
                cost.status = cost_data['status']
            
            cost.updated_at = datetime.now()
            db.session.commit()
            
            return True, '运营成本更新成功'
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新运营成本失败: {str(e)}")
            return False, f'更新失败: {str(e)}'
    
    @classmethod
    def delete_operational_cost(cls, cost_id: int) -> Tuple[bool, str]:
        """
        删除运营成本记录
        
        Args:
            cost_id: 成本记录ID
            
        Returns:
            (成功标志, 消息)
        """
        try:
            cost = OperationalCost.query.get(cost_id)
            if not cost:
                return False, '成本记录不存在'
            
            db.session.delete(cost)
            db.session.commit()
            
            return True, '运营成本删除成功'
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除运营成本失败: {str(e)}")
            return False, f'删除失败: {str(e)}'
    
    @classmethod
    def get_operational_costs(cls, start_date: Optional[date] = None, 
                             end_date: Optional[date] = None,
                             cost_type: Optional[str] = None,
                             status: Optional[str] = None) -> List[OperationalCost]:
        """
        获取运营成本记录列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            cost_type: 成本类型筛选
            status: 状态筛选
            
        Returns:
            成本记录列表
        """
        try:
            query = OperationalCost.query
            
            if start_date:
                query = query.filter(OperationalCost.cost_date >= start_date)
            if end_date:
                query = query.filter(OperationalCost.cost_date <= end_date)
            if cost_type:
                query = query.filter(OperationalCost.cost_type == cost_type)
            if status:
                query = query.filter(OperationalCost.status == status)
            
            # 按日期倒序排列
            query = query.order_by(OperationalCost.cost_date.desc())
            
            return query.all()
            
        except Exception as e:
            logger.error(f"获取运营成本列表失败: {str(e)}")
            return []
    
    @classmethod
    def calculate_operational_costs_for_period(cls, start_date: Optional[datetime] = None,
                                             end_date: Optional[datetime] = None) -> Dict:
        """
        计算指定时间段的运营成本统计
        
        Args:
            start_date: 开始日期时间
            end_date: 结束日期时间
            
        Returns:
            运营成本统计信息
        """
        try:
            # 转换日期时间到日期
            start_date_obj = start_date.date() if start_date else None
            end_date_obj = end_date.date() if end_date else None
            
            # 获取成本记录
            costs = cls.get_operational_costs(start_date_obj, end_date_obj, status='active')
            
            # 按类型分组统计
            cost_by_type = {}
            total_amount = 0
            
            for cost in costs:
                cost_type = cost.cost_type
                amount = cls.safe_float(cost.amount)
                
                if cost_type not in cost_by_type:
                    cost_by_type[cost_type] = {
                        'amount': 0,
                        'count': 0,
                        'items': []
                    }
                
                cost_by_type[cost_type]['amount'] += amount
                cost_by_type[cost_type]['count'] += 1
                cost_by_type[cost_type]['items'].append({
                    'id': cost.id,
                    'name': cost.cost_name,
                    'amount': amount,
                    'date': cost.cost_date.strftime('%Y-%m-%d'),
                    'description': cost.description
                })
                
                total_amount += amount
            
            return {
                'total_amount': total_amount,
                'cost_by_type': cost_by_type,
                'cost_count': len(costs),
                'period': {
                    'start_date': start_date_obj.strftime('%Y-%m-%d') if start_date_obj else '开始',
                    'end_date': end_date_obj.strftime('%Y-%m-%d') if end_date_obj else '至今'
                }
            }
            
        except Exception as e:
            logger.error(f"计算运营成本统计失败: {str(e)}")
            return {
                'total_amount': 0,
                'cost_by_type': {},
                'cost_count': 0,
                'period': {
                    'start_date': '开始',
                    'end_date': '至今'
                }
            }
    
    @classmethod
    def allocate_operational_costs_to_courses(cls, start_date: Optional[datetime] = None,
                                            end_date: Optional[datetime] = None) -> Dict:
        """
        将运营成本按比例分配到指定时间段的课程
        
        Args:
            start_date: 开始日期时间
            end_date: 结束日期时间
            
        Returns:
            成本分配信息
        """
        try:
            # 1. 获取时间段内的运营成本
            operational_costs = cls.calculate_operational_costs_for_period(start_date, end_date)
            
            # 2. 获取时间段内的课程数量
            course_query = Course.query
            if start_date:
                course_query = course_query.filter(Course.created_at >= start_date)
            if end_date:
                course_query = course_query.filter(Course.created_at <= end_date)
            
            course_count = course_query.count()
            
            # 3. 计算每门课程应分摊的运营成本
            total_operational_cost = operational_costs['total_amount']
            cost_per_course = total_operational_cost / course_count if course_count > 0 else 0
            
            return {
                'total_operational_cost': total_operational_cost,
                'cost_per_course': cost_per_course,
                'course_count': course_count,
                'cost_breakdown': operational_costs['cost_by_type'],
                'allocation_method': 'proportional',  # 按比例分配
                'period': operational_costs['period']
            }
            
        except Exception as e:
            logger.error(f"分配运营成本到课程失败: {str(e)}")
            return {
                'total_operational_cost': 0,
                'cost_per_course': 0,
                'course_count': 0,
                'cost_breakdown': {},
                'allocation_method': 'proportional',
                'period': {
                    'start_date': '开始',
                    'end_date': '至今'
                }
            }
    
    @classmethod
    def get_cost_type_options(cls) -> List[str]:
        """获取成本类型选项"""
        return [
            '房租',
            '水电费',
            '网络费',
            '设备费',
            '营销费',
            '办公用品',
            '清洁费',
            '其他'
        ]
    
    @classmethod
    def get_billing_period_options(cls) -> List[str]:
        """获取计费周期选项"""
        return [
            'month',    # 月
            'quarter',  # 季
            'year',     # 年
            'one-time'  # 一次性
        ]
