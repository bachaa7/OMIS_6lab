"""
Контроллер панели разработчика
Создание и тестирование помощников
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from utils.database import Database
from utils.logger import SystemLogger

developer_bp = Blueprint('developer', __name__)


@developer_bp.route('/')
@login_required
@role_required('developer')
def developer_panel():
    """Панель разработчика"""
    db = Database()

    # Получаем тесты
    tests = db.execute_all('''
                           SELECT t.*, u.username as creator_name
                           FROM tests t
                                    JOIN users u ON t.created_by = u.id
                           ORDER BY t.created_at DESC
                           ''')

    # Помощники
    assistants = db.execute_all('SELECT * FROM assistants')

    # Статистика тестов
    stats = {
        'total_tests': db.execute_one('SELECT COUNT(*) as count FROM tests')['count'],
        'passed_tests': db.execute_one("SELECT COUNT(*) as count FROM tests WHERE status = 'passed'")['count'],
        'failed_tests': db.execute_one("SELECT COUNT(*) as count FROM tests WHERE status = 'failed'")['count'],
        'pending_tests': db.execute_one("SELECT COUNT(*) as count FROM tests WHERE status = 'pending'")['count'],
        'total_assistants': db.execute_one('SELECT COUNT(*) as count FROM assistants')['count'],
    }

    # NLP статистика
    nlp_stats = {
        'total_queries': db.execute_one('SELECT COUNT(*) as count FROM chat_messages')['count'],
        'high_confidence': db.execute_one('SELECT COUNT(*) as count FROM chat_messages WHERE confidence > 0.7')[
            'count'],
        'avg_confidence': db.execute_one('SELECT AVG(confidence) as avg FROM chat_messages WHERE confidence > 0')[
                              'avg'] or 0,
    }

    return render_template('developer.html',
                           tests=tests,
                           assistants=assistants,
                           stats=stats,
                           nlp_stats=nlp_stats,
                           username=session['username'],
                           role=session['role'])


@developer_bp.route('/create_test', methods=['POST'])
@login_required
@role_required('developer')
def create_test():
    """Создание нового теста"""
    name = request.form.get('name')
    description = request.form.get('description')
    test_type = request.form.get('test_type')
    code = request.form.get('code')
    expected_output = request.form.get('expected_output')

    if not name:
        flash('Введите название теста', 'danger')
        return redirect(url_for('developer.developer_panel'))

    db = Database()
    try:
        db.execute('''
                   INSERT INTO tests (name, description, test_type, code, expected_output, created_by)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (name, description, test_type, code, expected_output, session['user_id']))

        db.commit()
        SystemLogger.info(f'Создан тест: {name}', 'developer', session['user_id'])
        flash('Тест создан', 'success')
    except Exception as e:
        flash(f'Ошибка при создании теста: {e}', 'danger')

    return redirect(url_for('developer.developer_panel'))


@developer_bp.route('/test/<int:test_id>/run')
@login_required
@role_required('developer')
def run_test(test_id):
    """Запуск теста"""
    db = Database()
    test = db.execute_one('SELECT * FROM tests WHERE id = ?', (test_id,))

    if not test:
        flash('Тест не найден', 'danger')
        return redirect(url_for('developer.developer_panel'))

    # Имитация выполнения теста
    import random
    result = random.choice(['passed', 'failed'])
    actual_output = '{"result": "success"}' if result == 'passed' else '{"result": "error"}'

    db.execute('''
               UPDATE tests
               SET status        = ?,
                   actual_output = ?,
                   executed_at   = CURRENT_TIMESTAMP
               WHERE id = ?
               ''', (result, actual_output, test_id))

    db.commit()
    flash(f'Тест "{test["name"]}" выполнен: {result}', 'success' if result == 'passed' else 'warning')

    return redirect(url_for('developer.developer_panel'))


@developer_bp.route('/assistant/create', methods=['POST'])
@login_required
@role_required('developer')
def create_developer_assistant():
    """Создание помощника разработчиком"""
    name = request.form.get('name')
    description = request.form.get('description')
    specialty = request.form.get('specialty')
    icon = request.form.get('icon', '🤖')
    color = request.form.get('color', '#17a2b8')

    if not name:
        flash('Введите имя помощника', 'danger')
        return redirect(url_for('developer.developer_panel'))

    db = Database()
    try:
        db.execute('''
                   INSERT INTO assistants (name, description, specialty, icon, color, created_by)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (name, description, specialty, icon, color, session['user_id']))

        db.commit()
        SystemLogger.info(f'Создан помощник: {name}', 'developer', session['user_id'])
        flash('Помощник создан', 'success')
    except Exception as e:
        flash(f'Ошибка при создании помощника: {e}', 'danger')

    return redirect(url_for('developer.developer_panel'))