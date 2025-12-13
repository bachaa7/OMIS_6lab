"""
Модель системного лога
Для мониторинга и аудита системы
"""
from datetime import datetime


class Log:
    """
    Класс Log представляет запись в системном журнале.

    Атрибуты:
        id (int): Уникальный идентификатор
        level (str): Уровень (INFO, WARNING, ERROR)
        message (str): Сообщение
        module (str): Модуль системы
        user_id (int): ID пользователя
        ip_address (str): IP адрес
        created_at (datetime): Дата создания
    """

    LEVELS = ['INFO', 'WARNING', 'ERROR']

    def __init__(self, id=None, level='INFO', message='', module='',
                 user_id=None, ip_address='', created_at=None):
        self.id = id
        self.level = level if level in self.LEVELS else 'INFO'
        self.message = message
        self.module = module
        self.user_id = user_id
        self.ip_address = ip_address
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'module': self.module,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

    @classmethod
    def from_db_row(cls, row):
        """Создание объекта из строки БД"""
        if not row:
            return None

        # Преобразуем sqlite3.Row в словарь
        row_dict = dict(row)

        return cls(
            id=row_dict['id'],
            level=row_dict['level'],
            message=row_dict['message'],
            module=row_dict.get('module', ''),
            user_id=row_dict.get('user_id'),
            ip_address=row_dict.get('ip_address', ''),
            created_at=row_dict.get('created_at')
        )

    def __repr__(self):
        return f"<Log {self.level}: {self.message[:50]}>"