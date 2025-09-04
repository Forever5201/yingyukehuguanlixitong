"""
主蓝图定义

说明：
- 仅负责提供 Blueprint 实例，不包含任何路由定义。
- 现有的 `app/routes.py` 会导入并在该蓝图上注册所有路由。
- 这样做为了后续按模块拆分时可以保持同一个 `main_bp` 对象，避免破坏现有 URL 与模板调用。
"""

from flask import Blueprint


main_bp = Blueprint('main', __name__)

