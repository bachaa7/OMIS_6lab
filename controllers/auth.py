"""
Контроллер аутентификации
Обрабатывает вход, выход и регистрацию пользователей
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
from utils.logger import SystemLogger

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')

        if not username or not password:
            flash('Заполните все поля', 'danger')
            return render_template('login.html')

        # Аутентификация
        success, message, user = AuthService.authenticate(username, password)

        if success and user:
            # Сохраняем данные в сессии
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['avatar_color'] = user.avatar_color

            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('chat.dashboard'))
        else:
            flash(message, 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        role = request.form.get('role', 'client')

        if not username or not email or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('auth.register'))

        # Регистрация
        success, message, user_id = AuthService.register_user(
            username, email, password, role
        )

        if success:
            flash(message + ' Теперь войдите.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    if 'user_id' in session:
        SystemLogger.info(
            f'Пользователь {session.get("username")} вышел из системы',
            'auth',
            session['user_id']
        )

    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))