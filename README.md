# AI旅行规划师

基于AI的智能旅行规划Web应用，支持文字和语音输入，自动生成个性化旅行计划。

## 核心功能

- **智能行程规划**：AI生成详细旅行路线，包含交通、住宿、景点、餐厅推荐
- **旅游偏好设置**：保存个人旅行偏好，生成更符合需求的计划
- **费用记录管理**：记录和统计旅行开销，支持关联具体计划
- **语音输入**：支持语音输入旅行需求
- **地图展示**：高德地图展示行程路线和景点位置
- **用户系统**：注册登录，云端保存所有数据

## 技术栈

- **后端**: Flask + Flask-SocketIO
- **前端**: HTML5 + CSS3 + JavaScript
- **AI**: 火山方舟 DeepSeek API
- **语音**: 科大讯飞实时语音识别
- **地图**: 高德地图API
- **数据库**: Supabase (PostgreSQL)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 火山方舟 DeepSeek API
ARK_API_KEY=your_ark_api_key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DEEPSEEK_MODEL=your_endpoint_id

# 科大讯飞语音识别
SPEECH_APP_ID=your_app_id
SPEECH_ACCESS_KEY=your_access_key
SPEECH_SECRET_KEY=your_secret_key

# 高德地图
AMAP_API_KEY=your_amap_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Flask
FLASK_SECRET_KEY=your_secret_key
```

### 3. 初始化数据库

在Supabase SQL编辑器中执行 `database/schema.sql` 文件。

**重要**：如果遇到RLS错误，执行：

```sql
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 4. 启动应用

```bash
python run.py
```

或使用快捷方式：`快速启动.bat`

访问：`http://localhost:8080`

## 使用说明

### 1. 注册/登录
- 首次访问会看到欢迎页面
- 点击"注册"创建账号
- 登录后进入主应用界面

### 2. 设置旅游偏好（推荐）
- 点击"⚙️ 偏好设置"
- 选择旅行风格、住宿类型、饮食偏好等
- 保存后，AI会根据偏好生成更个性化的计划

### 3. 生成旅行计划
- **文字输入**：输入"我想去北京3天，预算5000元"
- **语音输入**：点击麦克风按钮，说出需求
- 点击"生成旅行计划"
- 查看地图和详细行程

### 4. 记录费用
- 点击"💰 费用记录"
- 选择关联的旅行计划（可选）
- 添加费用金额、类别、描述
- 查看费用汇总和统计

### 5. 管理计划
- 在"我的旅行计划"列表中查看所有计划
- 点击计划查看详情
- 点击🗑️按钮删除不需要的计划

## 项目结构

```
homework_3/
├── app.py                    # Flask主应用
├── config.py                 # 配置管理
├── run.py                    # 启动脚本
├── requirements.txt          # Python依赖
├── .env                      # 环境变量（需自行创建）
├── 快速启动.bat              # Windows快速启动
├── database/
│   └── schema.sql           # 数据库结构
├── services/                # 服务层
│   ├── deepseek_service.py  # AI生成服务
│   ├── speech_recognition_service.py  # 语音识别
│   ├── supabase_service.py  # 数据库服务
│   ├── amap_service.py      # 地图服务
│   ├── preference_service.py # 偏好设置服务
│   └── expense_service.py   # 费用记录服务
├── templates/               # HTML模板
│   ├── landing.html         # 欢迎页
│   └── app.html             # 主应用页
└── static/                  # 静态资源
    ├── css/
    │   ├── landing.css
    │   └── style.css
    └── js/
        ├── landing.js
        ├── app.js
        └── audio-recorder.js
```

## 常见问题

### 1. RLS策略错误
如果遇到"new row violates row-level security policy"错误：

```sql
-- 在Supabase SQL编辑器执行
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 2. 语音识别问题
- 必须使用 `http://localhost:8080` 或 HTTPS
- 检查浏览器麦克风权限
- 关闭其他占用麦克风的应用
- 推荐使用Chrome浏览器

### 3. API配置
确保所有API密钥已正确配置在 `.env` 文件中：
- 火山方舟DeepSeek API（必需）
- 科大讯飞语音识别（语音功能必需）
- 高德地图API（地图功能必需）
- Supabase配置（数据存储必需）

## 注意事项

- **安全**：不要将 `.env` 文件提交到代码库
- **浏览器**：推荐使用Chrome、Firefox、Edge等现代浏览器
- **端口**：默认8080端口，如占用可在 `run.py` 中修改

## 许可证

本项目仅供学习和研究使用。

