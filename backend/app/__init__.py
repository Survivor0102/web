from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask import Flask
from flask_cors import CORS
from config import config

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # JSON配置：确保正确处理中文字符
    app.config['JSON_AS_ASCII'] = False

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

    # 注册蓝图
    from .auth import auth_bp
    from .customer_service import customer_service_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(customer_service_bp, url_prefix='/api/customer-service')

    # 导入WebSocket事件处理函数（必须在socketio.init_app之后）
    from .customer_service import socket_events

    # 错误处理
    from flask import jsonify

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # 健康检查端点
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy'})

    return app

# 创建默认应用实例
app = create_app()

# 导入模型（确保在db之后导入）
from .models import User, FAQCategory, FAQItem, ChatSession, ChatMessage, AgentStatus

__all__ = [
    'app',
    'db',
    'migrate',
    'socketio',
    'create_app',
    'User',
    'FAQCategory',
    'FAQItem',
    'ChatSession',
    'ChatMessage',
    'AgentStatus'
]