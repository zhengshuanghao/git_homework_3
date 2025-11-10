# 项目结构说明

本文档描述了AI旅行规划师项目的整理后目录结构。

## 📁 项目结构

```
homework_3/
├── 📄 核心文件
│   ├── app.py                          # Flask主应用（WebSocket服务器）
│   ├── config.py                       # 配置管理（环境变量、API密钥）
│   ├── run.py                          # 应用启动脚本
│   ├── requirements.txt                # Python依赖列表
│   ├── .env                            # 环境变量配置（API密钥）
│   ├── .gitignore                      # Git忽略文件列表
│   └── config.json.example             # 配置文件示例
│
├── 📂 services/                        # 服务层（业务逻辑）
│   ├── __init__.py                     # 包初始化文件
│   ├── doubao_service.py               # 豆包实时语音大模型服务 ⭐
│   ├── doubao_wrapper.py               # 豆包同步包装器（Flask集成）
│   ├── deepseek_service.py             # DeepSeek LLM服务（行程规划）
│   ├── supabase_service.py             # Supabase数据库服务
│   └── amap_service.py                 # 高德地图服务
│
├── 📂 templates/                       # HTML模板
│   └── index.html                      # 主页模板
│
├── 📂 static/                          # 静态资源
│   ├── 📂 css/
│   │   └── style.css                   # 主样式表
│   └── 📂 js/
│       ├── app.js                      # 主JavaScript（UI交互）
│       └── doubao-audio.js             # 豆包音频处理模块 ⭐
│
├── 📂 database/                        # 数据库
│   └── schema.sql                      # Supabase数据库架构
│
└── 📚 文档
    ├── README.md                       # 项目主文档 ⭐
    ├── DOUBAO_INTEGRATION_GUIDE.md     # 豆包集成指南 ⭐
    └── SWITCH_TO_DOUBAO_COMPLETE.md    # 切换到豆包的总结 ⭐
```

## 📝 文件说明

### 核心应用文件

#### `app.py`
- Flask主应用
- WebSocket服务器（Socket.IO）
- 路由定义
- 事件处理（语音对话、旅行规划）

#### `config.py`
- 配置管理类
- 从`.env`加载环境变量
- 支持JSON配置文件
- API密钥管理

#### `run.py`
- 应用启动脚本
- 配置加载
- 服务器启动（http://localhost:8080）

#### `.env`
- 环境变量配置文件
- 包含所有API密钥：
  - `DOUBAO_APP_ID` - 豆包应用ID
  - `DOUBAO_ACCESS_KEY` - 豆包访问密钥
  - `DOUBAO_SECRET_KEY` - 豆包密钥
  - `AMAP_API_KEY` - 高德地图密钥
  - `DEEPSEEK_API_KEY` - DeepSeek API密钥
  - `SUPABASE_URL` - Supabase数据库URL
  - `SUPABASE_KEY` - Supabase API密钥

#### `requirements.txt`
- Python依赖包列表
- 主要依赖：
  - Flask - Web框架
  - Flask-SocketIO - WebSocket支持
  - websockets - 异步WebSocket客户端（豆包）
  - pyaudio - 音频处理
  - supabase - 数据库客户端
  - openai - LLM API
  - pydub - 音频转换

### 服务层（services/）

#### `doubao_service.py` ⭐ 核心
- 豆包实时语音大模型API客户端
- WebSocket通信
- 异步音频/文本处理
- 实时双向对话

#### `doubao_wrapper.py`
- 豆包服务的同步包装器
- 管理异步事件循环
- 提供同步接口给Flask
- 音频队列管理

#### `deepseek_service.py`
- DeepSeek大语言模型API
- 旅行行程规划
- AI对话生成

#### `supabase_service.py`
- Supabase数据库服务
- 用户认证（登录/注册）
- 旅行计划存储
- 费用记录管理

#### `amap_service.py`
- 高德地图API服务
- 地理位置查询
- 路线规划

### 前端文件（templates/ & static/）

#### `templates/index.html`
- 主页HTML模板
- UI结构
- 引入CSS和JavaScript

#### `static/css/style.css`
- 主样式表
- 响应式设计
- UI美化

#### `static/js/app.js`
- 主JavaScript文件
- UI交互逻辑
- Socket.IO客户端
- 旅行规划功能

#### `static/js/doubao-audio.js` ⭐ 新增
- 豆包音频处理模块
- 实时流式录音
- PCM音频播放
- 音频队列管理
- 打断功能

### 数据库（database/）

#### `schema.sql`
- Supabase数据库表结构
- `travel_plans` - 旅行计划表
- `expenses` - 费用记录表
- Row Level Security (RLS) 策略

### 文档（📚）

