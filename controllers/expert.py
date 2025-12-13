"""
Контроллер панели эксперта
Верификация ответов и управление базой знаний
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from utils.database import Database
from utils.logger import SystemLogger
from services.knowledge_service import KnowledgeService

expert_bp = Blueprint('expert', __name__)


@expert_bp.route('/')
@login_required
@role_required('expert')
def expert_panel():
    """Панель эксперта"""
    db = Database()

    # Неверифицированные сообщения
    unverified_messages = db.execute_all('''
                                         SELECT cm.*,
                                                u.username     as user_name,
                                                u.avatar_color as user_color,
                                                a.name         as assistant_name,
                                                a.icon         as assistant_icon
                                         FROM chat_messages cm
                                                  JOIN users u ON cm.user_id = u.id
                                                  LEFT JOIN assistants a ON cm.assistant_id = a.id
                                         WHERE cm.is_verified = 0
                                         ORDER BY cm.created_at DESC
                                         ''')

    # База знаний
    knowledge_items = KnowledgeService.get_all_knowledge()

    # Статистика
    stats = {
        'unverified_count': len(unverified_messages),
        'knowledge_count': db.execute_one('SELECT COUNT(*) as count FROM knowledge_base')['count'],
        'verified_today': db.execute_one('''
                                         SELECT COUNT(*) as count
                                         FROM chat_messages
                                         WHERE is_verified = 1 AND DATE (created_at) = DATE ('now')
                                         ''')['count']
    }

    return render_template('expert.html',
                           unverified_messages=unverified_messages,
                           knowledge_items=knowledge_items,
                           stats=stats,
                           username=session['username'],
                           role=session['role'])


@expert_bp.route('/message/<int:message_id>/verify', methods=['POST'])
@login_required
@role_required('expert')
def verify_message(message_id):
    """Верификация сообщения"""
    action = request.form.get('action')
    notes = request.form.get('notes', '')

    db = Database()

    if action == 'approve':
        db.execute('''
                   UPDATE chat_messages
                   SET is_verified        = 1,
                       verified_by        = ?,
                       verification_notes = ?,
                       rating             = 5
                   WHERE id = ?
                   ''', (session['user_id'], notes, message_id))
        flash('Ответ одобрен и опубликован', 'success')
    elif action == 'reject':
        db.execute('''
                   UPDATE chat_messages
                   SET is_verified        = 0,
                       verification_notes = ?
                   WHERE id = ?
                   ''', (notes, message_id))
        flash('Ответ отправлен на доработку', 'warning')

    db.commit()
    SystemLogger.info(f'Сообщение {message_id} верифицировано: {action}', 'expert', session['user_id'])

    return redirect(url_for('expert.expert_panel'))


@expert_bp.route('/knowledge/add', methods=['POST'])
@login_required
@role_required('expert')
def add_knowledge():
    """Добавление материала в базу знаний"""
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category')
    source = request.form.get('source')
    icon = request.form.get('icon', '📚')

    if not title or not content:
        flash('Заполните название и содержание', 'danger')
        return redirect(url_for('expert.expert_panel'))

    try:
        KnowledgeService.add_knowledge(
            title, content, category, source, icon,
            uploaded_by=session['user_id'],
            is_verified=True
        )
        flash('Материал добавлен в базу знаний', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении материала: {e}', 'danger')

    return redirect(url_for('expert.expert_panel'))