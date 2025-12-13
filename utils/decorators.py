"""
Декораторы для контроля доступа
Часть подсистемы управления доступом
"""
from functools import wraps
from flask import session, redirect, url_for, flash, g
from utils.database import Database


def login_required(f):
    """
    Декоратор для проверки аутентификации пользователя.
    Если пользователь не авторизован, перенаправляет на страницу входа.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Требуется авторизация', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def role_required(role):
    """
    Декоратор для проверки роли пользователя.
    Проверяет, имеет ли пользователь необходимую роль для доступа.

    Args:
        role (str): Требуемая роль (admin, developer, expert, client)
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Требуется авторизация', 'warning')
                return redirect(url_for('auth.login'))

            db = Database()
            user = db.execute_one('SELECT role FROM users WHERE id = ?',
                                  (session['user_id'],))

            if not user or user['role'] != role:
                flash('Недостаточно прав для выполнения операции', 'danger')
                return redirect(url_for('chat.chat'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator