"""
API контроллер
Предоставляет REST API для интеграции с внешними системами
"""
from flask import Blueprint, jsonify, request, session
from utils.decorators import login_required
from services.knowledge_service import KnowledgeService
from services.nlp_service import NLPService

api_bp = Blueprint('api', __name__)


@api_bp.route('/template/<int:template_id>')
@login_required
def get_template(template_id):
    """Получение шаблона документа"""
    # Здесь будет логика получения шаблона
    return jsonify({
        'success': True,
        'id': template_id,
        'name': 'Договор аренды квартиры',
        'content': 'Шаблон договора...'
    })


@api_bp.route('/knowledge/search', methods=['POST'])
@login_required
def search_knowledge():
    """Поиск в базе знаний"""
    data = request.json
    query = data.get('query', '')
    category = data.get('category')

    results = KnowledgeService.search_knowledge(query, category)

    return jsonify({
        'success': True,
        'results': [kb.to_dict() for kb in results]
    })


@api_bp.route('/nlp/analyze', methods=['POST'])
@login_required
def analyze_text():
    """Анализ текста через NLP"""
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Текст не предоставлен'}), 400

    nlp = NLPService()
    result = nlp.process_query(text)

    return jsonify({
        'success': True,
        **result
    })