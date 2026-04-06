from datetime import datetime
from app import db

class FAQCategory(db.Model):
    __tablename__ = 'faq_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 分类名称
    description = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)  # 排序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    items = db.relationship('FAQItem', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'item_count': self.items.count()
        }

class FAQItem(db.Model):
    __tablename__ = 'faq_items'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('faq_categories.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(200))  # 触发关键词，逗号分隔
    usage_count = db.Column(db.Integer, default=0)  # 使用次数统计
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'question': self.question,
            'answer': self.answer,
            'keywords': self.keywords,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String(32), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 分配的客服

    # 会话状态：waiting（等待分配）、active（进行中）、closed（已结束）、transferred（已转接）
    status = db.Column(db.String(20), default='waiting', nullable=False)

    # 会话上下文
    context = db.Column(db.JSON)  # 触发上下文，如 {page: 'achievement', id: '123'}

    # 会话信息
    title = db.Column(db.String(200))  # 会话标题（自动生成或用户填写）
    rating = db.Column(db.Integer)  # 用户评分 1-5
    feedback = db.Column(db.Text)  # 用户反馈

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        user_info = None
        if self.user:
            user_info = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                # avatar字段可能需要扩展User模型，暂时留空
            }

        agent_info = None
        if self.agent:
            agent_info = {
                'id': self.agent.id,
                'username': self.agent.username,
                'email': self.agent.email,
            }

        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': user_info,
            'agent_id': self.agent_id,
            'agent': agent_info,
            'status': self.status,
            'context': self.context,
            'title': self.title,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'message_count': self.messages.count()
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), db.ForeignKey('chat_sessions.id'), nullable=False)

    # 发送者类型：user（用户）、agent（客服）、system（系统）
    sender_type = db.Column(db.String(10), nullable=False)
    sender_id = db.Column(db.Integer)  # user_id 或 agent_id

    # 消息内容
    content = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.JSON)  # 附件信息列表

    # FAQ关联
    is_faq_answer = db.Column(db.Boolean, default=False)
    faq_item_id = db.Column(db.Integer, db.ForeignKey('faq_items.id'))

    # 消息状态
    read_by_recipient = db.Column(db.Boolean, default=False)
    delivered = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    faq_item = db.relationship('FAQItem')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'content': self.content,
            'attachments': self.attachments,
            'is_faq_answer': self.is_faq_answer,
            'faq_item_id': self.faq_item_id,
            'read_by_recipient': self.read_by_recipient,
            'delivered': self.delivered,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AgentStatus(db.Model):
    __tablename__ = 'agent_status'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.String(20), default='offline')  # offline, online, away, busy
    current_session_count = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('status', uselist=False))

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'status': self.status,
            'current_session_count': self.current_session_count,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

    def can_accept_session(self, max_sessions=5):
        """检查客服是否可以接受新会话"""
        if self.status not in ['online', 'away']:
            return False
        return self.current_session_count < max_sessions

    def update_last_active(self):
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()