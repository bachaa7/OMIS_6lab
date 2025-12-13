"""
Система логирования
Обеспечивает аудит действий пользователей
"""
from flask import request, session
from utils.database import Database
from models.log import Log


class SystemLogger:
    """
    Класс SystemLogger обеспечивает логирование действий в системе.
    Записывает информацию о действиях пользователей, ошибках и событиях.
    """

    @staticmethod
    def log(level, message, module=None, user_id=None):
        """
        Добавление записи в лог.

        Args:
            level (str): Уровень лога (INFO, WARNING, ERROR)
            message (str): Сообщение лога
            module (str): Модуль, из которого произошло событие
            user_id (int): ID пользователя (если есть)
        """
        db = Database()

        # Получаем информацию о запросе
        ip_address = request.remote_addr if request else None
        user_agent = request.user_agent.string if request and request.user_agent else None

        # Если user_id не передан, пытаемся взять из сессии
        if user_id is None and session:
            user_id = session.get('user_id')

        db.execute('''
                   INSERT INTO logs (level, message, module, user_id, ip_address, user_agent)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (level, message, module, user_id, ip_address, user_agent))

        db.commit()

    @staticmethod
    def info(message, module=None, user_id=None):
        """Логирование информационного сообщения"""
        SystemLogger.log('INFO', message, module, user_id)

    @staticmethod
    def warning(message, module=None, user_id=None):
        """Логирование предупреждения"""
        SystemLogger.log('WARNING', message, module, user_id)

    @staticmethod
    def error(message, module=None, user_id=None):
        """Логирование ошибки"""
        SystemLogger.log('ERROR', message, module, user_id)

    @staticmethod
    def log_action(module):
        """
        Декоратор для автоматического логирования действий.

        Args:
            module (str): Название модуля
        """
        from functools import wraps

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    result = f(*args, **kwargs)
                    if 'user_id' in session:
                        SystemLogger.info(
                            f'Выполнено действие: {f.__name__}',
                            module,
                            session['user_id']
                        )
                    return result
                except Exception as e:
                    if 'user_id' in session:
                        SystemLogger.error(
                            f'Ошибка в {f.__name__}: {str(e)}',
                            module,
                            session['user_id']
                        )
                    raise e

            return decorated_function

        return decorator