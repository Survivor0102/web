from functools import wraps
from flask import request, jsonify, g
from app.models import User

def token_required(f):
    """要求有效token的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': '缺少认证token'}), 401

        # 验证token
        user = User.verify_auth_token(token)
        if not user:
            return jsonify({'error': '无效或过期的token'}), 401

        # 将用户信息保存到g对象
        g.current_user = user
        g.token = token

        return f(*args, **kwargs)
    return decorated_function

def require_role(role_name):
    """要求特定角色的装饰器"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return jsonify({'error': '未认证'}), 401

            if not g.current_user.has_role(role_name):
                return jsonify({'error': '权限不足'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_agent_or_admin(f):
    """要求客服或管理员角色的装饰器"""
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({'error': '未认证'}), 401

        if not g.current_user.can_access_agent_console():
            return jsonify({'error': '权限不足'}), 403

        return f(*args, **kwargs)
    return decorated_function