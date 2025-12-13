"""
Модель сообщения чата
Представляет взаимодействие в подсистеме NLP и интерфейса
"""
from datetime import datetime


class Message:
    """
    Класс Message представляет сообщение в чате.

    Атрибуты:
        id (int): Уникальный идентификатор
        user_id (int): ID пользователя
        assistant_id (int): ID помощника
        message (str): Текст запроса пользователя
        response (str): Ответ помощника
        intent (str): Определённый интент
        category (str): Категория запроса
        confidence (float): Уверенность классификации
        is_verified (bool): Верифицирован ли ответ
        created_at (datetime): Дата создания
    """

    def __init__(self, id=None, user_id=None, assistant_id=None,
                 message='', response='', intent='', category='',
                 confidence=0.0, is_verified=False, rating=None,
                 created_at=None):
        self.id = id
        self.user_id = user_id
        self.assistant_id = assistant_id
        self.message = message
        self.response = response
        self.intent = intent
        self.category = category
        self.confidence = confidence
        self.is_verified = is_verified
        self.rating = rating
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assistant_id': self.assistant_id,
            'message': self.message,
            'response': self.response,
            'intent': self.intent,
            'category': self.category,
            'confidence': self.confidence,
            'is_verified': self.is_verified,
            'rating': self.rating,
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
            user_id=row_dict['user_id'],
            assistant_id=row_dict.get('assistant_id'),
            message=row_dict['message'],
            response=row_dict.get('response', ''),
            intent=row_dict.get('intent', ''),
            category=row_dict.get('category', ''),
            confidence=row_dict.get('confidence', 0.0),
            is_verified=bool(row_dict.get('is_verified', False)),
            rating=row_dict.get('rating'),
            created_at=row_dict.get('created_at')
        )

    def __repr__(self):
        return f"<Message {self.id} intent={self.intent}>"