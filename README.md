# 智慧矿山实验室客服系统

基于Vue3 + Flask的实时在线客服系统，支持人工客服与用户实时对话、FAQ智能匹配、客服工作台等功能。

## 项目结构

```
web/
├── frontend/              # Vue3前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 可复用组件
│   │   ├── stores/       # Pinia状态管理
│   │   ├── router/       # 路由配置
│   │   ├── api/          # API封装
│   │   └── main.js       # 应用入口
│   └── package.json
├── backend/              # Flask后端项目
│   ├── app/
│   │   ├── models/       # 数据模型
│   │   ├── auth/         # 认证模块
│   │   ├── customer_service/ # 客服业务模块
│   │   └── utils/        # 工具函数
│   ├── config.py         # 配置文件
│   ├── app.py           # 应用工厂
│   ├── run.py           # 启动脚本
│   └── requirements.txt
├── start_frontend.bat   # 前端启动脚本
├── start_backend.bat    # 后端启动脚本
└── README.md
```

## 功能特点

### 用户端功能
- ✅ 用户注册/登录（JWT认证）
- ✅ 在线客服聊天（WebSocket实时通信）
- ✅ 消息已读/未读状态
- ✅ 输入状态提示（正在输入...）
- ✅ FAQ智能匹配（自动回复常见问题）
- ✅ 多会话管理
- ✅ "需要对接"按钮集成到各页面

### 客服端功能
- ✅ 客服工作台（多会话并行管理）
- ✅ 实时消息推送
- ✅ 会话分配与转接
- ✅ 快捷回复模板
- ✅ FAQ知识库调用
- ✅ 客服在线状态管理
- ✅ 会话统计与监控

### 管理功能
- ✅ 用户角色系统（user/agent/admin）
- ✅ FAQ知识库管理
- ✅ 客服绩效统计（预留）

## 技术栈

### 前端
- **Vue 3** - 前端框架
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Element Plus** - UI组件库
- **Socket.IO Client** - WebSocket通信
- **Axios** - HTTP客户端

### 后端
- **Flask** - Python Web框架
- **Flask-SQLAlchemy** - ORM
- **Flask-SocketIO** - WebSocket支持
- **Flask-Migrate** - 数据库迁移
- **Flask-CORS** - 跨域支持
- **JWT** - 用户认证

## 快速开始

### 1. 环境准备

#### 后端环境
```bash
# 使用Anaconda创建Python环境
conda create -n web python=3.11
conda activate web

# 或直接使用现有的web环境
conda activate web
```

#### 前端环境
确保已安装Node.js (>=16.0.0) 和 npm。

### 2. 启动后端服务器

```bash
# 方法1：使用批处理文件（Windows）
双击 start_backend.bat

# 方法2：手动启动
cd backend
pip install -r requirements.txt
python run.py
```

后端将启动在 `http://localhost:5000`

### 3. 启动前端开发服务器

```bash
# 方法1：使用批处理文件（Windows）
双击 start_frontend.bat

# 方法2：手动启动
cd frontend
npm install
npm run dev
```

前端将启动在 `http://localhost:3000`

### 4. 访问应用

1. 打开浏览器访问 `http://localhost:3000`
2. 使用以下测试账户登录：

   **普通用户：**
   - 用户名: `testuser`
   - 密码: `test123`

   **客服人员：**
   - 用户名: `testagent`
   - 密码: `agent123`

3. 普通用户可以：
   - 点击首页的"需要对接"按钮发起客服咨询
   - 访问"客服中心"页面进行在线聊天

4. 客服人员可以：
   - 访问"客服工作台"管理多个会话
   - 切换在线状态（在线/忙碌/离开/离线）

## API文档

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 客服相关
- `POST /api/customer-service/session/start` - 开始新会话
- `GET /api/customer-service/session/{id}` - 获取会话详情
- `GET /api/customer-service/session/{id}/messages` - 获取会话消息
- `POST /api/customer-service/session/{id}/send` - 发送消息
- `GET /api/customer-service/sessions` - 获取用户会话列表
- `GET /api/customer-service/agent/sessions` - 获取客服会话列表（需客服角色）
- `PUT /api/customer-service/agent/status` - 更新客服状态（需客服角色）

### WebSocket事件
- `connect` - 连接建立
- `send_message` - 发送消息
- `new_message` - 接收新消息
- `typing` - 输入状态通知
- `session_assigned` - 会话分配通知
- `session_transferred` - 会话转接通知

## 数据库设计

### 核心表结构
- **users** - 用户表（含角色字段）
- **chat_sessions** - 客服会话表
- **chat_messages** - 聊天消息表
- **faq_categories** - FAQ分类表
- **faq_items** - FAQ条目表
- **agent_status** - 客服状态表

## 开发说明

### 添加新的FAQ
1. 后端初始化时会创建示例FAQ数据
2. 可以通过数据库管理工具直接添加
3. 未来可以扩展管理界面

### 创建客服账户
目前需要通过代码创建客服账户：
```python
# 在Flask应用中创建客服账户
user = User(
    username='客服用户名',
    email='客服邮箱',
    role='agent',
    agent_skill_tags=['技能1', '技能2']
)
user.set_password('密码')
```

### 扩展管理员功能
系统已预留管理员角色，只需：
1. 将用户角色设置为`admin`
2. 在权限检查处添加`admin`角色判断

## 部署建议

### 生产环境配置
1. 修改 `backend/config.py` 中的安全配置
2. 设置环境变量：
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_URL` (使用PostgreSQL/MySQL)
3. 使用生产级Web服务器（Gunicorn + Nginx）
4. 启用HTTPS

### 数据库迁移
```bash
cd backend
flask db init
flask db migrate -m "迁移描述"
flask db upgrade
```

## 常见问题

### 1. WebSocket连接失败
- 检查后端SocketIO服务器是否正常运行
- 确认前端代理配置正确（vite.config.js）
- 检查防火墙设置

### 2. 数据库问题
- 首次运行会自动创建SQLite数据库
- 确认有数据库文件的写入权限
- 如需重置数据库，删除 `backend/app.db` 文件后重新运行

### 3. 前端依赖安装失败
- 使用淘宝npm镜像：`npm config set registry https://registry.npmmirror.com`
- 清除npm缓存：`npm cache clean --force`

## 项目待完善功能

1. **文件上传** - 支持图片/文件传输
2. **客服评价系统** - 会话结束后用户评分
3. **数据统计面板** - 客服绩效、会话统计
4. **移动端优化** - 更好的移动端体验
5. **通知系统** - 邮件/短信通知集成
6. **多语言支持** - 国际化

## 许可证

MIT License