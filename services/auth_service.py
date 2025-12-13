"""
Сервис аутентификации и авторизации
Представляет подсистему управления доступом
"""
from models.user import User
from utils.database import Database
from utils.logger import SystemLogger


class AuthService:
    """
    Сервис AuthService обеспечивает аутентификацию и авторизацию пользователей.
    Управляет регистрацией, входом и проверкой прав доступа.
    """

    @staticmethod
    def register_user(username, email, password, role='client'):
        """
        Регистрация нового пользователя.

        Args:
            username (str): Имя пользователя
            email (str): Email адрес
            password (str): Пароль
            role (str): Роль пользователя

        Returns:
            tuple: (успех, сообщение, user_id)
        """
        db = Database()

        # Проверка существования пользователя
        existing = db.execute_one(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username, email)
        )

        if existing:
            return False, 'Пользователь с таким именем или email уже существует', None

        # Хеширование пароля
        password_hash = User.hash_password(password)

        # Создание пользователя
        cursor = db.execute('''
                            INSERT INTO users (username, email, password_hash, role)
                            VALUES (?, ?, ?, ?)
                            ''', (username, email, password_hash, role))

        db.commit()
        user_id = cursor.lastrowid

        # Логирование
        SystemLogger.info(
            f'Зарегистрирован новый пользователь: {username} (роль: {role})',
            'auth',
            user_id
        )

        return True, 'Регистрация успешна', user_id

    @staticmethod
    def authenticate(username, password):
        """
        Аутентификация пользователя.

        Args:
            username (str): Имя пользователя
            password (str): Пароль

        Returns:
            tuple: (успех, сообщение, user_object)
        """
        db = Database()

        # Поиск пользователя
        user_row = db.execute_one(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        )

        if not user_row:
            SystemLogger.warning(
                f'Попытка входа с несуществующим именем: {username}',
                'auth'
            )
            return False, 'Неверное имя пользователя или пароль', None

        user = User.from_db_row(user_row)

        # Проверка активности
        if not user.is_active:
            SystemLogger.warning(
                f'Попытка входа в заблокированный аккаунт: {username}',
                'auth',
                user.id
            )
            return False, 'Аккаунт заблокирован', None

        # Проверка пароля
        if not user.check_password(password):
            SystemLogger.warning(
                f'Неверный пароль для пользователя: {username}',
                'auth',
                user.id
            )
            return False, 'Неверное имя пользователя или пароль', None

        # Успешный вход
        SystemLogger.info(
            f'Пользователь {username} вошел в систему',
            'auth',
            user.id
        )

        return True, 'Вход выполнен успешно', user

    @staticmethod
    def get_user_by_id(user_id):
        """
        Получение пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            User или None: Объект пользователя
        """
        db = Database()
        user_row = db.execute_one('SELECT * FROM users WHERE id = ?', (user_id,))
        return User.from_db_row(user_row)

    @staticmethod
    def update_user_status(user_id, is_active):
        """
        Изменение статуса пользователя (активация/деактивация).

        Args:
            user_id (int): ID пользователя
            is_active (bool): Новый статус
        """
        db = Database()
        db.execute('UPDATE users SET is_active = ? WHERE id = ?', (is_active, user_id))
        db.commit()

        action = "активирован" if is_active else "деактивирован"
        SystemLogger.info(
            f'Пользователь {user_id} {action}',
            'auth'
        )

    @staticmethod
    def change_user_role(user_id, new_role):
        """
        Изменение роли пользователя.

        Args:
            user_id (int): ID пользователя
            new_role (str): Новая роль
        """
        db = Database()
        db.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
        db.commit()

        SystemLogger.info(
            f'Роль пользователя {user_id} изменена на {new_role}',
            'auth'
        )