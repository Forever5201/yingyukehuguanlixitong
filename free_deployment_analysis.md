"""
PythonAnywhere WSGI 配置文件
放置在: /var/www/your_username_pythonanywhere_com_wsgi.py
"""

import sys
import os

# 添加项目路径
project_folder = '/home/your_username/your_project_folder'
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

# 导入 Flask 应用
from app import create_app

application = create_app()

# 确保在 PythonAnywhere 环境下创建数据库
if not os.path.exists(os.path.join(project_folder, 'instance')):
    os.makedirs(os.path.join(project_folder, 'instance'))