"""
Модель виртуального помощника
Представляет подсистему помощников
"""
from datetime import datetime


class Assistant:
    """
    Класс Assistant представляет виртуального помощника.

    Атрибуты:
        id (int): Уникальный идентификатор
        name (str): Название помощника
        description (str): Описание функционала
        specialty (str): Специализация
        icon (str): Иконка (эмодзи)
        color (str): Цвет темы
        created_by (int): ID создателя
        is_active (bool): Статус активности
        created_at (datetime): Дата создания
    """

    def __init__(self, id=None, name='', description='', specialty='',
                 icon='⚖️', color='#007bff', created_by=None,
                 is_active=True, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.specialty = specialty
        self.icon = icon
        self.color = color
        self.created_by = created_by
        self.is_active = is_active
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'specialty': self.specialty,
            'icon': self.icon,
            'color': self.color,
            'created_by': self.created_by,
            'is_active': self.is_active,
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
            name=row_dict['name'],
            description=row_dict.get('description', ''),
            specialty=row_dict.get('specialty', ''),
            icon=row_dict.get('icon', '⚖️'),
            color=row_dict.get('color', '#007bff'),
            created_by=row_dict.get('created_by'),
            is_active=bool(row_dict.get('is_active', True)),
            created_at=row_dict.get('created_at')
        )

    def __repr__(self):
        return f"<Assistant {self.name} ({self.specialty})>"