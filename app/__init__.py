from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # 注册传统路由（向后兼容）
        from . import routes
        
        # 注册新的统一API蓝图
        from .api.course_controller import course_api
        app.register_blueprint(course_api)
        
        # 确保services目录存在
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        if not os.path.exists(services_dir):
            os.makedirs(services_dir)
            
        # 确保api目录存在
        api_dir = os.path.join(os.path.dirname(__file__), 'api')
        if not os.path.exists(api_dir):
            os.makedirs(api_dir)
        
        db.create_all()

    return app