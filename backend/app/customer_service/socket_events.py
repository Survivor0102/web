from flask import request, g, current_app
from flask_socketio import join_room, leave_room, emit
from app import socketio, db
from app.models import User, AgentStatus, ChatSession
from app.utils.auth import token_required
from datetime import datetime
import jwt

# 存储sid到用户ID的映射
socket_users = {}

def get_user_from_token(token):
    """从token获取用户"""
    try:
        # 使用应用配置中的JWT密钥
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except:
        return None

def get_current_user():
    """从socket_users映射获取当前用户"""
    print(f'get_current_user() called - SID: {request.sid}')
    print(f'socket_users映射: {socket_users}')

    # 首先尝试从socket_users映射获取
    if request.sid in socket_users:
        user_id = socket_users[request.sid]
        print(f'在socket_users中找到用户ID: {user_id}')
        user = User.query.get(user_id)
        if user:
            print(f'数据库查询成功: {user.username}(id:{user.id})')
            # 同时设置g.current_user以便其他代码使用
            g.current_user = user
            return user
        else:
            print(f'警告: 数据库中没有找到用户ID {user_id}')

    # 回退到g.current_user
    if hasattr(g, 'current_user') and g.current_user:
        print(f'使用g.current_user: {g.current_user.username}(id:{g.current_user.id})')
        return g.current_user

    print('get_current_user: 未找到用户')
    return None

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    print(f'=== WEBSOCKET CONNECT ===')
    print(f'SID: {request.sid}')
    print(f'Token参数: {request.args.get("token")[:30] if request.args.get("token") else "None"}')
    print(f'请求头: {dict(request.headers)}')

    token = request.args.get('token')
    if not token:
        print('WebSocket连接失败：缺少token')
        return False

    user = get_user_from_token(token)
    if not user:
        print('WebSocket连接失败：无效token')
        return False

    print(f'WebSocket连接成功 - 用户: {user.username}(id:{user.id}, 角色:{user.role})')
    print(f'Socket users映射大小: {len(socket_users)}')

    # 保存用户信息到连接上下文
    g.current_user = user
    # 存储sid到用户ID的映射
    socket_users[request.sid] = user.id
    print(f'已添加到socket_users: {request.sid} -> {user.id}')

    # 用户加入自己的房间，用于接收个人消息
    join_room(f'user_{user.id}')

    if user.is_agent():
        # 客服加入客服相关房间
        join_room(f'agent_{user.id}')
        join_room('agents_all')

        # 更新客服状态
        agent_status = AgentStatus.query.get(user.id)
        if not agent_status:
            agent_status = AgentStatus(user_id=user.id)
            db.session.add(agent_status)

        agent_status.status = 'online'
        agent_status.last_active = datetime.utcnow()
        db.session.commit()

        # 通知其他客服有新客服上线
        emit('agent_online', {
            'agent_id': user.id,
            'username': user.username
        }, room='agents_all', include_self=False)

        print(f'客服 {user.username} 已上线')

    # 用户加入其所有会话的房间
    from app.models import ChatSession
    user_sessions = ChatSession.query.filter(
        (ChatSession.user_id == user.id) |
        (ChatSession.agent_id == user.id)
    ).filter(ChatSession.status.in_(['waiting', 'active'])).all()

    for session in user_sessions:
        join_room(f'session_{session.id}')

    print(f'用户 {user.username} 已连接')
    return True

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    # 从映射中移除用户
    if request.sid in socket_users:
        user_id = socket_users.pop(request.sid)
        user = User.query.get(user_id)

        if user and user.is_agent():
            # 更新客服状态为离线
            agent_status = AgentStatus.query.get(user.id)
            if agent_status:
                agent_status.status = 'offline'
                agent_status.last_active = datetime.utcnow()
                db.session.commit()

            # 通知其他客服该客服已离线
            emit('agent_offline', {
                'agent_id': user.id,
                'username': user.username
            }, room='agents_all', include_self=False)

            print(f'客服 {user.username} 已离线')

        if user:
            print(f'用户 {user.username} 已断开连接')

@socketio.on('join_session')
def handle_join_session(data):
    """加入特定会话房间"""
    user = get_current_user()
    if not user:
        return

    session_id = data.get('session_id')
    if session_id:
        join_room(f'session_{session_id}')
        print(f'用户 {user.username} 加入会话 {session_id}')

@socketio.on('leave_session')
def handle_leave_session(data):
    """离开特定会话房间"""
    user = get_current_user()
    if not user:
        return

    session_id = data.get('session_id')
    if session_id:
        leave_room(f'session_{session_id}')
        print(f'用户 {user.username} 离开会话 {session_id}')

