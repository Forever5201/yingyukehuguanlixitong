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
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # 保存原始请求URL，登录后跳转回来
            next_page = request.args.get('next')
            if next_page:
                flash('请先登录后再访问该页面', 'warning')
            return redirect(url_for('main.login', next=next_page))
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


