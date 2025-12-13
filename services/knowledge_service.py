"""
Сервис работы с базой знаний
Представляет подсистему базы знаний
"""
from models.knowledge import KnowledgeBase
from utils.database import Database
from utils.logger import SystemLogger


class KnowledgeService:
    """
    Сервис KnowledgeService обеспечивает работу с базой юридических знаний.
    Управляет статьями, шаблонами и нормативными актами.
    """

    @staticmethod
    def add_knowledge(title, content, category, source, icon='📚',
                      uploaded_by=None, is_verified=False):
        """
        Добавление материала в базу знаний.

        Args:
            title (str): Название
            content (str): Содержимое
            category (str): Категория
            source (str): Источник
            icon (str): Иконка
            uploaded_by (int): ID загрузившего
            is_verified (bool): Верифицирован ли

        Returns:
            int: ID созданной записи
        """
        db = Database()

        cursor = db.execute('''
                            INSERT INTO knowledge_base (title, content, category, source, icon,
                                                        uploaded_by, is_verified)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (title, content, category, source, icon, uploaded_by, is_verified))

        db.commit()
        knowledge_id = cursor.lastrowid

        SystemLogger.info(
            f'Добавлен материал в базу знаний: {title}',
            'knowledge',
            uploaded_by
        )

        return knowledge_id

    @staticmethod
    def search_knowledge(query, category=None):
        """
        Поиск в базе знаний.

        Args:
            query (str): Поисковый запрос
            category (str): Категория для фильтрации

        Returns:
            list: Список найденных записей
        """
        db = Database()

        if category:
            sql = '''
                  SELECT * \
                  FROM knowledge_base
                  WHERE (title LIKE ? OR content LIKE ?)
                    AND category = ?
                    AND is_verified = 1
                  ORDER BY uploaded_at DESC \
                  '''
            params = (f'%{query}%', f'%{query}%', category)
        else:
            sql = '''
                  SELECT * \
                  FROM knowledge_base
                  WHERE (title LIKE ? OR content LIKE ?)
                    AND is_verified = 1
                  ORDER BY uploaded_at DESC \
                  '''
            params = (f'%{query}%', f'%{query}%')

        rows = db.execute_all(sql, params)
        return [KnowledgeBase.from_db_row(row) for row in rows]

    @staticmethod
    def get_all_knowledge():
        """
        Получение всех материалов базы знаний.

        Returns:
            list: Список всех записей
        """
        db = Database()
        rows = db.execute_all('''
                              SELECT kb.*, u.username as uploader_name
                              FROM knowledge_base kb
                                       LEFT JOIN users u ON kb.uploaded_by = u.id
                              ORDER BY kb.uploaded_at DESC
                              ''')
        return rows

    @staticmethod
    def verify_knowledge(knowledge_id, verified_by):
        """
        Верификация материала экспертом.

        Args:
            knowledge_id (int): ID материала
            verified_by (int): ID верифицирующего эксперта
        """
        db = Database()
        db.execute('''
                   UPDATE knowledge_base
                   SET is_verified = 1,
                       verified_by = ?
                   WHERE id = ?
                   ''', (verified_by, knowledge_id))
        db.commit()

        SystemLogger.info(
            f'Материал {knowledge_id} верифицирован',
            'knowledge',
            verified_by
        )

    @staticmethod
    def get_by_category(category):
        """
        Получение материалов по категории.

        Args:
            category (str): Категория

        Returns:
            list: Список материалов
        """
        db = Database()
        rows = db.execute_all('''
                              SELECT *
                              FROM knowledge_base
                              WHERE category = ?
                                AND is_verified = 1
                              ORDER BY uploaded_at DESC
                              ''', (category,))
        return [KnowledgeBase.from_db_row(row) for row in rows]