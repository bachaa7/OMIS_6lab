"""
Контроллер чата с помощниками
Основной интерфейс взаимодействия пользователей с системой
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.decorators import login_required
from utils.database import Database
from services.nlp_service import NLPService
from models.message import Message
from models.assistant import Assistant
from datetime import datetime

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/dashboard')
@login_required
def dashboard():
    """Главная панель - перенаправление по ролям"""
    role = session.get('role', 'client')

    if role == 'admin':
        return redirect(url_for('admin.admin_panel'))
    elif role == 'developer':
        return redirect(url_for('developer.developer_panel'))
    elif role == 'expert':
        return redirect(url_for('expert.expert_panel'))
    else:
        return redirect(url_for('chat.chat'))


@chat_bp.route('/chat')
@login_required
def chat():
    """Страница чата с помощником"""
    db = Database()

    # Получаем список помощников
    assistants_rows = db.execute_all(
        'SELECT * FROM assistants WHERE is_active = 1'
    )
    assistants = [Assistant.from_db_row(row) for row in assistants_rows]

    # Получаем последние сообщения пользователя
    messages = db.execute_all('''
                              SELECT cm.*,
                                     a.name  as assistant_name,
                                     a.icon  as assistant_icon,
                                     a.color as assistant_color
                              FROM chat_messages cm
                                       LEFT JOIN assistants a ON cm.assistant_id = a.id
                              WHERE cm.user_id = ?
                              ORDER BY cm.created_at DESC LIMIT 10
                              ''', (session['user_id'],))

    return render_template('chat.html',
                           username=session['username'],
                           role=session['role'],
                           avatar_color=session.get('avatar_color', '#007bff'),
                           assistants=assistants,
                           messages=messages)


@chat_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    """API для отправки сообщения в чат"""
    data = request.json
    message_text = data.get('message', '').strip()
    assistant_id = data.get('assistant_id')

    if not message_text:
        return jsonify({'error': 'Сообщение пустое'}), 400

    # Обработка NLP
    nlp = NLPService()
    nlp_result = nlp.process_query(message_text)

    # Сохранение в БД
    db = Database()
    cursor = db.execute('''
                        INSERT INTO chat_messages (user_id, assistant_id, message, response, intent, category,
                                                   confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            session['user_id'],
                            assistant_id,
                            message_text,
                            nlp_result['response'],
                            nlp_result['intent'],
                            nlp_result['category'],
                            nlp_result['confidence']
                        ))

    db.commit()
    message_id = cursor.lastrowid

    return jsonify({
        'success': True,
        'message_id': message_id,
        'response': nlp_result['response'],
        'intent': nlp_result['intent'],
        'category': nlp_result['category'],
        'confidence': nlp_result['confidence'],
        'icon': nlp_result.get('icon', '⚖️'),
        'timestamp': nlp_result['timestamp']
    })


@chat_bp.route('/history')
@login_required
def history():
    """История консультаций"""
    db = Database()
    messages = db.execute_all('''
                              SELECT cm.*,
                                     a.name  as assistant_name,
                                     a.icon  as assistant_icon,
                                     a.color as assistant_color
                              FROM chat_messages cm
                                       LEFT JOIN assistants a ON cm.assistant_id = a.id
                              WHERE cm.user_id = ?
                              ORDER BY cm.created_at DESC
                              ''', (session['user_id'],))

    return render_template('history.html',
                           messages=messages,
                           username=session['username'],
                           role=session['role'])