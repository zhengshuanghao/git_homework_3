# 项目结构说明

## 目录结构

```
homework_3/
│
├── app.py                      # Flask主应用文件
├── run.py                      # 启动脚本（带配置检查）
├── config.py                   # 配置管理模块
├── requirements.txt            # Python依赖包
├── config.json.example         # 配置文件示例
├── .env.example               # 环境变量示例（需创建）
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目详细说明文档
├── QUICKSTART.md              # 快速开始指南
├── PROJECT_STRUCTURE.md       # 本文件
│
├── services/                  # 服务层
│   ├── __init__.py
│   ├── iflytek_service.py     # 科大讯飞语音识别服务
│   ├── deepseek_service.py    # DeepSeek LLM服务
│   ├── supabase_service.py    # Supabase数据库服务
│   ├── amap_service.py        # 高德地图服务
│   └── audio_converter.py     # 音频格式转换服务
│
├── templates/                 # HTML模板
│   └── index.html            # 主页面
│
├── static/                    # 静态文件
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       └── app.js            # 前端JavaScript
│
├── database/                  # 数据库相关
│   └── schema.sql            # Supabase数据库表结构
│
└── example/                   # 示例代码
    └── rtasr_llm_demo.py     # 科大讯飞API示例
```

## 核心文件说明

### 后端文件

1. **app.py**: Flask应用主文件
   - 定义所有API路由
   - WebSocket事件处理
   - 服务初始化

2. **config.py**: 配置管理
   - 从环境变量或配置文件读取API密钥
   - 配置保存和加载

3. **services/**: 服务层
   - `iflytek_service.py`: 科大讯飞语音识别WebSocket客户端
   - `deepseek_service.py`: DeepSeek LLM API调用
   - `supabase_service.py`: Supabase数据库操作和用户认证
   - `amap_service.py`: 高德地图API封装
   - `audio_converter.py`: 音频格式转换（WebM转PCM）

### 前端文件

1. **templates/index.html**: 主页面
   - 用户界面布局
   - 模态框（设置、登录、注册）
   - 地图容器

2. **static/css/style.css**: 样式文件
   - 响应式设计
   - 现代化UI样式

3. **static/js/app.js**: 前端逻辑
   - 地图初始化和管理
   - 语音录制和识别
   - API调用
   - WebSocket通信

## 数据流

### 语音识别流程
1. 用户点击录音按钮
2. 浏览器获取麦克风权限
3. MediaRecorder录制音频（WebM格式）
4. 前端转换为PCM格式
5. 通过WebSocket发送到后端
6. 后端转发到科大讯飞API
7. 识别结果返回并显示

### 行程生成流程
1. 用户输入/说出旅行需求
2. 前端发送到 `/api/travel/plan`
3. 后端调用DeepSeek LLM生成计划
4. 解析JSON格式的行程数据
5. 保存到Supabase（如果用户已登录）
6. 前端展示行程和地图标记

### 地图展示流程
1. 从行程数据中提取位置信息
2. 调用高德地图API获取坐标（如果需要）
3. 在地图上添加标记
4. 显示信息窗口

## API接口

### REST API

- `GET /api/config` - 获取配置
- `POST /api/config` - 更新配置
- `POST /api/travel/plan` - 创建旅行计划
- `GET /api/travel/plans` - 获取计划列表
- `GET /api/travel/plan/<id>` - 获取单个计划
- `POST /api/travel/expense` - 添加费用记录
- `POST /api/user/login` - 用户登录
- `POST /api/user/register` - 用户注册

### WebSocket事件

- `connect` - 连接建立
- `start_recording` - 开始录音
- `audio_data` - 发送音频数据
- `stop_recording` - 停止录音
- `recognition_interim` - 实时识别结果
- `recording_result` - 最终识别结果

## 配置管理

### 环境变量（.env）

```env
IFLYTEK_APP_ID=
IFLYTEK_API_KEY=
IFLYTEK_API_SECRET=
AMAP_API_KEY=
DEEPSEEK_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
```

### 配置文件（config.json）

与应用内设置同步，用于持久化存储配置。

## 数据库结构

### travel_plans 表
- 存储用户的旅行计划
- 包含计划数据和元信息

### expenses 表
- 存储费用记录
- 关联到旅行计划

## 部署注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥
2. **环境变量**: 生产环境使用环境变量而非配置文件
3. **HTTPS**: 生产环境应使用HTTPS
4. **CORS**: 根据实际需求配置CORS策略
5. **数据库**: 确保Supabase RLS策略正确配置

## 扩展建议

1. **缓存**: 添加Redis缓存常用数据
2. **队列**: 使用消息队列处理异步任务
3. **日志**: 添加结构化日志记录
4. **监控**: 添加应用性能监控
5. **测试**: 添加单元测试和集成测试




