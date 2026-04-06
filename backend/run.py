#!/usr/bin/env python3
"""
启动Flask应用
"""
import os
from app import app, db, socketio
from app.models import User, FAQCategory, FAQItem, AgentStatus
import uuid

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功")

        # 检查是否需要初始化数据
        if User.query.count() == 0:
            print("初始化示例数据...")

            # 创建示例FAQ分类
            categories = [
                ('成果申报', '关于成果申报的常见问题'),
                ('创新提交', '关于创新提交的常见问题'),
                ('项目咨询', '关于项目申报的常见问题'),
                ('技术支持', '技术问题咨询'),
                ('一般咨询', '其他一般问题')
            ]

            for name, description in categories:
                category = FAQCategory(name=name, description=description)
                db.session.add(category)

            db.session.commit()

            # 创建示例FAQ项
            faq_items = [
                (1, '如何提交成果？', '请登录后进入"成果中心"页面，点击"上传成果"按钮，填写相关信息并提交。', '提交,成果,上传'),
                (1, '成果审核需要多长时间？', '成果审核通常需要3-5个工作日，具体时间视申报数量而定。', '审核,时间,多久'),
                (2, '创新提交有什么要求？', '创新提交需要详细说明创新点、技术方案和预期效益，建议提供相关证明材料。', '创新,要求,提交'),
                (3, '项目申报流程是什么？', '项目申报流程包括：注册登录 → 填写申报书 → 提交审核 → 专家评审 → 结果公示。', '项目,申报,流程'),
                (4, '网站遇到技术问题怎么办？', '请通过客服系统反馈具体问题，技术团队会尽快处理。', '技术,问题,故障'),
                (5, '如何联系客服？', '您可以在任何页面的右下角点击"在线客服"按钮，或直接访问客服页面。', '联系,客服,帮助')
            ]

            for category_id, question, answer, keywords in faq_items:
                faq = FAQItem(
                    category_id=category_id,
                    question=question,
                    answer=answer,
                    keywords=keywords
                )
                db.session.add(faq)

            db.session.commit()
            print("示例FAQ数据创建成功")

        print(f"数据库位置: {app.config['SQLALCHEMY_DATABASE_URI']}")

def create_test_users():
    """创建测试用户（仅开发环境使用）"""
    with app.app_context():
        # 检查是否已存在测试用户
        if User.query.filter_by(username='testuser').first():
            print("测试用户已存在")
            return

        print("创建测试用户...")

        # 创建普通用户
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('test123')
        db.session.add(user)

        # 创建客服用户
        agent = User(
            username='testagent',
            email='agent@example.com',
            role='agent',
            agent_skill_tags=['成果申报', '项目咨询'],
            agent_status='offline'
        )
        agent.set_password('agent123')
        db.session.add(agent)
        # 刷新以获取agent.id
        db.session.flush()

        # 创建客服状态记录
        agent_status = AgentStatus(user_id=agent.id, status='offline')
        db.session.add(agent_status)

        db.session.commit()
        print("测试用户创建成功:")
        print("  普通用户: testuser / test123")
        print("  客服用户: testagent / agent123")

if __name__ == '__main__':
    # 初始化数据库
    init_database()

    # 创建测试用户（仅开发环境）
    if app.config.get('DEBUG', True):
        create_test_users()

    print(f"\n服务器启动在: http://localhost:5000")
    print("前端地址: http://localhost:3000")
    print("\n按 Ctrl+C 停止服务器")

    # 启动SocketIO服务器
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)