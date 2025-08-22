from flask import Flask, send_from_directory, Response
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

    # favicon 路由，避免 /favicon.ico 404
    @app.route('/favicon.ico')
    def favicon():
        static_dir = os.path.join(app.root_path, 'static')
        ico = os.path.join(static_dir, 'favicon.ico')
        png = os.path.join(static_dir, 'favicon.png')
        if os.path.exists(ico):
            return send_from_directory(static_dir, 'favicon.ico', mimetype='image/x-icon')
        if os.path.exists(png):
            return send_from_directory(static_dir, 'favicon.png', mimetype='image/png')
        # 1x1 空白 PNG 兜底
        empty_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\x9ei\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return Response(empty_png, mimetype='image/png')

    return app