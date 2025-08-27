"""
重构后的路由示例 - 展示如何使用服务层

这个文件展示了如何将 routes.py 中的业务逻辑迁移到服务层
"""

from flask import Blueprint, request, jsonify, session
from .services import RefundService, ProfitService, PerformanceService
from .models import Course, CourseRefund
import logging

logger = logging.getLogger(__name__)

# 创建重构示例蓝图
refactored_bp = Blueprint('refactored', __name__)


# ========== 退费相关路由 - 使用 RefundService ==========

@refactored_bp.route('/api/courses/<int:course_id>/refund-info', methods=['GET'])
def get_refund_info(course_id):
    """获取课程的可退费信息 - 重构版"""
    try:
        course = Course.query.get(course_id)
        if not course or course.is_trial:
            return jsonify({'success': False, 'message': '课程不存在或不是正课'}), 404
        
        # 使用服务层计算退费信息
        refund_calc = RefundService.calculate_refund_amount(course_id, 0)
        
        # 获取退费历史
        refund_history = RefundService.get_refund_history(course_id)
        
        return jsonify({
            'success': True,
            'refund_summary': {
                'total_refunded_sessions': refund_calc['total_refunded_sessions'],
                'total_refunded_amount': refund_calc['total_refunded_amount'],
                'refundable_sessions': refund_calc['remaining_sessions'] + refund_calc['total_refunded_sessions'],
                'remaining_sessions': refund_calc['remaining_sessions'],
                'unit_price': refund_calc['unit_price']
            },
            'refund_history': refund_history
        })
    except Exception as e:
        logger.error(f"获取退费信息失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取退费信息失败'}), 500


@refactored_bp.route('/api/courses/<int:course_id>/refund', methods=['POST'])
def apply_course_refund(course_id):
    """申请正课退费 - 重构版"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 准备退费数据
        refund_data = {
            'refund_sessions': int(data.get('refund_sessions', 0)),
            'refund_reason': data.get('refund_reason', ''),
            'refund_channel': data.get('refund_channel', '原路退回'),
            'refund_fee': float(data.get('refund_fee', 0)),
            'remark': data.get('remark', ''),
            'operator_name': session.get('user_name', 'System')
        }
        
        # 使用服务层处理退费（自带事务管理）
        success, message, refund = RefundService.process_refund(course_id, refund_data)
        
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        
        # 计算剩余信息
        refund_calc = RefundService.calculate_refund_amount(course_id, 0)
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'refund_id': refund.id,
                'refund_amount': refund.refund_amount,
                'actual_refund': refund.refund_amount - refund.refund_fee,
                'remaining_sessions': refund_calc['remaining_sessions']
            }
        })
        
    except Exception as e:
        logger.error(f"处理退费失败: {str(e)}")
        return jsonify({'success': False, 'message': '处理退费失败'}), 500


@refactored_bp.route('/api/courses/<int:course_id>/refund-history', methods=['GET'])
def get_refund_history(course_id):
    """获取课程退费历史 - 重构版"""
    try:
        # 直接使用服务层获取格式化的历史记录
        refund_history = RefundService.get_refund_history(course_id)
        
        return jsonify({
            'success': True,
            'data': refund_history
        })
    except Exception as e:
        logger.error(f"获取退费历史失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取退费历史失败'}), 500


# ========== 员工业绩相关路由 - 使用 PerformanceService ==========

@refactored_bp.route('/api/employees/<int:employee_id>/performance', methods=['GET'])
def get_employee_performance(employee_id):
    """获取员工业绩详情 - 重构版"""
    try:
        # 获取查询参数
        period = request.args.get('period', 'current_month')
        
        # 根据期间计算日期范围
        from datetime import datetime
        now = datetime.now()
        
        if period == 'current_month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now
        else:
            # 其他期间的处理...
            start_date = None
            end_date = None
        
        # 使用服务层获取业绩数据
        performance = PerformanceService.calculate_employee_performance(
            employee_id, start_date, end_date
        )
        
        return jsonify({
            'success': True,
            'data': performance
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"获取员工业绩失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取业绩数据失败'}), 500


@refactored_bp.route('/api/performance/ranking', methods=['GET'])
def get_performance_ranking():
    """获取业绩排名 - 重构版"""
    try:
        period = request.args.get('period', 'month')
        
        # 使用服务层获取排名数据
        ranking = PerformanceService.get_performance_ranking(period)
        
        return jsonify({
            'success': True,
            'data': ranking,
            'period': period
        })
        
    except Exception as e:
        logger.error(f"获取业绩排名失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取排名数据失败'}), 500


# ========== 利润报表相关路由 - 使用 ProfitService ==========

@refactored_bp.route('/api/profit-report', methods=['GET'])
def get_profit_report():
    """获取利润报表 - 重构版"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 转换日期
        from datetime import datetime
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 使用服务层生成报表
        report = ProfitService.generate_profit_report(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        logger.error(f"生成利润报表失败: {str(e)}")
        return jsonify({'success': False, 'message': '生成报表失败'}), 500


# ========== 复杂业务操作示例 - 使用事务管理 ==========

from .services import ComplexTransactionManager

@refactored_bp.route('/api/trial-courses/<int:trial_id>/convert', methods=['POST'])
def convert_trial_to_formal(trial_id):
    """试听转正课 - 重构版，使用事务管理"""
    try:
        # 获取正课数据
        data = request.get_json()
        
        formal_course_data = {
            'course_type': data.get('course_type'),
            'sessions': int(data.get('sessions', 0)),
            'price': float(data.get('price', 0)),
            'gift_sessions': int(data.get('gift_sessions', 0)),
            'cost': float(data.get('cost', 0)),
            'other_cost': float(data.get('other_cost', 0)),
            'payment_channel': data.get('payment_channel'),
            'meta': data.get('meta')
        }
        
        # 使用事务管理器处理复杂业务
        result = ComplexTransactionManager.process_trial_to_formal_conversion(
            trial_id, formal_course_data
        )
        
        return jsonify({
            'success': True,
            'message': '试听转正课成功',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"试听转正课失败: {str(e)}")
        return jsonify({'success': False, 'message': '转换失败'}), 500


# ========== 如何集成到现有系统 ==========
"""
集成步骤：

1. 在 app/__init__.py 中注册新的蓝图（用于测试）：
   from .routes_refactored import refactored_bp
   app.register_blueprint(refactored_bp, url_prefix='/v2')

2. 逐步迁移现有路由：
   - 选择一个功能模块（如退费）
   - 将业务逻辑移到对应的服务类
   - 更新路由使用服务类
   - 充分测试后替换原路由

3. 最终目标：
   - routes.py 只包含路由定义和请求/响应处理
   - 所有业务逻辑都在 services/ 目录中
   - 使用事务装饰器确保数据一致性
"""