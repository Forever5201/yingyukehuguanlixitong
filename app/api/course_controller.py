"""
课程API控制器 - 统一的RESTful API接口

实现正规软件开发规范中的API设计原则：
1. 统一的资源命名
2. 标准的HTTP状态码
3. 一致的响应格式
4. 清晰的错误处理
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

# 使用相对导入避免循环导入问题
try:
    from ..services.course_service import CourseService
    from ..services.course_service_adapter import (
        CourseServiceAdapter, 
        ServiceException,
        ValidationException,
        BusinessLogicException
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from services.course_service import CourseService
    from services.course_service_adapter import (
        CourseServiceAdapter,
        ServiceException,
        ValidationException,
        BusinessLogicException
    )

logger = logging.getLogger(__name__)

# 创建蓝图
course_api = Blueprint('course_api', __name__, url_prefix='/api/v1')

class ApiResponse:
    """统一的API响应格式"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict:
        """成功响应"""
        return {
            'success': True,
            'message': message,
            'data': data
        }
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, details: Any = None) -> Dict:
        """错误响应"""
        response = {
            'success': False,
            'message': message,
            'code': code
        }
        if details:
            response['details'] = details
        return response

@course_api.route('/courses', methods=['GET'])
def get_courses():
    """
    获取课程列表
    
    Query Parameters:
        - type: 课程类型 (trial/formal, 可选)
        - status: 课程状态 (可选)
        - include_customer: 是否包含客户详情 (true/false, 默认true)
    """
    try:
        # 解析查询参数
        course_type = request.args.get('type')
        status = request.args.get('status')
        include_customer = request.args.get('include_customer', 'true').lower() == 'true'
        
        # 验证参数
        if course_type and course_type not in ['trial', 'formal']:
            return jsonify(ApiResponse.error("课程类型参数无效")), 400
        
        # 获取课程数据
        courses = CourseService.get_courses(
            course_type=course_type,
            status=status,
            include_customer=True
        )
        
        # 格式化数据
        formatted_courses = CourseService.format_course_data(
            courses, 
            include_customer_details=include_customer
        )
        
        # 计算业绩统计
        performance = CourseService.calculate_performance(courses)
        
        response_data = {
            'courses': formatted_courses,
            'performance': performance,
            'total_count': len(formatted_courses)
        }
        
        return jsonify(ApiResponse.success(response_data))
        
    except Exception as e:
        logger.error(f"获取课程列表失败: {str(e)}")
        return jsonify(ApiResponse.error("获取课程列表失败")), 500

@course_api.route('/courses/trial', methods=['GET'])
def get_trial_courses():
    """
    获取试听课列表（使用适配器模式）
    
    Query Parameters:
        - status: 试听课状态
        - employee_id: 员工ID
        - start_date: 开始日期
        - end_date: 结束日期
    """
    try:
        # 获取查询参数
        status = request.args.get('status')
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 调用服务层适配器
        result = CourseServiceAdapter.get_trial_courses(
            status=status,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(result)
        
    except ServiceException as e:
        logger.error(f"服务层错误: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 500
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        return jsonify(ApiResponse.error("获取试听课列表失败")), 500

@course_api.route('/courses/trial', methods=['POST'])
def create_trial_course():
    """
    创建试听课（使用适配器模式）
    
    Request Body:
        - customer_id: 客户ID（可选，如果没有则创建新客户）
        - customer_name: 客户姓名（创建新客户时需要）
        - customer_phone: 客户电话（创建新客户时必需）
        - customer_gender: 客户性别
        - customer_grade: 客户年级
        - customer_region: 客户地区
        - trial_price: 试听价格
        - source: 渠道来源
        - assigned_employee_id: 分配的员工ID
    """
    try:
        data = request.get_json()
        
        # 调用服务层适配器
        result = CourseServiceAdapter.create_trial_course(data)
        
        return jsonify(result), 201
        
    except ValidationException as e:
        return jsonify(ApiResponse.error(str(e), 400)), 400
    except BusinessLogicException as e:
        return jsonify(ApiResponse.error(str(e), 409)), 409
    except ServiceException as e:
        return jsonify(ApiResponse.error(str(e))), 500
    except Exception as e:
        logger.error(f"创建试听课失败: {str(e)}")
        return jsonify(ApiResponse.error("创建试听课失败")), 500

@course_api.route('/courses/trial/<int:trial_id>/convert', methods=['POST'])
def convert_trial_to_formal(trial_id):
    """
    试听课转正课
    
    Path Parameters:
        - trial_id: 试听课ID
        
    Request Body:
        - course_type: 课程类型
        - sessions: 购买节数
        - gift_sessions: 赠送节数
        - price: 单节售价
        - payment_channel: 支付渠道
        - cost: 成本
        - other_cost: 其他成本
    """
    try:
        data = request.get_json()
        
        # 调用服务层适配器
        result = CourseServiceAdapter.convert_trial_to_formal(trial_id, data)
        
        return jsonify(result), 201
        
    except ValidationException as e:
        return jsonify(ApiResponse.error(str(e), 400)), 400
    except BusinessLogicException as e:
        return jsonify(ApiResponse.error(str(e), 409)), 409
    except ServiceException as e:
        return jsonify(ApiResponse.error(str(e))), 500
    except Exception as e:
        logger.error(f"试听课转正失败: {str(e)}")
        return jsonify(ApiResponse.error("试听课转正失败")), 500

@course_api.route('/courses/status-mapping', methods=['GET'])
def get_status_mapping():
    """获取课程状态映射"""
    try:
        mapping = CourseService.get_status_mapping()
        return jsonify(ApiResponse.success(mapping))
    except Exception as e:
        logger.error(f"获取状态映射失败: {str(e)}")
        return jsonify(ApiResponse.error("获取状态映射失败")), 500

# 错误处理
@course_api.errorhandler(404)
def not_found(error):
    return jsonify(ApiResponse.error("资源未找到", 404)), 404

@course_api.errorhandler(400)
def bad_request(error):
    return jsonify(ApiResponse.error("请求参数错误", 400)), 400

@course_api.errorhandler(500)
def internal_error(error):
    return jsonify(ApiResponse.error("服务器内部错误", 500)), 500