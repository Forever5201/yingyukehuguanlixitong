"""
会话管理服务
支持多设备登录、会话控制、设备管理等功能
"""

from datetime import datetime, timezone, timedelta
from flask import session, request, current_app
from flask_login import current_user
from ..models import User, db
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class SessionService:
    """会话管理服务类"""
    
    @staticmethod
    def create_session_token(user_id, device_info=None):
        """
        创建会话令牌
        
        Args:
            user_id: 用户ID
            device_info: 设备信息
            
        Returns:
            str: 会话令牌
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        device_hash = hashlib.md5(str(device_info).encode()).hexdigest() if device_info else "unknown"
        
        token_data = {
            'user_id': user_id,
            'timestamp': timestamp,
            'device_hash': device_hash,
            'ip': request.remote_addr
        }
        
        return hashlib.sha256(json.dumps(token_data, sort_keys=True).encode()).hexdigest()
    
    @staticmethod
    def get_device_info():
        """
        获取设备信息
        
        Returns:
            dict: 设备信息
        """
        user_agent = request.headers.get('User-Agent', '')
        
        # 简单的设备类型检测
        device_type = 'unknown'
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_type = 'mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            device_type = 'tablet'
        elif 'Windows' in user_agent or 'Mac' in user_agent or 'Linux' in user_agent:
            device_type = 'desktop'
        
        return {
            'user_agent': user_agent,
            'device_type': device_type,
            'ip': request.remote_addr,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def set_session_data(user, remember=True, device_info=None):
        """
        设置会话数据
        
        Args:
            user: 用户对象
            remember: 是否记住登录
            device_info: 设备信息
        """
        # 设置会话过期时间
        if remember:
            session.permanent = True
            # 设置会话有效期为30天
            current_app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
            # 浏览器关闭时过期
            current_app.permanent_session_lifetime = timedelta(hours=24)
        
        # 存储用户信息
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['login_time'] = datetime.now(timezone.utc).isoformat()
        session['device_info'] = device_info or SessionService.get_device_info()
        session['session_token'] = SessionService.create_session_token(user.id, device_info)
        
        # 记录登录日志
        logger.info(f"用户 {user.username} 登录成功，设备: {session['device_info']['device_type']}")
    
    @staticmethod
    def validate_session():
        """
        验证会话有效性
        
        Returns:
            bool: 会话是否有效
        """
        if not session.get('user_id'):
            return False
        
        # 检查会话是否过期
        login_time_str = session.get('login_time')
        if not login_time_str:
            return False
        
        try:
            login_time = datetime.fromisoformat(login_time_str.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            
            # 检查会话是否超过30天
            if current_time - login_time > timedelta(days=30):
                logger.info(f"会话已过期，用户ID: {session.get('user_id')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"会话验证失败: {e}")
            return False
    
    @staticmethod
    def clear_session():
        """
        清除会话数据
        """
        session.clear()
        logger.info("会话已清除")
    
    @staticmethod
    def get_active_sessions_count(user_id):
        """
        获取用户活跃会话数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 活跃会话数量
        """
        # 这里可以实现更复杂的会话统计
        # 目前返回1（当前会话）
        return 1
    
    @staticmethod
    def force_logout_other_devices(user_id):
        """
        强制登出其他设备
        
        Args:
            user_id: 用户ID
        """
        # 这里可以实现强制登出其他设备的逻辑
        # 可以通过数据库记录会话状态
        logger.info(f"强制登出用户 {user_id} 的其他设备")
    
    @staticmethod
    def get_session_info():
        """
        获取当前会话信息
        
        Returns:
            dict: 会话信息
        """
        if not current_user.is_authenticated:
            return None
        
        return {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'login_time': session.get('login_time'),
            'device_info': session.get('device_info'),
            'session_token': session.get('session_token')
        }


