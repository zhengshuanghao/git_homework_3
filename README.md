# AI旅行规划师 (AI Travel Planner)

一个基于Web的智能旅行规划应用，通过AI理解用户需求，自动生成详细的旅行路线和建议，并提供实时旅行辅助。

## 功能特性

### 核心功能

1. **智能行程规划**
   - 支持文字和语音输入旅行需求
   - 自动生成个性化旅行路线
   - 包含交通、住宿、景点、餐厅等详细信息

2. **费用预算与管理**
   - AI预算分析
   - 费用记录和跟踪
   - 支持语音输入费用

3. **用户管理与数据存储**
   - 用户注册登录系统
   - 云端行程同步
   - 多设备访问支持

## 技术栈

- **后端**: Python Flask + Flask-SocketIO
- **前端**: HTML5 + CSS3 + JavaScript
- **语音识别**: 科大讯飞实时语音识别API
- **地图服务**: 高德地图API
- **数据库**: Supabase (PostgreSQL)
- **AI服务**: DeepSeek LLM API

## 安装和配置

### 1. 环境要求

- Python 3.8+
- pip
- FFmpeg（用于音频格式转换，pydub依赖）
  
  **Windows**: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)，将ffmpeg.exe添加到系统PATH
  
  **macOS**: `brew install ffmpeg`
  
  **Linux**: `sudo apt-get install ffmpeg` 或 `sudo yum install ffmpeg`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

#### 方式一：使用环境变量（推荐）

创建 `.env` 文件（参考 `.env.example`）：

```env
# 科大讯飞语音识别API
IFLYTEK_APP_ID=c80a4c00
IFLYTEK_API_KEY=be6071e8028efa1bac85a18023221559
IFLYTEK_API_SECRET=OTcyNDQ5ZTI0MjUzNDg0ZTUxODViNjcw

# 高德地图API
AMAP_API_KEY=62b0a02ed7213d7753d65007051c0c6f
AMAP_API_SECRET=66a262e19c64cdc1109b2c70dd89fee0

# DeepSeek LLM API
DEEPSEEK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Supabase配置
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# Flask配置
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

#### 方式二：使用应用内设置

启动应用后，点击右上角"设置"按钮，在设置页面中输入API密钥。

### 4. 配置Supabase数据库

在Supabase中创建以下表：

#### travel_plans 表

```sql
CREATE TABLE travel_plans (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    user_input TEXT,
    plan_data JSONB,
    destination TEXT,
    duration TEXT,
    budget NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_travel_plans_user_id ON travel_plans(user_id);
```

#### expenses 表

```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    plan_id INTEGER REFERENCES travel_plans(id),
    expense_data JSONB,
    amount NUMERIC,
    category TEXT,
    description TEXT,
    date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_plan_id ON expenses(plan_id);
```

#### 启用Row Level Security (RLS)

```sql
-- 启用RLS
ALTER TABLE travel_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许用户访问自己的数据）
CREATE POLICY "Users can view own plans" ON travel_plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own plans" ON travel_plans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own expenses" ON expenses
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 5. 运行应用

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

应用将在 `http://localhost:8080` 启动。

**注意**: 如果遇到端口占用问题，可以修改 `app.py` 或 `run.py` 中的端口号。

## 使用说明

### 1. 配置API密钥

首次使用前，请先在设置页面配置所有必需的API密钥：
- 科大讯飞API（语音识别）
- 高德地图API（地图服务）
- DeepSeek API（AI行程规划）
- Supabase配置（用户认证和数据存储）

### 2. 创建旅行计划

#### 文字输入
1. 选择"文字输入"模式
2. 在文本框中输入旅行需求，例如："我想去日本，5天，预算1万元，喜欢美食和动漫，带孩子"
3. 点击"生成旅行计划"按钮

#### 语音输入
1. 选择"语音输入"模式
2. 点击"点击开始录音"按钮
3. 说出你的旅行需求
4. 点击"停止"按钮
5. 系统会自动识别语音并生成计划

### 3. 查看行程

生成的旅行计划会显示在右侧：
- 地图上标记了所有景点和地点
- 左侧显示详细的行程安排
- 包含每日活动、费用、建议等信息

### 4. 用户功能

- **注册/登录**: 保存和管理多份旅行计划
- **我的计划**: 查看历史旅行计划
- **费用管理**: 记录和管理旅行开销

## 项目结构

```
homework_3/
├── app.py                 # Flask主应用
├── config.py              # 配置管理
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略文件
├── README.md             # 项目说明
├── services/             # 服务层
│   ├── __init__.py
│   ├── iflytek_service.py    # 科大讯飞语音识别
│   ├── deepseek_service.py   # DeepSeek LLM
│   ├── supabase_service.py   # Supabase数据库
│   └── amap_service.py       # 高德地图
├── templates/            # HTML模板
│   └── index.html
└── static/              # 静态文件
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## API说明

### 后端API

- `GET /api/config` - 获取配置
- `POST /api/config` - 更新配置
- `POST /api/travel/plan` - 创建旅行计划
- `GET /api/travel/plans` - 获取旅行计划列表
- `GET /api/travel/plan/<plan_id>` - 获取单个旅行计划
- `POST /api/travel/expense` - 添加费用记录
- `POST /api/user/login` - 用户登录
- `POST /api/user/register` - 用户注册

### WebSocket事件

- `start_recording` - 开始录音
- `audio_data` - 发送音频数据
- `stop_recording` - 停止录音
- `recognition_interim` - 实时识别结果
- `recording_result` - 最终识别结果

## 注意事项

1. **API密钥安全**
   - 不要将API密钥提交到公开代码库
   - 使用 `.env` 文件或应用内设置管理密钥
   - 确保 `.env` 文件在 `.gitignore` 中

2. **浏览器兼容性**
   - 需要支持WebSocket和MediaRecorder API
   - 推荐使用Chrome、Firefox、Edge等现代浏览器

3. **语音识别**
   - 需要浏览器麦克风权限
   - 建议在安静环境中使用
   - 支持中文识别

4. **地图服务**
   - 高德地图API需要配置正确的域名白名单
   - 免费版有调用次数限制

## 开发说明

### 添加新功能

1. 在 `services/` 目录下创建新的服务类
2. 在 `app.py` 中注册路由
3. 在前端 `static/js/app.js` 中添加相应的交互逻辑

### 调试

- 后端日志会输出到控制台
- 前端使用浏览器开发者工具查看日志
- 检查网络请求和WebSocket连接状态

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交Issue。

## 故障排查与补充文档

下面是从项目其它文档合并的常见问题与解决步骤（已合并为最终文档）。

### 语音 / 麦克风 问题

- 浏览器必须在安全上下文下才能访问麦克风：使用 `http://localhost:8080` 或 `https://`，不要直接使用局域网 IP（除非已配置 HTTPS）。
- 检查浏览器麦克风权限（地址栏锁图标），并允许麦克风访问。
- 关闭其他可能占用麦克风的应用（Zoom、Teams、微信、系统录音等）。
- Windows: 检查“设置 → 隐私 → 麦克风”，允许桌面应用访问麦克风。
- 如果遇到 `NotReadableError` / `NotAllowedError` 等，尝试换浏览器或重启浏览器/电脑。
- 调试脚本（在浏览器 Console 中运行）：

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => { stream.getTracks().forEach(t => t.stop()); console.log('Microphone OK'); })
    .catch(err => console.error('Microphone error:', err));
