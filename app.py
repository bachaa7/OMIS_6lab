"""
Главный файл приложения
Юридическая AI-Платформа с виртуальными помощниками

Система состоит из 4 подсистем:
1. Подсистема управления доступом
2. Подсистема помощников
3. Подсистема базы знаний
4. Подсистема NLP и интерфейса
"""

from flask import Flask, render_template, g
from config import config
from utils.database import Database

# Импорт контроллеров (Blueprint)
from controllers.auth import auth_bp
from controllers.admin import admin_bp
from controllers.developer import developer_bp
from controllers.expert import expert_bp
from controllers.chat import chat_bp
from controllers.api import api_bp


def create_app(config_name='development'):
    """
    Фабрика приложений Flask.
    Создаёт и конфигурирует приложение.

    Args:
        config_name (str): Имя конфигурации (development, production)

    Returns:
        Flask: Настроенное приложение
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Регистрация контроллеров (Blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(developer_bp, url_prefix='/developer')
    app.register_blueprint(expert_bp, url_prefix='/expert')
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Обработчики событий приложения
    @app.before_request
    def before_request():
        """Выполняется перед каждым запросом"""
        pass

    @app.teardown_appcontext
    def close_db(error):
        """Закрытие подключения к БД после запроса"""
        db = Database()
        db.close_connection()

    # Главная страница
    @app.route('/')
    def index():
        """Главная страница сайта"""
        db = Database()
        stats = {
            'users': db.execute_one('SELECT COUNT(*) as count FROM users')['count'],
            'assistants': db.execute_one('SELECT COUNT(*) as count FROM assistants')['count']
        }
        return render_template('index.html', stats=stats)

    # Инициализация БД
    with app.app_context():
        db = Database()
        db.init_database()

        # Добавление демо-данных если БД пустая
        users_count = db.execute_one('SELECT COUNT(*) as count FROM users')['count']
        if users_count == 0:
            init_demo_data(db)

    return app


def init_demo_data(db):
    """
    Инициализация демо-данных для тестирования.
    Создаёт тестовых пользователей и помощников.
    """
    from models.user import User

    print("\n📊 Добавляю демо-данные...")

    # Создание тестовых пользователей
    users_data = [
        ('admin', 'admin@example.com', 'admin123', 'admin', '#dc3545'),
        ('developer', 'dev@example.com', 'dev123', 'developer', '#17a2b8'),
        ('expert', 'expert@example.com', 'expert123', 'expert', '#28a745'),
        ('client', 'client@example.com', 'client123', 'client', '#6c757d'),
    ]

    for username, email, password, role, color in users_data:
        try:
            password_hash = User.hash_password(password)
            db.execute('''
                       INSERT
                       OR IGNORE INTO users (username, email, password_hash, role, avatar_color)
                VALUES (?, ?, ?, ?, ?)
                       ''', (username, email, password_hash, role, color))
            print(f"   ✓ Создан пользователь: {username} ({role})")
        except Exception as e:
            print(f"   ✗ Ошибка при создании пользователя {username}: {e}")

    # Создание помощников
    assistants_data = [
        ('Гражданско-правовой помощник', 'Помощник по договорам, сделкам, недвижимости',
         'гражданское право', '🏛️', '#007bff'),
        ('Трудовой помощник', 'Консультации по трудовому праву',
         'трудовое право', '👨‍💼', '#28a745'),
        ('Семейный помощник', 'Вопросы брака, развода, алиментов',
         'семейное право', '👨‍👩‍👧', '#ff6b6b'),
    ]

    for name, desc, specialty, icon, color in assistants_data:
        try:
            db.execute('''
                       INSERT INTO assistants (name, description, specialty, icon, color)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (name, desc, specialty, icon, color))
            print(f"   ✓ Создан помощник: {name}")
        except Exception as e:
            print(f"   ✗ Ошибка при создании помощника {name}: {e}")

    db.commit()
    print("\n✅ Демо-данные успешно добавлены!")
    print("\n" + "=" * 60)
    print("📊 ДОСТУПНЫЕ ПОЛЬЗОВАТЕЛИ:")
    print("   👑 Администратор: admin / admin123")
    print("   👨‍💻 Разработчик: developer / dev123")
    print("   🧑‍⚖️ Эксперт: expert / expert123")
    print("   👤 Клиент: client / client123")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 ЮРИДИЧЕСКАЯ AI-ПЛАТФОРМА")
    print("=" * 60)

    # Создание и запуск приложения
    app = create_app('development')

    print("\n🌐 ОТКРОЙТЕ В БРАУЗЕРЕ")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5555)