#### `README.md` ⭐ 主文档
- 项目介绍
- 功能特性
- 安装配置
- 使用说明
- API文档
- 故障排查

#### `DOUBAO_INTEGRATION_GUIDE.md` ⭐ 集成指南
- 豆包API集成详细步骤
- 前端修改指南
- 使用说明
- 测试步骤
- 常见问题

#### `SWITCH_TO_DOUBAO_COMPLETE.md` ⭐ 切换总结
- 从科大讯飞切换到豆包的完整说明
- 已完成的工作
- 快速开始
- 豆包 vs 科大讯飞对比

## 🎯 核心功能模块

### 1. 实时语音对话（豆包）⭐ 新功能

**文件：**
- `services/doubao_service.py`
- `services/doubao_wrapper.py`
- `static/js/doubao-audio.js`

**功能：**
- 端到端实时语音大模型
- 语音识别 + AI对话 + 语音合成一体化
- 实时双向对话
- 支持打断

### 2. 旅行规划

**文件：**
- `services/deepseek_service.py`
- `app.py` (路由: `/api/travel/plan`)

**功能：**
- AI生成旅行行程
- 智能推荐
- 多日行程规划

### 3. 地图服务

**文件：**
- `services/amap_service.py`
- `static/js/app.js` (地图初始化)

**功能：**
- 地图显示
- 位置标记
- 路线规划

### 4. 用户管理

**文件：**
- `services/supabase_service.py`
- `app.py` (路由: `/api/user/*`)

**功能：**
- 用户注册/登录
- 行程保存
- 云端同步

## 🚀 启动应用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
编辑 `.env` 文件，填入您的API密钥。

### 3. 启动服务器
```bash
python run.py
```

### 4. 访问应用
打开浏览器访问：`http://localhost:8080`

## 🔧 开发说明

### 添加新功能

1. **后端服务**：在 `services/` 创建新的服务类
2. **路由**：在 `app.py` 添加新的路由
3. **前端**：在 `static/js/app.js` 添加交互逻辑

### 调试

- **后端**：查看控制台日志
- **前端**：打开浏览器开发者工具（F12）
- **WebSocket**：查看Network标签的WS连接

### 测试

- **语音对话**：打开应用，点击"开始录音"
- **旅行规划**：输入旅行需求，点击"生成旅行计划"

## 📦 依赖说明

### 核心依赖

- **Flask 3.0.0** - Web框架
- **Flask-SocketIO 5.3.6** - WebSocket支持
- **websockets 12.0** - 异步WebSocket（豆包）⭐
- **pyaudio >= 0.2.13** - 音频处理 ⭐
- **supabase 2.3.4** - 数据库
- **openai 1.12.0** - LLM API
- **pydub 0.25.1** - 音频转换

### 工具依赖

- **python-dotenv 1.0.0** - 环境变量管理
- **requests 2.31.0** - HTTP请求

## 📖 相关文档

### 必读文档

1. **README.md** - 项目主文档
2. **DOUBAO_INTEGRATION_GUIDE.md** - 豆包集成指南
3. **SWITCH_TO_DOUBAO_COMPLETE.md** - 切换到豆包的说明

### API文档

- [豆包API文档](https://www.volcengine.com/docs/6561/1221095)
- [高德地图API](https://lbs.amap.com/)
- [DeepSeek API](https://platform.deepseek.com/)
- [Supabase文档](https://supabase.com/docs)

## 🎉 主要特性

### ✨ 新增功能（豆包）

- ✅ 端到端实时语音对话
- ✅ AI语音助手
- ✅ 实时双向交互
- ✅ 支持打断
- ✅ 高质量语音合成

### 📱 原有功能

- ✅ 智能行程规划
- ✅ 地图可视化
- ✅ 用户管理
- ✅ 云端同步
- ✅ 费用管理

## 🔒 安全注意事项

1. **不要提交 `.env` 文件到Git**
2. **API密钥保密**
3. **生产环境使用HTTPS**
4. **配置Supabase RLS策略**

## 🐛 常见问题

### 1. 无法启动服务器

- 检查端口8080是否被占用
- 检查Python版本（需要3.8+）
- 检查依赖是否安装

### 2. 语音对话无法使用

- 检查豆包API密钥是否正确
- 检查网络连接
- 检查麦克风权限

### 3. PyAudio安装失败

- Windows: 使用 `pip install pipwin && pipwin install pyaudio`
- 或下载预编译wheel文件

## 📞 技术支持

如有问题，请查看：
1. README.md 的故障排查部分
2. DOUBAO_INTEGRATION_GUIDE.md 的常见问题部分
3. 控制台日志

---

**最后更新：** 2025-11-10
**版本：** 2.0（豆包实时语音版）




