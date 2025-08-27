"""
退费管理服务 - 处理所有退费相关的业务逻辑

功能：
1. 创建退费记录
2. 验证退费合法性
3. 重新计算利润和业绩
4. 事务管理确保数据一致性
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Course, CourseRefund, Customer
from .profit_service import ProfitService
import logging

logger = logging.getLogger(__name__)


class RefundService:
    """退费管理服务类"""
    
    @classmethod
    def validate_refund_request(cls, course_id: int, refund_sessions: int) -> Tuple[bool, str]:
        """
        验证退费请求的合法性
        
        Args:
            course_id: 课程ID
            refund_sessions: 申请退费的节数
            
        Returns:
            (是否合法, 错误信息)
        """
        try:
            course = Course.query.get(course_id)
            if not course:
                return False, "课程不存在"
            
            if course.is_trial:
                return False, "试听课不支持退费"
            
            # 计算已退费节数
            existing_refunds = CourseRefund.query.filter_by(
                course_id=course_id,
                status='completed'
            ).all()
            
            total_refunded = sum(r.refund_sessions for r in existing_refunds)
            remaining_sessions = ProfitService.safe_int(course.sessions) - total_refunded
            
            if refund_sessions <= 0:
                return False, "退费节数必须大于0"
            
            if refund_sessions > remaining_sessions:
                return False, f"退费节数超过剩余节数（剩余{remaining_sessions}节）"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"验证退费请求失败: {str(e)}")
            return False, "验证失败"
    
    @classmethod
    def calculate_refund_amount(cls, course_id: int, refund_sessions: int) -> Dict:
        """
        计算退费金额
        
        Args:
            course_id: 课程ID
            refund_sessions: 退费节数
            
        Returns:
            退费计算结果
        """
        try:
            course = Course.query.get(course_id)
            if not course:
                raise ValueError("课程不存在")
            
            # 单节价格
            unit_price = ProfitService.safe_float(course.price)
            
            # 退费金额 = 退费节数 × 单节价格
            refund_amount = refund_sessions * unit_price
            
            # 计算已退费信息
            existing_refunds = CourseRefund.query.filter_by(
                course_id=course_id,
                status='completed'
            ).all()
            
            total_refunded_sessions = sum(r.refund_sessions for r in existing_refunds)
            total_refunded_amount = sum(r.refund_amount for r in existing_refunds)
            
            # 计算剩余信息
            total_sessions = ProfitService.safe_int(course.sessions)
            remaining_sessions = total_sessions - total_refunded_sessions - refund_sessions
            remaining_amount = remaining_sessions * unit_price
            
            return {
                'unit_price': unit_price,
                'refund_amount': refund_amount,
                'refund_sessions': refund_sessions,
                'total_refunded_sessions': total_refunded_sessions + refund_sessions,
                'total_refunded_amount': total_refunded_amount + refund_amount,
                'remaining_sessions': remaining_sessions,
                'remaining_amount': remaining_amount,
                'original_sessions': total_sessions,
                'original_amount': total_sessions * unit_price
            }
            
        except Exception as e:
            logger.error(f"计算退费金额失败: {str(e)}")
            raise
    
    @classmethod
    def process_refund(cls, course_id: int, refund_data: Dict) -> Tuple[bool, str, Optional[CourseRefund]]:
        """
        处理退费请求（带事务）
        
        Args:
            course_id: 课程ID
            refund_data: 退费数据，包含:
                - refund_sessions: 退费节数
                - refund_reason: 退费原因
                - refund_channel: 退费渠道
                - refund_fee: 手续费
                - operator_name: 操作员
                - remark: 备注
                
        Returns:
            (成功与否, 消息, 退费记录)
        """
        try:
            # 验证请求
            is_valid, error_msg = cls.validate_refund_request(
                course_id, refund_data.get('refund_sessions', 0)
            )
            
            if not is_valid:
                return False, error_msg, None
            
            # 计算退费金额
            refund_calc = cls.calculate_refund_amount(
                course_id, refund_data['refund_sessions']
            )
            
            # 使用事务处理
            with db.session.begin():
                # 创建退费记录
                refund = CourseRefund(
                    course_id=course_id,
                    refund_sessions=refund_data['refund_sessions'],
                    refund_amount=refund_calc['refund_amount'],
                    refund_reason=refund_data.get('refund_reason', ''),
                    refund_channel=refund_data.get('refund_channel', ''),
                    refund_fee=ProfitService.safe_float(refund_data.get('refund_fee', 0)),
                    operator_name=refund_data.get('operator_name', ''),
                    remark=refund_data.get('remark', ''),
                    status='completed'
                )
                
                # 设置退课时间
                if refund_data.get('refund_date'):
                    try:
                        from datetime import datetime
                        refund.refund_date = datetime.fromisoformat(refund_data['refund_date'].replace('T', ' '))
                    except:
                        # 如果日期格式错误，使用当前时间
                        refund.refund_date = datetime.now()
                else:
                    # 如果没有提供退课时间，使用当前时间
                    refund.refund_date = datetime.now()
                
                db.session.add(refund)
                
                # 如果需要，可以在这里更新课程状态或其他相关数据
                # 例如：标记课程为部分退费状态
                
                # 提交事务
                db.session.flush()  # 确保获得ID
                
                logger.info(f"退费处理成功: course_id={course_id}, refund_id={refund.id}")
                return True, "退费处理成功", refund
                
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"退费处理数据库错误: {str(e)}")
            return False, "数据库操作失败", None
        except Exception as e:
            db.session.rollback()
            logger.error(f"退费处理失败: {str(e)}")
            return False, f"处理失败: {str(e)}", None
    
    @classmethod
    def cancel_refund(cls, refund_id: int, reason: str = "") -> Tuple[bool, str]:
        """
        取消退费记录
        
        Args:
            refund_id: 退费记录ID
            reason: 取消原因
            
        Returns:
            (成功与否, 消息)
        """
        try:
            with db.session.begin():
                refund = CourseRefund.query.get(refund_id)
                if not refund:
                    return False, "退费记录不存在"
                
                if refund.status != 'completed':
                    return False, "该退费记录已被取消"
                
                # 更新状态
                refund.status = 'cancelled'
                if reason:
                    refund.remark = f"{refund.remark}\n取消原因: {reason}" if refund.remark else f"取消原因: {reason}"
                
                db.session.flush()
                
                logger.info(f"退费取消成功: refund_id={refund_id}")
                return True, "退费取消成功"
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"取消退费失败: {str(e)}")
            return False, f"取消失败: {str(e)}"
    
    @classmethod
    def get_refund_history(cls, course_id: int) -> List[Dict]:
        """
        获取课程的退费历史
        
        Args:
            course_id: 课程ID
            
        Returns:
            退费记录列表
        """
        try:
            refunds = CourseRefund.query.filter_by(course_id=course_id).order_by(
                CourseRefund.created_at.desc()
            ).all()
            
            history = []
            for refund in refunds:
                history.append({
                    'id': refund.id,
                    'refund_sessions': refund.refund_sessions,
                    'refund_amount': refund.refund_amount,
                    'refund_reason': refund.refund_reason,
                    'refund_channel': refund.refund_channel,
                    'refund_fee': refund.refund_fee,
                    'refund_date': refund.refund_date.strftime('%Y-%m-%d %H:%M:%S') if refund.refund_date else '',
                    'status': refund.status,
                    'operator_name': refund.operator_name,
                    'remark': refund.remark,
                    'created_at': refund.created_at.strftime('%Y-%m-%d %H:%M:%S') if refund.created_at else ''
                })
            
            return history
            
        except Exception as e:
            logger.error(f"获取退费历史失败: {str(e)}")
            return []
    
    @classmethod
    def get_refund_summary(cls, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> Dict:
        """
        获取退费汇总统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            退费统计数据
        """
        try:
            query = CourseRefund.query.filter_by(status='completed')
            
            if start_date:
                query = query.filter(CourseRefund.refund_date >= start_date)
            if end_date:
                query = query.filter(CourseRefund.refund_date <= end_date)
            
            refunds = query.all()
            
            # 统计数据
            total_count = len(refunds)
            total_sessions = sum(r.refund_sessions for r in refunds)
            total_amount = sum(r.refund_amount for r in refunds)
            total_fee = sum(r.refund_fee for r in refunds)
            
            # 按渠道统计
            channel_stats = {}
            for refund in refunds:
                channel = refund.refund_channel or '未知'
                if channel not in channel_stats:
                    channel_stats[channel] = {
                        'count': 0,
                        'sessions': 0,
                        'amount': 0,
                        'fee': 0
                    }
                
                channel_stats[channel]['count'] += 1
                channel_stats[channel]['sessions'] += refund.refund_sessions
                channel_stats[channel]['amount'] += refund.refund_amount
                channel_stats[channel]['fee'] += refund.refund_fee
            
            return {
                'total': {
                    'count': total_count,
                    'sessions': total_sessions,
                    'amount': total_amount,
                    'fee': total_fee,
                    'net_amount': total_amount - total_fee
                },
                'by_channel': channel_stats,
                'period': {
                    'start': start_date.strftime('%Y-%m-%d') if start_date else None,
                    'end': end_date.strftime('%Y-%m-%d') if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"获取退费汇总失败: {str(e)}")
            return {
                'total': {
                    'count': 0,
                    'sessions': 0,
                    'amount': 0,
                    'fee': 0,
                    'net_amount': 0
                },
                'by_channel': {},
                'period': {}
            }