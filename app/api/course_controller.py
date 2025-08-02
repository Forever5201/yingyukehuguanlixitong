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
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from services.course_service import CourseService

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