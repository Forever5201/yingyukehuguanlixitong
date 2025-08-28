"""
用户认证服务
处理用户登录、验证、权限管理等功能
"""

from datetime import datetime, timezone
from flask import session, flash
from flask_login import login_user, logout_user, current_user
from ..models import User, db
from .session_service import SessionService
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            tuple: (success, message, user)
        """
        try:
            # 查找用户
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return False, "用户名不存在", None
            
            if not user.is_active:
                return False, "账户已被禁用", None
            
            # 验证密码
            if not user.check_password(password):
                return False, "密码错误", None
            
            # 更新最后登录时间
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # 获取设备信息
            device_info = SessionService.get_device_info()
            
            # 设置会话数据
            SessionService.set_session_data(user, remember=True, device_info=device_info)
            
            # 登录用户
            login_user(user, remember=True)
            
            logger.info(f"用户 {username} 登录成功")
            return True, "登录成功", user
            
        except Exception as e:
            logger.error(f"用户登录失败: {str(e)}")
            return False, "登录失败，请稍后重试", None
    
    @staticmethod
    def logout_user_service():
        """
        用户登出
        
        Returns:
            bool: 是否成功登出
        """
        try:
            if current_user.is_authenticated:
                logger.info(f"用户 {current_user.username} 登出")
            
            logout_user()
            SessionService.clear_session()
            return True
            
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            return False
    
    @staticmethod
    def create_default_user():
        """
        创建默认管理员用户
        
        Returns:
            bool: 是否成功创建
        """
        try:
            # 检查是否已存在默认用户
            existing_user = User.query.filter_by(username='17844540733').first()
            if existing_user:
                logger.info("默认用户已存在")
                return True
            
            # 创建默认用户
            user = User(
                username='17844540733',
                email='admin@example.com',
                role='admin',
                is_active=True
            )
            user.set_password('yuan971035088')
            
            db.session.add(user)
            db.session.commit()
            
            logger.info("默认管理员用户创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建默认用户失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象或None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象或None
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def is_admin(user):
        """
        检查用户是否为管理员
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否为管理员
        """
        return user and user.role == 'admin'
    
    @staticmethod
    def require_admin(user):
        """
        要求管理员权限
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否有管理员权限
        """
        if not user or not user.is_authenticated:
            return False
        return AuthService.is_admin(user)
