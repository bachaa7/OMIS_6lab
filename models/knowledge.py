"""
Модель базы знаний
Представляет подсистему базы знаний
"""
from datetime import datetime


class KnowledgeBase:
    """
    Класс KnowledgeBase представляет элемент базы знаний.

    Атрибуты:
        id (int): Уникальный идентификатор
        title (str): Название документа/статьи
        content (str): Содержимое
        category (str): Категория (гражданское право, трудовое и т.д.)
        source (str): Источник информации
        icon (str): Иконка
        uploaded_by (int): ID загрузившего
        is_verified (bool): Верифицирован ли
        created_at (datetime): Дата создания
    """

    def __init__(self, id=None, title='', content='', category='',
                 source='', icon='📚', uploaded_by=None,
                 is_verified=False, created_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.source = source
        self.icon = icon
        self.uploaded_by = uploaded_by
        self.is_verified = is_verified
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'source': self.source,
            'icon': self.icon,
            'uploaded_by': self.uploaded_by,
            'is_verified': self.is_verified,
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
            title=row_dict['title'],
            content=row_dict['content'],
            category=row_dict.get('category', ''),
            source=row_dict.get('source', ''),
            icon=row_dict.get('icon', '📚'),
            uploaded_by=row_dict.get('uploaded_by'),
            is_verified=bool(row_dict.get('is_verified', False)),
            created_at=row_dict.get('created_at')
        )

    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"