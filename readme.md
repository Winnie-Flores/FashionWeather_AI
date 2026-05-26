# FashionWeather AI - 智能天气穿搭助手

基于天气感知与多模态衣橱管理的智能穿搭推荐系统

## 项目简介

FashionWeather AI 是一款融合实时天气感知、多模态图像识别和AI智能推荐的智能穿搭系统。根据用户所在地天气、个人衣橱和风格偏好，自动生成最佳穿搭建议。

## 核心功能

- 🌍 **智能天气感知** - 自动获取本地天气并分析
- 📊 **天气数据可视化** - ECharts图表展示天气变化
- 👕 **智能穿衣推荐** - 根据天气生成穿搭建议
- 📸 **多模态衣橱管理** - 用户上传衣服AI自动识别
- 🤖 **AI穿搭组合** - 自动组合用户衣橱中的衣服
- 💬 **AI聊天助手** - 对话式穿搭咨询

## 技术栈

### 前端
- React 18
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Framer Motion
- ECharts
- Zustand (状态管理)
- Axios (HTTP客户端)

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- JWT认证

### AI能力
- OpenAI API (预留接口)
- DeepSeek API (预留接口)
- GPT-4o Vision (预留接口)

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+
- npm 或 yarn

### 1. 克隆项目

```bash
cd WeatherAI
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 安装后端依赖

```bash
cd ../backend
pip install -r requirements.txt
```

### 4. 配置环境变量（可选）

前端 `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

后端 `.env` (可选):
```env
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
WEATHER_API_KEY=your_weather_api_key
```

### 5. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 运行

### 6. 启动前端

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 运行

### 7. 访问系统

打开浏览器访问 http://localhost:3000

### 8. 测试账号

系统已内置测试账号，可以直接登录体验：

| 用户名 | 密码 | 说明 |
|--------|------|------|
| test | test123 | 测试账号（自动创建）|

## 项目结构

```
WeatherAI/
├── frontend/          # 前端项目 (Next.js)
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── pages/        # Next.js 页面
│   │   │   ├── index.tsx        # 首页
│   │   │   ├── weather.tsx      # 天气详情页
│   │   │   ├── recommend.tsx    # AI推荐页
│   │   │   ├── wardrobe.tsx     # 衣橱管理页
│   │   │   ├── chat.tsx         # AI聊天页
│   │   │   ├── profile.tsx      # 用户中心
│   │   │   ├── login.tsx        # 登录页
│   │   │   └── register.tsx     # 注册页
│   │   ├── services/     # API 服务
│   │   ├── hooks/         # 自定义 Hooks
│   │   ├── types/         # TypeScript 类型
│   │   ├── utils/         # 工具函数
│   │   ├── store/         # 状态管理
│   │   └── styles/        # 全局样式
│   └── public/
│
├── backend/           # 后端项目 (FastAPI)
│   ├── app/
│   │   ├── api/          # API 路由
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── weather.py       # 天气接口
│   │   │   ├── clothes.py       # 衣橱接口
│   │   │   ├── ai.py           # AI推荐接口
│   │   │   └── chat.py         # 聊天接口
│   │   ├── models/       # SQLAlchemy 模型
│   │   │   ├── user.py
│   │   │   ├── clothes.py
│   │   │   ├── outfit.py
│   │   │   ├── chat.py
│   │   │   └── weather.py
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务服务
│   │   │   ├── weather_service.py
│   │   │   └── ai_service.py
│   │   ├── core/         # 核心配置
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   └── main.py       # 应用入口
│   ├── uploads/           # 上传文件目录
│   └── requirements.txt
│
├── docs/              # 文档
└── README.md
```

## API 接口

### 认证接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |

### 天气接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/weather` | 获取当前天气 |
| GET | `/api/weather/forecast` | 获取天气预报 |
| GET | `/api/weather/hourly` | 获取逐时天气 |
| GET | `/api/weather/aqi` | 获取空气质量 |
| GET | `/api/weather/advice` | 获取穿衣建议 |

### 衣橱接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/clothes` | 获取衣服列表 |
| POST | `/api/clothes` | 添加衣服 |
| POST | `/api/clothes/upload` | 上传衣服图片 |
| PUT | `/api/clothes/{id}` | 更新衣服 |
| DELETE | `/api/clothes/{id}` | 删除衣服 |
| POST | `/api/clothes/analyze` | 分析衣服图片 |

### AI接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/ai/recommend` | 获取穿搭推荐 |
| GET | `/api/ai/recommend/today` | 获取今日推荐 |
| GET | `/api/ai/recommend/scenes` | 获取可选场景 |

### 聊天接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/chat` | 发送消息 |
| GET | `/api/chat/history` | 获取聊天历史 |
| DELETE | `/api/chat/history` | 清空聊天历史 |

## 页面说明

| 页面 | 路径 | 功能 |
|------|------|------|
| 首页 | `/` | 天气总览与今日推荐 |
| 天气详情 | `/weather` | 图表分析与预测 |
| AI推荐 | `/recommend` | 今日穿搭推荐 |
| 衣橱管理 | `/wardrobe` | 管理衣服 |
| AI聊天 | `/chat` | AI对话助手 |
| 用户中心 | `/profile` | 偏好设置 |
| 登录 | `/login` | 用户登录 |
| 注册 | `/register` | 用户注册 |

## 功能演示

### 首页
- 显示当前天气信息
- 7日天气预报
- 穿衣建议
- 今日穿搭推荐
- 快捷入口

### 天气详情页
- 温度趋势图表
- 湿度/降雨概率图表
- 穿衣舒适度雷达图
- 空气质量指示
- 紫外线指数

### 衣橱管理
- 上传衣服图片
- AI自动识别分类
- 衣服筛选
- 衣服编辑删除

### AI推荐
- 根据场景选择推荐
- 展示推荐穿搭
- 推荐理由说明
- 穿搭小贴士

### AI聊天
- 对话式交互
- 天气咨询
- 穿搭建议
- 历史记录

## 开发说明

### 添加新的API接口

1. 在 `backend/app/schemas/` 创建 Pydantic 模型
2. 在 `backend/app/models/` 创建 SQLAlchemy 模型
3. 在 `backend/app/api/` 创建路由文件
4. 在 `frontend/src/services/api.ts` 添加前端调用
5. 在 `frontend/src/types/index.ts` 添加类型定义

### 添加新的页面

1. 在 `frontend/src/pages/` 创建页面文件
2. 使用 `Layout` 组件包裹页面内容
3. 添加对应的导航链接

### 添加新的组件

1. 在 `frontend/src/components/` 创建组件文件夹
2. 创建 `index.tsx` 导出组件
3. 在 `frontend/src/components/index.ts` 导出

## 配置说明

### 天气API

系统默认使用模拟数据。如需使用真实天气数据：

1. 注册天气API服务（如 OpenWeatherMap、和风天气）
2. 在 `backend/app/services/weather_service.py` 中实现真实API调用
3. 配置 `WEATHER_API_KEY`

### AI服务

系统预留了AI接口。如需启用：

1. 配置 `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY`
2. 在 `backend/app/services/ai_service.py` 中实现真实API调用

## 部署说明

### 前端部署

```bash
cd frontend
npm run build
npm start
```

### 后端部署

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 使用 PM2 部署后端

```bash
pip install pm2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name weatherai
```



## License

MIT License
