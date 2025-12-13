"""
Контроллер админ-панели
Управление пользователями, системой и мониторинг
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from utils.database import Database
from utils.logger import SystemLogger
from services.auth_service import AuthService
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@role_required('admin')
def admin_panel():
    """Главная страница админ-панели"""
    db = Database()

    # Получаем всех пользователей
    users = db.execute_all('''
                           SELECT u.*,
                                  (SELECT COUNT(*) FROM chat_messages WHERE user_id = u.id) as messages_count,
                                  (SELECT COUNT(*) FROM assistants WHERE created_by = u.id) as assistants_count
                           FROM users u
                           ORDER BY u.created_at DESC
                           ''')

    # Получаем помощников
    assistants = db.execute_all('SELECT * FROM assistants')

    # Статистика
    stats = {
        'total_users': db.execute_one('SELECT COUNT(*) as count FROM users')['count'],
        'active_users': db.execute_one('SELECT COUNT(*) as count FROM users WHERE is_active = 1')['count'],
        'total_messages': db.execute_one('SELECT COUNT(*) as count FROM chat_messages')['count'],
        'verified_messages': db.execute_one('SELECT COUNT(*) as count FROM chat_messages WHERE is_verified = 1')[
            'count'],
    }

    return render_template('admin.html',
                           users=users,
                           assistants=assistants,
                           stats=stats,
                           current_date=datetime.now(),
                           username=session['username'],
                           role=session['role'])


@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user(user_id):
    """Активация/деактивация пользователя"""
    db = Database()
    user = db.execute_one('SELECT * FROM users WHERE id = ?', (user_id,))

    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('admin.admin_panel'))

    new_status = 0 if user['is_active'] else 1
    AuthService.update_user_status(user_id, new_status)

    action = "активирован" if new_status else "деактивирован"
    flash(f'Пользователь {user["username"]} {action}', 'success')

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Удаление пользователя"""
    db = Database()

    # Нельзя удалить себя
    if user_id == session['user_id']:
        flash('Нельзя удалить свой собственный аккаунт', 'danger')
        return redirect(url_for('admin.admin_panel'))

    user = db.execute_one('SELECT * FROM users WHERE id = ?', (user_id,))
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('admin.admin_panel'))

    try:
        # Удаляем связанные записи
        db.execute('DELETE FROM chat_messages WHERE user_id = ?', (user_id,))
        db.execute('UPDATE assistants SET created_by = NULL WHERE created_by = ?', (user_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()

        SystemLogger.info(f'Пользователь {user["username"]} удален', 'admin', session['user_id'])
        flash(f'Пользователь {user["username"]} успешно удален', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении пользователя: {e}', 'danger')

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def change_user_role(user_id):
    """Изменение роли пользователя"""
    new_role = request.form.get('role')

    if new_role not in ['admin', 'developer', 'expert', 'client']:
        flash('Некорректная роль', 'danger')
        return redirect(url_for('admin.admin_panel'))

    AuthService.change_user_role(user_id, new_role)
    flash(f'Роль пользователя изменена на {new_role}', 'success')

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/logs')
@login_required
@role_required('admin')
def admin_logs():
    """Просмотр системных логов"""
    db = Database()

    # Фильтры
    level = request.args.get('level', '')
    user_id = request.args.get('user_id', '')

    query = '''
            SELECT l.*, u.username, u.avatar_color
            FROM logs l
                     LEFT JOIN users u ON l.user_id = u.id
            WHERE 1 = 1
            '''
    params = []

    if level:
        query += ' AND l.level = ?'
        params.append(level)

    if user_id:
        query += ' AND l.user_id = ?'
        params.append(user_id)

    query += ' ORDER BY l.created_at DESC LIMIT 100'

    logs = db.execute_all(query, params)

    # Статистика логов
    stats = {
        'total_logs': db.execute_one('SELECT COUNT(*) as count FROM logs')['count'],
        'error_logs': db.execute_one("SELECT COUNT(*) as count FROM logs WHERE level = 'ERROR'")['count'],
        'warning_logs': db.execute_one("SELECT COUNT(*) as count FROM logs WHERE level = 'WARNING'")['count'],
        'info_logs': db.execute_one("SELECT COUNT(*) as count FROM logs WHERE level = 'INFO'")['count'],
    }

    users = db.execute_all('SELECT id, username FROM users ORDER BY username')

    return render_template('admin_logs.html',
                           logs=logs,
                           stats=stats,
                           users=users,
                           username=session['username'],
                           role=session['role'])


@admin_bp.route('/create_assistant', methods=['POST'])
@login_required
@role_required('admin')
def create_assistant():
    """Создание нового помощника"""
    from models.assistant import Assistant

    name = request.form.get('name')
    description = request.form.get('description')
    specialty = request.form.get('specialty')
    icon = request.form.get('icon', '⚖️')
    color = request.form.get('color', '#007bff')

    if not name:
        flash('Введите имя помощника', 'danger')
        return redirect(url_for('admin.admin_panel'))

    db = Database()
    try:
        db.execute('''
                   INSERT INTO assistants (name, description, specialty, icon, color, created_by)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (name, description, specialty, icon, color, session['user_id']))

        db.commit()
        SystemLogger.info(f'Создан помощник: {name}', 'admin', session['user_id'])
        flash('Помощник успешно создан', 'success')
    except Exception as e:
        flash(f'Ошибка при создании помощника: {e}', 'danger')

    return redirect(url_for('admin.admin_panel'))