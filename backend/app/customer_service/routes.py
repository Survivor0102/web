from flask import request, jsonify, g
from app import db, socketio
from app.customer_service import customer_service_bp
from app.models import (
    User, FAQCategory, FAQItem, ChatSession, ChatMessage, AgentStatus
)
from app.utils.auth import token_required, require_role, require_agent_or_admin
import uuid
from datetime import datetime

# 服务类
from .services import ChatService

chat_service = ChatService()

@customer_service_bp.route('/session/start', methods=['POST'])
@token_required
def start_session():
    """开始新的客服会话"""
    data = request.get_json()
    context = data.get('context', {})  # 会话上下文，如 {page: 'achievement', id: '123'}

    # 生成会话ID
    session_id = str(uuid.uuid4())[:32]

    # 创建会话
    session = ChatSession(
        id=session_id,
        user_id=g.current_user.id,
        status='waiting',
        context=context
    )

    db.session.add(session)
    db.session.commit()

    # 尝试分配客服
    chat_service.try_assign_agent(session_id)

    return jsonify({
        'message': '会话创建成功',
        'session': session.to_dict()
    }), 201

@customer_service_bp.route('/session/<session_id>', methods=['GET'])
@token_required
def get_session(session_id):
    """获取会话信息"""
    session = ChatSession.query.get_or_404(session_id)

    # 权限检查：用户只能查看自己的会话，客服可以查看分配的会话
    if (g.current_user.id != session.user_id and
        g.current_user.id != session.agent_id and
        not g.current_user.is_admin()):
        return jsonify({'error': '权限不足'}), 403

    return jsonify({'session': session.to_dict()})

@customer_service_bp.route('/session/<session_id>/messages', methods=['GET'])
@token_required
def get_session_messages(session_id):
    """获取会话消息历史"""
    print(f'获取会话消息 - 会话ID: {session_id}, 请求用户: {g.current_user.username}')
    session = ChatSession.query.get_or_404(session_id)

    # 权限检查
    # 用户只能查看自己的会话，客服可以查看所有会话（包括等待中的），管理员可以查看所有
    if (g.current_user.id != session.user_id and
        not g.current_user.is_agent() and
        not g.current_user.is_admin()):
        return jsonify({'error': '权限不足'}), 403

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    print(f'查询参数 - page: {page}, per_page: {per_page}')
    messages_query = ChatMessage.query.filter_by(session_id=session_id)\
        .order_by(ChatMessage.created_at.asc())

    # 执行查询
    messages = messages_query.paginate(page=page, per_page=per_page, error_out=False)

    print(f'查询结果 - 找到 {messages.total} 条消息，当前页 {len(messages.items)} 条')
    for i, msg in enumerate(messages.items[:3]):  # 只打印前3条消息的概要
        print(f'  消息{i+1}: ID={msg.id}, 发送者={msg.sender_type}({msg.sender_id}), 内容={msg.content[:30]}...')

    return jsonify({
        'messages': [msg.to_dict() for msg in messages.items],
        'total': messages.total,
        'page': messages.page,
        'per_page': messages.per_page,
        'pages': messages.pages
    })

@customer_service_bp.route('/session/<session_id>/send', methods=['POST'])
@token_required
def send_message(session_id):
    """发送消息到会话"""
    data = request.get_json()
    content = data.get('content')
    attachments = data.get('attachments', [])

    if not content:
        return jsonify({'error': '消息内容不能为空'}), 400

    session = ChatSession.query.get_or_404(session_id)

    # 权限检查：只有会话参与用户可以发送消息
    if (g.current_user.id != session.user_id and
        g.current_user.id != session.agent_id):
        return jsonify({'error': '权限不足'}), 403

    # 创建消息
    message = ChatMessage(
        session_id=session_id,
        sender_type='user' if g.current_user.id == session.user_id else 'agent',
        sender_id=g.current_user.id,
        content=content,
        attachments=attachments
    )

    db.session.add(message)

    # 更新会话最后消息时间
    session.last_message_at = datetime.utcnow()
    # 只有当有客服分配时才将状态从waiting改为active
    if session.status == 'waiting' and session.agent_id:
        session.status = 'active'
        print(f'[成功] 会话 {session_id} 状态从waiting变为active（已分配客服 {session.agent_id}）')
    elif session.status == 'waiting' and not session.agent_id:
        print(f'[警告] 会话 {session_id} 仍为waiting状态，等待客服分配')
        # 尝试分配客服
        chat_service.try_assign_agent(session_id)
        # 重新查询会话获取最新状态
        db.session.refresh(session)
        if session.agent_id:
            print(f'[成功] 分配客服成功，客服ID: {session.agent_id}')
            session.status = 'active'
        else:
            print(f'[失败] 暂时无可用客服，会话保持waiting状态')

    db.session.commit()

    # 通过WebSocket广播消息
    socketio.emit('new_message', {
        'session_id': session_id,
        'message': message.to_dict()
    }, room=f'session_{session_id}')

    # 如果发送者是用户，尝试FAQ匹配
    if g.current_user.id == session.user_id:
        faq_match = chat_service.match_faq(content)
        if faq_match:
            # 创建系统回复
            system_message = ChatMessage(
                session_id=session_id,
                sender_type='system',
                content=faq_match['answer'],
                is_faq_answer=True,
                faq_item_id=faq_match['id']
            )
            db.session.add(system_message)
            db.session.commit()

            # 广播系统回复
            socketio.emit('new_message', {
                'session_id': session_id,
                'message': system_message.to_dict()
            }, room=f'session_{session_id}')

    return jsonify({'message': '消息发送成功', 'message': message.to_dict()})

