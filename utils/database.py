"""
Класс для работы с базой данных SQLite
Обеспечивает централизованный доступ к данным
"""
import sqlite3
from flask import g
from config import Config


class Database:
    """
    Класс Database обеспечивает работу с SQLite базой данных.
    Использует паттерн Singleton для управления подключениями.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE

    def get_connection(self):
        """
        Получение подключения к БД.
        Использует Flask g для хранения подключения в контексте запроса.
        """
        if 'db' not in g:
            g.db = sqlite3.connect(self.db_path)
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_connection(self):
        """Закрытие подключения к БД"""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def execute(self, query, params=()):
        """
        Выполнение SQL запроса с параметрами.

        Args:
            query (str): SQL запрос
            params (tuple): Параметры запроса

        Returns:
            Cursor: Курсор с результатами
        """
        conn = self.get_connection()
        return conn.execute(query, params)

    def execute_one(self, query, params=()):
        """
        Выполнение запроса и получение одной строки.

        Returns:
            Row или None: Первая строка результата или None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def execute_all(self, query, params=()):
        """
        Выполнение запроса и получение всех строк.

        Returns:
            list: Список строк результата
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def commit(self):
        """Фиксация изменений в БД"""
        conn = self.get_connection()
        conn.commit()

    def init_database(self):
        """
        Инициализация структуры базы данных.
        Создаёт все необходимые таблицы.
        """
        conn = self.get_connection()

        # Таблица пользователей
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS users
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         username
                         TEXT
                         UNIQUE
                         NOT
                         NULL,
                         email
                         TEXT
                         UNIQUE
                         NOT
                         NULL,
                         password_hash
                         TEXT
                         NOT
                         NULL,
                         role
                         TEXT
                         NOT
                         NULL
                         DEFAULT
                         'client',
                         created_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         is_active
                         BOOLEAN
                         DEFAULT
                         1,
                         avatar_color
                         TEXT
                         DEFAULT
                         '#007bff'
                     )
                     ''')

        # Таблица помощников
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS assistants
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         name
                         TEXT
                         NOT
                         NULL,
                         description
                         TEXT,
                         specialty
                         TEXT,
                         icon
                         TEXT
                         DEFAULT
                         '⚖️',
                         color
                         TEXT
                         DEFAULT
                         '#007bff',
                         created_by
                         INTEGER,
                         created_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         is_active
                         BOOLEAN
                         DEFAULT
                         1,
                         FOREIGN
                         KEY
                     (
                         created_by
                     ) REFERENCES users
                     (
                         id
                     )
                         )
                     ''')

        # Таблица сообщений
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS chat_messages
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         user_id
                         INTEGER
                         NOT
                         NULL,
                         assistant_id
                         INTEGER,
                         message
                         TEXT
                         NOT
                         NULL,
                         response
                         TEXT,
                         intent
                         TEXT,
                         category
                         TEXT,
                         confidence
                         FLOAT
                         DEFAULT
                         0.0,
                         created_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         rating
                         INTEGER,
                         is_verified
                         BOOLEAN
                         DEFAULT
                         0,
                         verified_by
                         INTEGER,
                         verification_notes
                         TEXT,
                         FOREIGN
                         KEY
                     (
                         user_id
                     ) REFERENCES users
                     (
                         id
                     ),
                         FOREIGN KEY
                     (
                         assistant_id
                     ) REFERENCES assistants
                     (
                         id
                     ),
                         FOREIGN KEY
                     (
                         verified_by
                     ) REFERENCES users
                     (
                         id
                     )
                         )
                     ''')

        # Таблица базы знаний
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS knowledge_base
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         title
                         TEXT
                         NOT
                         NULL,
                         content
                         TEXT
                         NOT
                         NULL,
                         category
                         TEXT,
                         source
                         TEXT,
                         icon
                         TEXT
                         DEFAULT
                         '📚',
                         uploaded_by
                         INTEGER,
                         uploaded_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         is_verified
                         BOOLEAN
                         DEFAULT
                         0,
                         verified_by
                         INTEGER,
                         FOREIGN
                         KEY
                     (
                         uploaded_by
                     ) REFERENCES users
                     (
                         id
                     ),
                         FOREIGN KEY
                     (
                         verified_by
                     ) REFERENCES users
                     (
                         id
                     )
                         )
                     ''')

        # Таблица логов
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS logs
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         level
                         TEXT
                         NOT
                         NULL,
                         message
                         TEXT
                         NOT
                         NULL,
                         module
                         TEXT,
                         user_id
                         INTEGER,
                         ip_address
                         TEXT,
                         user_agent
                         TEXT,
                         created_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         FOREIGN
                         KEY
                     (
                         user_id
                     ) REFERENCES users
                     (
                         id
                     )
                         )
                     ''')

        # Таблица тестов
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS tests
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         name
                         TEXT
                         NOT
                         NULL,
                         description
                         TEXT,
                         test_type
                         TEXT
                         NOT
                         NULL,
                         code
                         TEXT,
                         expected_output
                         TEXT,
                         actual_output
                         TEXT,
                         status
                         TEXT
                         DEFAULT
                         'pending',
                         created_by
                         INTEGER,
                         created_at
                         TIMESTAMP
                         DEFAULT
                         CURRENT_TIMESTAMP,
                         executed_at
                         TIMESTAMP,
                         FOREIGN
                         KEY
                     (
                         created_by
                     ) REFERENCES users
                     (
                         id
                     )
                         )
                     ''')

        self.commit()
        print("✅ База данных инициализирована")