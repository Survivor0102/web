from app import db, socketio
from app.models import (
    User, ChatSession, ChatMessage, FAQItem, AgentStatus
)
from datetime import datetime
import re

class ChatService:
    def __init__(self):
        pass

    def match_faq(self, user_message):
        """匹配用户消息与FAQ"""
        # 简单关键词匹配
        faq_items = FAQItem.query.all()

        best_match = None
        best_score = 0

        for faq in faq_items:
            score = self._calculate_match_score(user_message, faq)
            if score > best_score:
                best_score = score
                best_match = faq

        # 设置阈值，比如至少匹配一个关键词
        if best_match and best_score > 0:
            # 更新使用计数
            best_match.usage_count += 1
            db.session.commit()

            return {
                'id': best_match.id,
                'question': best_match.question,
                'answer': best_match.answer
            }

        return None

    def _calculate_match_score(self, message, faq_item):
        """计算消息与FAQ的匹配分数"""
        score = 0

        # 检查关键词
        if faq_item.keywords:
            keywords = [kw.strip() for kw in faq_item.keywords.split(',')]
            for keyword in keywords:
                if keyword and keyword.lower() in message.lower():
                    score += 1

        # 检查问题文本中的关键词
        question_keywords = re.findall(r'\w+', faq_item.question.lower())
        message_words = re.findall(r'\w+', message.lower())

        common_words = set(question_keywords) & set(message_words)
        score += len(common_words) * 0.5  # 每个共同词加0.5分

        return score

    def try_assign_agent(self, session_id):
        """尝试为会话分配客服"""
        print(f'[分配] 尝试为会话 {session_id} 分配客服')
        session = ChatSession.query.get(session_id)
        if not session or session.agent_id:
            print(f'[分配] 会话不存在或已分配客服')
            return

        # 查找合适的客服
        print(f'[分配] 查找可用客服...')
        agent = self._find_available_agent(session.context)
        if agent:
            print(f'[分配] 找到客服 {agent.username}(id:{agent.id})')
            session.agent_id = agent.id
            session.status = 'active'
            db.session.commit()

            # 更新客服会话计数
            agent_status = AgentStatus.query.get(agent.id)
            if agent_status:
                agent_status.current_session_count += 1
                db.session.commit()

            # 通知客服有新会话
            socketio.emit('session_assigned', {
                'session_id': session_id,
                'user_info': session.user.to_dict(),
                'context': session.context
            }, room=f'agent_{agent.id}')
            print(f'[分配] 客服分配成功，已通知客服')
        else:
            print(f'[分配] 未找到可用客服')

    def _find_available_agent(self, context=None):
        """查找可用的客服"""
        print(f'[查找] 开始查找可用客服...')

        # 首先查找在线的客服
        online_agents = AgentStatus.query.filter_by(status='online').all()
        print(f'[查找] AgentStatus表中online状态的客服数: {len(online_agents)}')

        available_agents = []
        for agent_status in online_agents:
            agent = User.query.get(agent_status.user_id)
            print(f'[查找] 检查客服: user_id={agent_status.user_id}, agent={agent}, 会话数={agent_status.current_session_count}, 上限={agent.max_concurrent_sessions if agent else "N/A"}')
            if (agent and
                agent_status.current_session_count < agent.max_concurrent_sessions):
                available_agents.append({
                    'agent': agent,
                    'status': agent_status,
                    'load': agent_status.current_session_count / agent.max_concurrent_sessions
                })
                print(f'[查找] 添加客服 {agent.username} 到可用列表')

        if not available_agents:
            # 尝试查找忙碌但未满的客服
            busy_agents = AgentStatus.query.filter_by(status='busy').all()
            print(f'[查找] AgentStatus表中busy状态的客服数: {len(busy_agents)}')
            for agent_status in busy_agents:
                agent = User.query.get(agent_status.user_id)
                if (agent and
                    agent_status.current_session_count < agent.max_concurrent_sessions):
                    available_agents.append({
                        'agent': agent,
                        'status': agent_status,
                        'load': agent_status.current_session_count / agent.max_concurrent_sessions
                    })

        if not available_agents:
            # 如果AgentStatus表中没有找到，尝试直接从User表中查找客服角色
            print(f'[查找] AgentStatus表中未找到可用客服，尝试从User表查找')
            all_agents = User.query.filter(User.role.in_(['agent', 'admin'])).all()
            print(f'[查找] User表中客服角色用户数: {len(all_agents)}')
            for agent in all_agents:
                # 检查或创建AgentStatus记录
                agent_status = AgentStatus.query.get(agent.id)
                if not agent_status:
                    # 创建默认的AgentStatus记录
                    agent_status = AgentStatus(user_id=agent.id, status='offline', current_session_count=0)
                    db.session.add(agent_status)
                    db.session.commit()
                    print(f'[查找] 为客服 {agent.username} 创建AgentStatus记录')

                if agent_status.current_session_count < agent.max_concurrent_sessions:
                    available_agents.append({
                        'agent': agent,
                        'status': agent_status,
                        'load': agent_status.current_session_count / agent.max_concurrent_sessions
                    })
                    print(f'[查找] 添加客服 {agent.username} 到可用列表（从User表）')

        if not available_agents:
            print(f'[查找] 最终未找到可用客服')
            return None

        # 选择负载最低的客服
        available_agents.sort(key=lambda x: x['load'])
        selected_agent = available_agents[0]['agent']
        print(f'[查找] 选择客服 {selected_agent.username}(id:{selected_agent.id}), 负载: {available_agents[0]["load"]:.2f}')
        return selected_agent

    def transfer_session(self, session_id, to_agent_id):
        """转接会话给其他客服"""
        session = ChatSession.query.get(session_id)
        if not session:
            return False

        to_agent = User.query.get(to_agent_id)
        if not to_agent or not to_agent.is_agent():
            return False

        # 更新原客服会话计数
        if session.agent_id:
            old_agent_status = AgentStatus.query.get(session.agent_id)
            if old_agent_status:
                old_agent_status.current_session_count = max(
                    0, old_agent_status.current_session_count - 1
                )

        # 更新新客服会话计数
        new_agent_status = AgentStatus.query.get(to_agent_id)
        if new_agent_status:
            new_agent_status.current_session_count += 1

        # 更新会话
        session.agent_id = to_agent_id
        session.status = 'active'
        db.session.commit()

        # 创建系统消息
        system_message = ChatMessage(
            session_id=session_id,
            sender_type='system',
            content=f'会话已转接给客服 {to_agent.username}',
            delivered=True
        )
        db.session.add(system_message)
        db.session.commit()

        # 通知相关方
        socketio.emit('session_transferred', {
            'session_id': session_id,
            'from_agent_id': session.agent_id,
            'to_agent_id': to_agent_id
        }, room=f'session_{session_id}')

        socketio.emit('new_session_assigned', {
            'session_id': session_id,
            'user_info': session.user.to_dict(),
            'context': session.context
        }, room=f'agent_{to_agent_id}')

        return True

    def close_session(self, session_id, feedback=None, rating=None):
        """关闭会话"""
        session = ChatSession.query.get(session_id)
        if not session:
            return False

        # 更新会话状态
        session.status = 'closed'
        if feedback:
            session.feedback = feedback
        if rating:
            session.rating = rating

        # 更新客服会话计数
        if session.agent_id:
            agent_status = AgentStatus.query.get(session.agent_id)
            if agent_status:
                agent_status.current_session_count = max(
                    0, agent_status.current_session_count - 1
                )

        db.session.commit()

        # 创建系统消息
        system_message = ChatMessage(
            session_id=session_id,
            sender_type='system',
            content='会话已结束',
            delivered=True
        )
        db.session.add(system_message)
        db.session.commit()

        # 通知会话已结束
        socketio.emit('session_closed', {
            'session_id': session_id
        }, room=f'session_{session_id}')

        return True