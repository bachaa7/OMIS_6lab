"""
Модель пользователя системы
Представляет подсистему управления доступом
"""
import hashlib
from datetime import datetime


class User:
    """
    Класс User представляет пользователя системы.

    Атрибуты:
        id (int): Уникальный идентификатор
        username (str): Имя пользователя
        email (str): Email адрес
        password_hash (str): Хеш пароля
        role (str): Роль пользователя (admin, developer, expert, client)
        is_active (bool): Статус активности
        avatar_color (str): Цвет аватара
        created_at (datetime): Дата создания
    """

    def __init__(self, id=None, username='', email='', password_hash='',
                 role='client', is_active=True, avatar_color='#007bff',
                 created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.avatar_color = avatar_color
        self.created_at = created_at or datetime.now()

    @staticmethod
    def hash_password(password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """Проверка пароля"""
        return self.password_hash == self.hash_password(password)

    def has_role(self, role):
        """Проверка роли пользователя"""
        return self.role == role

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'avatar_color': self.avatar_color,
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
            username=row_dict['username'],
            email=row_dict['email'],
            password_hash=row_dict['password_hash'],
            role=row_dict['role'],
            is_active=bool(row_dict['is_active']),
            avatar_color=row_dict.get('avatar_color', '#007bff'),
            created_at=row_dict.get('created_at')
        )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"