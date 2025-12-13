"""
Конфигурация приложения
"""
import os


class Config:
    """Базовая конфигурация"""

    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'legal-ai-secret-key-12345'
    DATABASE = 'legal_ai_platform.db'

    # Настройки безопасности
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True для HTTPS
    PERMANENT_SESSION_LIFETIME = 3600  # 1 час

    # Настройки NLP
    NLP_ENABLED = True
    NLP_CONFIDENCE_THRESHOLD = 0.3

    # Роли пользователей
    ROLES = {
        'admin': 'Администратор',
        'developer': 'Разработчик',
        'expert': 'Эксперт',
        'client': 'Клиент'
    }

    # Цвета аватаров по умолчанию
    ROLE_COLORS = {
        'admin': '#dc3545',
        'developer': '#17a2b8',
        'expert': '#28a745',
        'client': '#6c757d'
    }


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


# Выбор конфигурации
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}