@customer_service_bp.route('/sessions', methods=['GET'])
@token_required
def get_user_sessions():
    """获取当前用户的会话列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # 根据用户角色返回不同的会话
    if g.current_user.is_agent():
        # 客服可以查看分配给他的会话
        query = ChatSession.query.filter_by(agent_id=g.current_user.id)
    else:
        # 普通用户只能查看自己的会话
        query = ChatSession.query.filter_by(user_id=g.current_user.id)

    # 过滤和排序
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    sessions = query.order_by(ChatSession.last_message_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'sessions': [session.to_dict() for session in sessions.items],
        'total': sessions.total,
        'page': sessions.page,
        'per_page': sessions.per_page
    })

@customer_service_bp.route('/agent/sessions', methods=['GET'])
@require_agent_or_admin
def get_agent_sessions():
    """获取分配给当前客服的会话（客服工作台使用）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # 获取客服分配的会话以及未分配的等待中会话
    sessions = ChatSession.query.filter(
        (ChatSession.agent_id == g.current_user.id) |
        (ChatSession.agent_id.is_(None) & (ChatSession.status == 'waiting'))
    ).filter(ChatSession.status.in_(['waiting', 'active']))\
        .order_by(ChatSession.agent_id.is_(None).asc(),  # 未分配的在前
                  ChatSession.last_message_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'sessions': [session.to_dict() for session in sessions.items],
        'total': sessions.total,
        'page': sessions.page,
        'per_page': sessions.per_page
    })

@customer_service_bp.route('/agent/status', methods=['PUT'])
@require_agent_or_admin
def update_agent_status():
    """更新客服在线状态"""
    data = request.get_json()
    status = data.get('status')

    if status not in ['online', 'offline', 'away', 'busy']:
        return jsonify({'error': '无效的状态值'}), 400

    # 更新客服状态
    agent_status = AgentStatus.query.get(g.current_user.id)
    if not agent_status:
        agent_status = AgentStatus(user_id=g.current_user.id)
        db.session.add(agent_status)

    agent_status.status = status
    agent_status.last_active = datetime.utcnow()
    db.session.commit()

    # 广播状态更新
    socketio.emit('agent_status_update', {
        'agent_id': g.current_user.id,
        'status': status
    }, room='agents_all')

    return jsonify({'message': '状态更新成功', 'status': status})

@customer_service_bp.route('/faq/search', methods=['GET'])
def search_faq():
    """搜索FAQ"""
    query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)

    faq_query = FAQItem.query

    if query:
        # 简单关键词搜索（实际项目可以用全文搜索）
        faq_query = faq_query.filter(
            FAQItem.question.contains(query) |
            FAQItem.keywords.contains(query)
        )

    if category_id:
        faq_query = faq_query.filter_by(category_id=category_id)

    faq_items = faq_query.order_by(FAQItem.usage_count.desc()).limit(20).all()

    return jsonify({
        'items': [item.to_dict() for item in faq_items],
        'count': len(faq_items)
    })

@customer_service_bp.route('/faq/categories', methods=['GET'])
def get_faq_categories():
    """获取FAQ分类"""
    categories = FAQCategory.query.order_by(FAQCategory.order).all()
    return jsonify({'categories': [cat.to_dict() for cat in categories]})

