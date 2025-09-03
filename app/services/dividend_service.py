"""
股东分红记录管理服务
与现有利润分配系统完美集成
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from app.models import db, DividendRecord, DividendSummary, Config
from app.services.profit_service import ProfitService
import logging

logger = logging.getLogger(__name__)


class DividendService:
    """股东分红记录管理服务"""
    
    @classmethod
    def get_shareholders(cls) -> List[Dict]:
        """获取所有股东信息"""
        try:
            # 从Config表获取股东名称配置
            shareholder_a_config = Config.query.filter_by(key='shareholder_a_name').first()
            shareholder_b_config = Config.query.filter_by(key='shareholder_b_name').first()
            
            shareholder_a_name = shareholder_a_config.value if shareholder_a_config else '股东A'
            shareholder_b_name = shareholder_b_config.value if shareholder_b_config else '股东B'
            
            # 获取分红汇总信息
            summaries = DividendSummary.query.all()
            summary_dict = {s.shareholder_name: s for s in summaries}
            
            # 构建股东信息列表
            shareholders = []
            for name in [shareholder_a_name, shareholder_b_name]:
                summary = summary_dict.get(name)
                if not summary:
                    # 如果没有汇总记录，创建一个
                    summary = cls._create_summary_record(name)
                
                shareholders.append({
                    'name': name,
                    'summary': summary.to_dict()
                })
            
            return shareholders
            
        except Exception as e:
            logger.error(f"获取股东信息失败: {str(e)}")
            return []
    
    @classmethod
    def _create_summary_record(cls, shareholder_name: str) -> DividendSummary:
        """创建股东汇总记录"""
        try:
            summary = DividendSummary(shareholder_name=shareholder_name)
            db.session.add(summary)
            db.session.commit()
            return summary
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建股东汇总记录失败: {str(e)}")
            raise
    
    @classmethod
    def get_dividend_records(cls, shareholder_name: str = None, 
                           year: int = None, month: int = None,
                           status: str = None, limit: int = 50) -> List[Dict]:
        """获取分红记录列表"""
        try:
            query = DividendRecord.query
            
            # 应用筛选条件
            if shareholder_name:
                query = query.filter(DividendRecord.shareholder_name == shareholder_name)
            if year:
                query = query.filter(DividendRecord.period_year == year)
            if month:
                query = query.filter(DividendRecord.period_month == month)
            if status:
                query = query.filter(DividendRecord.status == status)
            
            # 按时间倒序排列
            records = query.order_by(DividendRecord.dividend_date.desc(), 
                                   DividendRecord.created_at.desc()).limit(limit).all()
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"获取分红记录失败: {str(e)}")
            return []
    
    @classmethod
    def create_dividend_record(cls, data: Dict) -> Tuple[bool, str, Optional[DividendRecord]]:
        """创建分红记录"""
        try:
            # 验证必要字段
            required_fields = ['shareholder_name', 'period_year', 'period_month', 
                             'calculated_profit', 'actual_dividend', 'dividend_date']
            for field in required_fields:
                if field not in data or data[field] is None:
                    return False, f"缺少必要字段: {field}", None
            
            # 验证股东名称
            shareholders = cls.get_shareholders()
            valid_names = [s['name'] for s in shareholders]
            if data['shareholder_name'] not in valid_names:
                return False, f"无效的股东名称: {data['shareholder_name']}", None
            
            # 验证金额
            try:
                calculated_profit = float(data['calculated_profit'])
                actual_dividend = float(data['actual_dividend'])
                if calculated_profit < 0 or actual_dividend < 0:
                    return False, "分红金额不能为负数", None
            except (ValueError, TypeError):
                return False, "分红金额必须为有效数字", None
            
            # 验证日期
            try:
                if isinstance(data['dividend_date'], str):
                    dividend_date = datetime.strptime(data['dividend_date'], '%Y-%m-%d').date()
                else:
                    dividend_date = data['dividend_date']
            except (ValueError, TypeError):
                return False, "无效的分红日期格式", None
            
            # 检查重复记录
            existing_record = DividendRecord.query.filter_by(
                shareholder_name=data['shareholder_name'],
                period_year=data['period_year'],
                period_month=data['period_month'],
                dividend_date=dividend_date
            ).first()
            
            if existing_record:
                return False, "该时期的分红记录已存在", None
            
            # 创建分红记录
            record = DividendRecord(
                shareholder_name=data['shareholder_name'],
                period_year=int(data['period_year']),
                period_month=int(data['period_month']),
                calculated_profit=calculated_profit,
                actual_dividend=actual_dividend,
                dividend_date=dividend_date,
                status=data.get('status', 'pending'),
                payment_method=data.get('payment_method', ''),
                remarks=data.get('remarks', ''),
                operator_name=data.get('operator_name', ''),
                snapshot_total_profit=data.get('snapshot_total_profit'),
                snapshot_profit_ratio=data.get('snapshot_profit_ratio')
            )
            
            db.session.add(record)
            
            # 更新汇总记录
            cls._update_dividend_summary(data['shareholder_name'])
            
            db.session.commit()
            
            return True, "分红记录创建成功", record
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建分红记录失败: {str(e)}")
            return False, f"创建失败: {str(e)}", None
    
    @classmethod
    def update_dividend_record(cls, record_id: int, data: Dict) -> Tuple[bool, str]:
        """更新分红记录"""
        try:
            record = DividendRecord.query.get(record_id)
            if not record:
                return False, "分红记录不存在"
            
            # 记录原股东名称用于更新汇总
            old_shareholder_name = record.shareholder_name
            
            # 更新字段
            updatable_fields = ['actual_dividend', 'status', 'payment_method', 
                              'remarks', 'operator_name']
            
            for field in updatable_fields:
                if field in data:
                    if field == 'actual_dividend':
                        try:
                            value = float(data[field])
                            if value < 0:
                                return False, "分红金额不能为负数"
                            setattr(record, field, value)
                        except (ValueError, TypeError):
                            return False, "分红金额必须为有效数字"
                    else:
                        setattr(record, field, data[field])
            
            record.updated_at = datetime.now()
            
            # 更新汇总记录
            cls._update_dividend_summary(old_shareholder_name)
            if 'shareholder_name' in data and data['shareholder_name'] != old_shareholder_name:
                cls._update_dividend_summary(data['shareholder_name'])
            
            db.session.commit()
            
            return True, "分红记录更新成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新分红记录失败: {str(e)}")
            return False, f"更新失败: {str(e)}"
    
    @classmethod
    def delete_dividend_record(cls, record_id: int) -> Tuple[bool, str]:
        """删除分红记录"""
        try:
            record = DividendRecord.query.get(record_id)
            if not record:
                return False, "分红记录不存在"
            
            shareholder_name = record.shareholder_name
            
            db.session.delete(record)
            
            # 更新汇总记录
            cls._update_dividend_summary(shareholder_name)
            
            db.session.commit()
            
            return True, "分红记录删除成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除分红记录失败: {str(e)}")
            return False, f"删除失败: {str(e)}"
    
    @classmethod
    def _update_dividend_summary(cls, shareholder_name: str):
        """更新股东分红汇总"""
        try:
            # 获取或创建汇总记录
            summary = DividendSummary.query.filter_by(shareholder_name=shareholder_name).first()
            if not summary:
                summary = DividendSummary(shareholder_name=shareholder_name)
                db.session.add(summary)
            
            # 重新计算汇总数据
            records = DividendRecord.query.filter_by(shareholder_name=shareholder_name).all()
            
            total_calculated = sum(r.calculated_profit for r in records)
            total_paid = sum(r.actual_dividend for r in records if r.status == 'paid')
            total_pending = sum(r.actual_dividend for r in records if r.status == 'pending')
            
            # 获取最后分红日期
            last_paid_record = DividendRecord.query.filter(
                and_(DividendRecord.shareholder_name == shareholder_name,
                     DividendRecord.status == 'paid')
            ).order_by(DividendRecord.dividend_date.desc()).first()
            
            # 更新汇总记录
            summary.total_calculated = total_calculated
            summary.total_paid = total_paid
            summary.total_pending = total_pending
            summary.record_count = len(records)
            summary.last_dividend_date = last_paid_record.dividend_date if last_paid_record else None
            summary.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"更新分红汇总失败: {str(e)}")
            raise
    
    @classmethod
    def calculate_current_period_profit(cls, year: int, month: int) -> Dict:
        """计算指定期间的利润分配"""
        try:
            # 使用现有的利润计算服务
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            # 获取利润报表
            profit_report = ProfitService.generate_comprehensive_profit_report(start_date, end_date)
            
            # 获取股东信息
            shareholders = cls.get_shareholders()
            
            # 构建结果
            result = {
                'period': {
                    'year': year,
                    'month': month,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                'profit_summary': {
                    'total_revenue': profit_report['revenue']['total_revenue'],
                    'total_cost': profit_report['cost']['total_cost'],
                    'net_profit': profit_report['profit']['net_profit'],
                    'profit_margin': profit_report['profit']['profit_margin']
                },
                'shareholder_distribution': {
                    shareholders[0]['name']: profit_report['shareholder_distribution']['shareholder_a_net_profit'],
                    shareholders[1]['name']: profit_report['shareholder_distribution']['shareholder_b_net_profit'],
                    'total_distributed': profit_report['shareholder_distribution']['total_distributed']
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"计算当期利润失败: {str(e)}")
            return {}
    
    @classmethod
    def get_dividend_statistics(cls, shareholder_name: str = None) -> Dict:
        """获取分红统计信息"""
        try:
            base_query = DividendRecord.query
            if shareholder_name:
                base_query = base_query.filter(DividendRecord.shareholder_name == shareholder_name)
            
            # 基础统计
            total_records = base_query.count()
            total_calculated = db.session.query(func.sum(DividendRecord.calculated_profit)).filter(
                DividendRecord.shareholder_name == shareholder_name if shareholder_name else True
            ).scalar() or 0
            
            total_paid = db.session.query(func.sum(DividendRecord.actual_dividend)).filter(
                and_(DividendRecord.status == 'paid',
                     DividendRecord.shareholder_name == shareholder_name if shareholder_name else True)
            ).scalar() or 0
            
            total_pending = db.session.query(func.sum(DividendRecord.actual_dividend)).filter(
                and_(DividendRecord.status == 'pending',
                     DividendRecord.shareholder_name == shareholder_name if shareholder_name else True)
            ).scalar() or 0
            
            # 按年度统计
            yearly_stats = db.session.query(
                DividendRecord.period_year,
                func.sum(DividendRecord.calculated_profit).label('year_calculated'),
                func.sum(DividendRecord.actual_dividend).label('year_dividend'),
                func.count().label('year_count')
            ).filter(
                DividendRecord.shareholder_name == shareholder_name if shareholder_name else True
            ).group_by(DividendRecord.period_year).order_by(DividendRecord.period_year.desc()).all()
            
            return {
                'total_records': total_records,
                'total_calculated': total_calculated,
                'total_paid': total_paid,
                'total_pending': total_pending,
                'unpaid_amount': total_calculated - total_paid,
                'yearly_stats': [
                    {
                        'year': stat.period_year,
                        'calculated_profit': stat.year_calculated,
                        'actual_dividend': stat.year_dividend,
                        'record_count': stat.year_count
                    }
                    for stat in yearly_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"获取分红统计失败: {str(e)}")
            return {}