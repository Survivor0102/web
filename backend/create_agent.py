#!/usr/bin/env python3
"""
创建客服账户脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models.user import User
import random
import string

def generate_password(length=12):
    """生成随机密码"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_username(base="agent"):
    """生成唯一用户名"""
    with app.app_context():
        # 查找现有的客服用户名
        existing_agents = User.query.filter(User.username.like(f"{base}%")).all()
        existing_numbers = []
        for agent in existing_agents:
            if agent.username.startswith(base):
                try:
                    num = int(agent.username[len(base):])
                    existing_numbers.append(num)
                except ValueError:
                    continue

        # 找到下一个可用的数字
        next_num = 1
        while next_num in existing_numbers:
            next_num += 1

        return f"{base}{next_num:03d}"

def create_agent_account(username=None, email=None, password=None):
    """创建客服账户"""
    with app.app_context():
        # 生成用户名和密码（如果未提供）
        if not username:
            username = generate_username()

        if not email:
            email = f"{username}@example.com"

        if not password:
            password = generate_password()

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            print(f"错误：用户名 '{username}' 已存在")
            return None

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            print(f"错误：邮箱 '{email}' 已存在")
            return None

        # 创建客服账户
        user = User(
            username=username,
            email=email,
            role='agent',
            agent_skill_tags=['成果申报', '项目咨询', '一般咨询'],  # 默认技能标签
            agent_status='offline',
            max_concurrent_sessions=5
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"客服账户创建成功！")
        print(f"用户名: {username}")
        print(f"邮箱: {email}")
        print(f"密码: {password}")
        print(f"角色: agent")
        print(f"技能标签: {user.agent_skill_tags}")
        print(f"最大并发会话数: {user.max_concurrent_sessions}")
        print(f"账户ID: {user.id}")

        return user

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='创建客服账户')
    parser.add_argument('--username', help='指定用户名（不指定则自动生成）')
    parser.add_argument('--email', help='指定邮箱（不指定则自动生成）')
    parser.add_argument('--password', help='指定密码（不指定则自动生成）')

    args = parser.parse_args()

    try:
        create_agent_account(
            username=args.username,
            email=args.email,
            password=args.password
        )
    except Exception as e:
        print(f"创建客服账户失败: {e}")
        sys.exit(1)