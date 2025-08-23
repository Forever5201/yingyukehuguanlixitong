"""
app/__init__.py 的修改建议
解决测试环境中路由不加载的问题
"""

# 在 app/__init__.py 的 create_app 函数中，修改路由导入部分：

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    if migrate_available:
        migrate.init_app(app, db)

    # 修改这部分：原来的代码
    # with app.app_context():
    #     # 注册传统路由（向后兼容）
    #     from . import routes
    
    # 改为：新的代码 - 无论是否在app_context中都导入路由
    # 注册传统路由（向后兼容）
    from . import routes
    
    # 注册新的统一API蓝图
    from .api.course_controller import course_api
    app.register_blueprint(course_api)
    
    # 其余代码保持不变...
    
    return app

# 或者，保持原有结构但添加测试支持：
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    if migrate_available:
        migrate.init_app(app, db)

    with app.app_context():
        # 注册传统路由（向后兼容）
        from . import routes
        
        # 注册新的统一API蓝图
        from .api.course_controller import course_api
        app.register_blueprint(course_api)
        
        # ... 其他代码 ...
        
        # 如果没有 Flask-Migrate，使用传统方式创建数据库
        if not migrate_available:
            db.create_all()
    
    # 重要：在测试环境中，确保路由已加载
    # 添加这个检查
    if app.config.get('TESTING'):
        # 强制确保routes模块已加载
        import app.routes
    
    # favicon 路由...
    
    return app