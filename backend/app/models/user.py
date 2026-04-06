from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import jwt
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user', 'agent', 'admin'

    # 客服相关字段
    agent_status = db.Column(db.String(20), default='offline')  # offline, online, away, busy
    agent_skill_tags = db.Column(db.JSON)  # 技能标签列表
    max_concurrent_sessions = db.Column(db.Integer, default=5)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    chat_sessions = db.relationship('ChatSession',
                                    foreign_keys='ChatSession.user_id',
                                    backref='user',
                                    lazy='dynamic')

    assigned_sessions = db.relationship('ChatSession',
                                        foreign_keys='ChatSession.agent_id',
                                        backref='agent',
                                        lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return self.role == role_name

    def is_agent(self):
        return self.has_role('agent') or self.has_role('admin')

    def is_admin(self):
        return self.has_role('admin')

    def can_access_agent_console(self):
        return self.role in ['agent', 'admin']

    def generate_auth_token(self, expires_in=None):
        """生成JWT令牌"""
        from flask import current_app
        if expires_in is None:
            # 从配置获取过期时间，默认为24小时
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            if hasattr(expires_in, 'total_seconds'):
                expires_in = int(expires_in.total_seconds())

        # 正确计算UTC时间戳
        import time
        current_timestamp = int(time.time())  # 使用time.time()获取正确的Unix时间戳
        payload = {
            'user_id': self.id,
            'username': self.username,
            'role': self.role,
            'exp': current_timestamp + expires_in
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except:
            return None

    def to_dict(self):
        """转换为字典，用于JSON响应"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'agent_status': self.agent_status if self.is_agent() else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'