"""
认证装饰器
用于保护需要登录的路由
"""

from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user, login_required
from .services.auth_service import AuthService


def login_required_custom(f):
    """
    自定义登录验证装饰器
    支持API和页面请求的不同处理方式
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from .services.session_service import SessionService
        
        # 首先检查Flask-Login状态
        flask_login_authenticated = current_user.is_authenticated
        
        # 检查自定义session状态
        custom_session_valid = SessionService.validate_session()
        
        # 如果两者都无效，则需要重新登录
        if not flask_login_authenticated and not custom_session_valid:
            # 判断是否为API请求
            if request.path.startswith('/api/'):
                # API请求返回JSON错误
                from flask import jsonify
                return jsonify({
                    'success': False,
                    'message': '登录状态已过期，请重新登录',
                    'error_code': 'UNAUTHORIZED',
                    'redirect_url': '/login'
                }), 401
            else:
                # 页面请求重定向到登录页
                next_page = request.args.get('next')
                if next_page:
                    flash('登录状态已过期，请重新登录', 'warning')
                return redirect(url_for('main.login', next=next_page))
        
        # 如果Flask-Login无效但session有效，尝试同步状态
        elif not flask_login_authenticated and custom_session_valid:
            try:
                from flask_login import login_user
                from .models import User
                from flask import session
                
                user_id = session.get('user_id')
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        login_user(user, remember=True)
                        print(f"同步用户登录状态: {user.username}")
            except Exception as e:
                print(f"同步登录状态失败: {e}")
                # 如果同步失败，清除所有会话
                SessionService.clear_session()
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({
                        'success': False,
                        'message': '登录状态异常，请重新登录',
                        'error_code': 'UNAUTHORIZED',
                        'redirect_url': '/login'
                    }), 401
                else:
                    flash('登录状态异常，请重新登录', 'warning')
                    return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    管理员权限验证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('main.login'))
        
        if not AuthService.is_admin(current_user):
            flash('您没有权限访问该页面', 'error')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function


def optional_login(f):
    """
    可选登录装饰器（已登录用户显示更多信息）
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这个装饰器不强制要求登录，但会传递登录状态给模板
        return f(*args, **kwargs)
    return decorated_function


