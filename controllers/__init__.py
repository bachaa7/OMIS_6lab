"""
Контроллеры (обработчики маршрутов)
"""

from .auth import auth_bp
from .admin import admin_bp
from .developer import developer_bp
from .expert import expert_bp
from .chat import chat_bp
from .api import api_bp

__all__ = ['auth_bp', 'admin_bp', 'developer_bp', 'expert_bp', 'chat_bp', 'api_bp']
