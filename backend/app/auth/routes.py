from flask import request, jsonify, g
from app import db
from app.auth import auth_bp
from app.models import User
from app.utils.auth import token_required, require_role

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必填字段: {field}'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400

    # 创建用户
    user = User(
        username=data['username'],
        email=data['email'],
        role='user'  # 默认普通用户
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # 生成token
    token = user.generate_auth_token()

    return jsonify({
        'message': '注册成功',
        'user': user.to_dict(),
        'token': token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '请输入用户名和密码'}), 400

    # 查找用户
    user = User.query.filter_by(username=data['username']).first()

    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成token
    token = user.generate_auth_token()

    return jsonify({
        'message': '登录成功',
        'user': user.to_dict(),
        'token': token
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify({'user': g.current_user.to_dict()})

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    # 在真实应用中，这里可以加入token黑名单等逻辑
    return jsonify({'message': '已登出'})

@auth_bp.route('/create-agent', methods=['POST'])
@token_required
@require_role('admin')  # 只有管理员可以创建客服账户
def create_agent_account():
    """创建客服账户（管理员功能）"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必填字段: {field}'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400

    # 创建客服账户
    user = User(
        username=data['username'],
        email=data['email'],
        role='agent',
        agent_skill_tags=data.get('skill_tags', []),
        agent_status='offline'
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '客服账户创建成功',
        'user': user.to_dict()
    }), 201