@socketio.on('send_message')
def handle_send_message(data):
    """处理发送消息事件（来自WebSocket）"""
    print('\n' + '='*60)
    print('=== HANDLE SEND MESSAGE EVENT ===')
    print(f'时间: {datetime.utcnow().isoformat()}')
    print(f'SID: {request.sid}')
    print(f'事件数据: {data}')
    print('='*60)

    # 获取当前用户
    user = get_current_user()
    print(f'\n当前用户: {user.username if user else None} (ID: {user.id if user else None})')
    if not user:
        print('❌ WebSocket消息处理失败：无当前用户上下文')
        return

    session_id = data.get('session_id')
    content = data.get('content')
    attachments = data.get('attachments', [])

    print(f'\n解析消息数据:')
    print(f'  会话ID: {session_id}')
    print(f'  内容长度: {len(content) if content else 0}')
    print(f'  内容预览: {content[:100] if content else "None"}')
    print(f'  附件数: {len(attachments)}')

    if not session_id or not content:
        print('❌ WebSocket消息处理失败：缺少会话ID或内容')
        return

    # 权限检查
    from app.models import ChatSession, ChatMessage
    print(f'\n查询会话: {session_id}')
    session = ChatSession.query.get(session_id)
    if not session:
        print(f'❌ 会话不存在: {session_id}')
        return
    else:
        print(f'✅ 找到会话:')
        print(f'  用户ID: {session.user_id}')
        print(f'  客服ID: {session.agent_id}')
        print(f'  状态: {session.status}')

    # 检查用户是否参与该会话
    print(f'\n检查权限:')
    print(f'  当前用户ID: {user.id}')
    print(f'  会话用户ID: {session.user_id}')
    print(f'  会话客服ID: {session.agent_id}')

    if (user.id != session.user_id and
        user.id != session.agent_id):
        print(f'❌ 权限不足: 用户 {user.id} 不是会话 {session_id} 的参与者')
        return
    else:
        print(f'✅ 权限验证通过')

    # 创建消息
    sender_type = 'user' if user.id == session.user_id else 'agent'
    print(f'创建消息 - 会话: {session_id}, 发送者: {user.username}({sender_type}), 内容: {content[:50]}...')
    message = ChatMessage(
        session_id=session_id,
        sender_type=sender_type,
        sender_id=user.id,
        content=content,
        attachments=attachments,
        delivered=True
    )

    db.session.add(message)
    print(f'消息对象已添加到session，消息ID: {message.id}')

    # 更新会话最后消息时间
    session.last_message_at = datetime.utcnow()
    # 只有当有客服分配时才将状态从waiting改为active
    if session.status == 'waiting' and session.agent_id:
        session.status = 'active'
        print(f'[成功] 会话 {session_id} 状态从waiting变为active（已分配客服 {session.agent_id}）')
    elif session.status == 'waiting' and not session.agent_id:
        print(f'[警告] 会话 {session_id} 仍为waiting状态，等待客服分配')
        # 尝试分配客服
        from .services import ChatService
        chat_service = ChatService()
        chat_service.try_assign_agent(session_id)
        # 重新查询会话获取最新状态
        session = ChatSession.query.get(session_id)
        if session.agent_id:
            print(f'[成功] 分配客服成功，客服ID: {session.agent_id}')
            session.status = 'active'
        else:
            print(f'[失败] 暂时无可用客服，会话保持waiting状态')

    try:
        db.session.commit()
        print(f'数据库提交成功，消息已保存，ID: {message.id}')
    except Exception as e:
        print(f'数据库提交失败: {e}')
        db.session.rollback()
        return

    # 广播消息给会话所有参与者
    print(f'广播消息到会话 {session_id}, 发送者: {user.username}({sender_type}), 内容: {content[:50]}...')
    emit('new_message', {
        'session_id': session_id,
        'message': message.to_dict()
    }, room=f'session_{session_id}')
    print(f'已发送消息到房间 session_{session_id}')

    # 如果发送者是用户，发送已读回执给客服
    if sender_type == 'user' and session.agent_id:
        emit('message_read_receipt', {
            'session_id': session_id,
            'message_id': message.id
        }, room=f'agent_{session.agent_id}')

@socketio.on('typing')
def handle_typing(data):
    """处理输入中状态"""
    user = get_current_user()
    if not user:
        return

    session_id = data.get('session_id')
    is_typing = data.get('is_typing', False)

    if session_id:
        # 通知会话其他参与者该用户正在输入
        emit('user_typing', {
            'session_id': session_id,
            'user_id': user.id,
            'username': user.username,
            'is_typing': is_typing
        }, room=f'session_{session_id}', include_self=False)

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """标记消息为已读"""
    user = get_current_user()
    if not user:
        return

    session_id = data.get('session_id')
    message_ids = data.get('message_ids', [])

    if not session_id or not message_ids:
        return

    # 更新消息状态
    from app.models import ChatMessage
    messages = ChatMessage.query.filter(
        ChatMessage.session_id == session_id,
        ChatMessage.id.in_(message_ids),
        ChatMessage.sender_id != user.id  # 不能标记自己发送的消息为已读
    ).all()

    for message in messages:
        message.read_by_recipient = True

    db.session.commit()

    # 通知发送者消息已被阅读
    for message in messages:
        if message.sender_id:
            emit('messages_read', {
                'session_id': session_id,
                'message_ids': [message.id],
                'reader_id': user.id
            }, room=f'user_{message.sender_id}')

@socketio.on('agent_status_update')
def handle_agent_status_update(data):
    """客服状态更新"""
    user = get_current_user()
    if not user or not user.is_agent():
        return

    status = data.get('status')
    if status not in ['online', 'offline', 'away', 'busy']:
        return

    # 更新客服状态
    agent_status = AgentStatus.query.get(user.id)
    if not agent_status:
        agent_status = AgentStatus(user_id=user.id)
        db.session.add(agent_status)

    agent_status.status = status
    agent_status.last_active = datetime.utcnow()
    db.session.commit()

    # 广播状态更新给所有客服
    emit('agent_status_changed', {
        'agent_id': user.id,
        'username': user.username,
        'status': status
    }, room='agents_all')