```

### Supabase 连接问题

- 如果 Supabase 初始化失败，常见原因是 `supabase-py` 与依赖版本不匹配。尝试安装受支持的版本：

```bash
pip uninstall supabase -y
pip install supabase==2.3.4
```

- 如果仍异常，建议在虚拟环境中重新安装依赖：

```powershell
# Windows
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

- 提示性测试脚本（`test_supabase.py` 已包含在仓库）可用于本地验证：

```bash
python test_supabase.py
```

### SSL / DeepSeek (Ark) 连接问题

- 如果在调用火山方舟（Ark）API时遇到 SSL 握手超时或 EOF 错误（例如 `_ssl.c:1000`），可能是本地 CA 不完整、网络中间件拦截（公司防火墙）或 SDK TLS 配置有问题。
- 调试步骤：
    1. 升级证书包：`pip install --upgrade certifi`
    2. 在本地临时禁用 SSL 验证（仅用于排查）：在 PowerShell 设置环境变量 ` $env:DISABLE_SSL_VERIFY = '1' ` 然后运行应用；如果禁用后能成功，说明是证书/中间件问题。
    3. 使用 `certifi.where()` 的路径作为 `REQUESTS_CA_BUNDLE`：

```powershell
$env:REQUESTS_CA_BUNDLE = (python -c "import certifi; print(certifi.where())")
python app.py
```

    4. 如果回退请求（README 中的回退逻辑）仍失败，请把完整的 SDK 错误和回退请求错误粘贴出来以便进一步排查。

### 服务器与启动说明（摘录）

- 开发启动：`python run.py` 或 `python app.py`，默认监听 `http://localhost:8080`。
- 看到 `Running on http://127.0.0.1:8080` 即表示服务已正常启动。
- 开发时看到的 Werkzeug 警告（提示开发服务器不适合生产）可以忽略；生产请使用 Waitress/Gunicorn 并配置 HTTPS。

### 需要保留的配置项（.env）

- `ARK_API_KEY` - 火山方舟 API Key
- `ARK_BASE_URL` - 火山方舟 REST 基础 URL（回退使用）
- `DEEPSEEK_MODEL` - 使用的模型 ID（确保在控制台已开通）
- `DISABLE_SSL_VERIFY` - 调试时可设置为 `1` 临时禁用 SSL 验证（不推荐在生产环境使用）

如果你需要，我可以把这些关键配置写入 `.env.example` 或 `README.md` 的配置示例中。

