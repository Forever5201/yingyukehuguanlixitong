import os
import secrets

class Config:
    # 使用固定的SECRET_KEY，避免重启时session失效
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-do-not-use-in-production-2024-stable-session'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database performance optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'pool_timeout': 30
    }
    
    # Session security configuration - 优化session配置
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # 增加session有效期
    PERMANENT_SESSION_LIFETIME = 60 * 24 * 60 * 60  # 60天（秒）
    # session cookie名称
    SESSION_COOKIE_NAME = 'education_session'
    
    # Upload size limit
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Cache configuration
    SEND_FILE_MAX_AGE_DEFAULT = 3600