@customer_service_bp.route('/agents/online', methods=['GET'])
def get_online_agents():
    """获取在线客服列表"""
    online_agents = AgentStatus.query.filter_by(status='online').all()

    agents_info = []
    for agent_status in online_agents:
        agent = User.query.get(agent_status.user_id)
        if agent:
            agents_info.append({
                **agent.to_dict(),
                'status': agent_status.status,
                'current_session_count': agent_status.current_session_count
            })

    return jsonify({'agents': agents_info})

@customer_service_bp.route('/session/<session_id>/accept', methods=['POST'])
@require_agent_or_admin
def accept_session(session_id):
    """客服主动接单"""
    session = ChatSession.query.get_or_404(session_id)

    # 检查会话是否已经被分配
    if session.agent_id:
        return jsonify({'error': '会话已被其他客服接单'}), 400

    # 检查会话状态是否为等待中
    if session.status != 'waiting':
        return jsonify({'error': '会话状态不是等待中'}), 400

    # 分配会话给当前客服
    session.agent_id = g.current_user.id
    session.status = 'active'
    session.updated_at = datetime.utcnow()

    # 更新客服会话计数
    agent_status = AgentStatus.query.get(g.current_user.id)
    if not agent_status:
        agent_status = AgentStatus(user_id=g.current_user.id, status='online', current_session_count=0)
        db.session.add(agent_status)

    agent_status.current_session_count += 1

    # 创建系统消息
    system_message = ChatMessage(
        session_id=session_id,
        sender_type='system',
        content=f'会话已被客服 {g.current_user.username} 接单',
        delivered=True
    )
    db.session.add(system_message)
    db.session.commit()

    # 通过WebSocket通知相关方
    socketio.emit('session_accepted', {
        'session_id': session_id,
        'agent_id': g.current_user.id,
        'agent_name': g.current_user.username
    }, room=f'session_{session_id}')

    # 通知客服有新会话分配（给自己）
    socketio.emit('session_assigned', {
        'session_id': session_id,
        'user_info': session.user.to_dict(),
        'context': session.context
    }, room=f'agent_{g.current_user.id}')

    return jsonify({
        'message': '接单成功',
        'session': session.to_dict()
    })

@customer_service_bp.route('/session/<session_id>/transfer', methods=['POST'])
@require_agent_or_admin
def transfer_session(session_id):
    """转接会话给其他客服"""
    data = request.get_json()
    to_agent_id = data.get('to_agent_id')

    if not to_agent_id:
        return jsonify({'error': '缺少目标客服ID'}), 400

    # 检查目标客服是否存在且是客服角色
    to_agent = User.query.get(to_agent_id)
    if not to_agent or not to_agent.is_agent():
        return jsonify({'error': '目标客服不存在或无权限'}), 400

    # 获取当前会话
    session = ChatSession.query.get_or_404(session_id)

    # 权限检查：只有当前负责的客服可以转接会话
    if session.agent_id != g.current_user.id and not g.current_user.is_admin():
        return jsonify({'error': '只能转接自己负责的会话'}), 403

    # 使用ChatService转接会话
    success = chat_service.transfer_session(session_id, to_agent_id)

    if not success:
        return jsonify({'error': '转接失败'}), 400

    return jsonify({
        'message': '转接成功',
        'session': session.to_dict()
    })

@customer_service_bp.route('/session/<session_id>/close', methods=['POST'])
@token_required
def close_session(session_id):
    """关闭会话"""
    data = request.get_json() or {}
    feedback = data.get('feedback')
    rating = data.get('rating')

    session = ChatSession.query.get_or_404(session_id)

    # 权限检查：只有会话参与用户可以关闭会话
    if (g.current_user.id != session.user_id and
        g.current_user.id != session.agent_id and
        not g.current_user.is_admin()):
        return jsonify({'error': '权限不足'}), 403

    # 检查会话是否已经是关闭状态
    if session.status == 'closed':
        return jsonify({'error': '会话已关闭'}), 400

    # 更新会话状态
    session.status = 'closed'
    session.feedback = feedback
    session.rating = rating
    session.updated_at = datetime.utcnow()

    # 如果有关联的客服，减少其当前会话计数
    if session.agent_id:
        agent_status = AgentStatus.query.get(session.agent_id)
        if agent_status and agent_status.current_session_count > 0:
            agent_status.current_session_count -= 1

    db.session.commit()

    # 通过WebSocket通知会话参与者
    socketio.emit('session_closed', {
        'session_id': session_id,
        'closed_by': g.current_user.id
    }, room=f'session_{session_id}')

    return jsonify({
        'message': '会话关闭成功',
        'session': session.to_dict()
    })