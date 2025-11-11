# 🗺️ AI旅行规划师

<div align="center">

**基于AI的智能旅行规划Web应用**

支持文字和语音输入 | 自动生成个性化旅行计划 | 费用管理 | 云端同步

[快速开始](#快速开始) • [功能特性](#功能特性) • [使用说明](#使用说明) • [常见问题](#常见问题)

</div>

---

## ✨ 功能特性

### 🎯 核心功能

- **🤖 智能行程规划**
  - AI生成详细旅行路线
  - 包含交通、住宿、景点、餐厅推荐
  - 根据预算推荐具体酒店和餐厅

- **⚙️ 旅游偏好设置**
  - 8大类偏好设置（旅行风格、住宿、饮食等）
  - 保存个人偏好，生成更符合需求的计划
  - AI自动结合偏好生成个性化方案

- **💰 费用记录管理**
  - 记录和统计旅行开销
  - 支持关联具体旅行计划
  - 费用分类汇总和可视化展示

- **🎤 语音输入**
  - 火山方舟流式语音识别
  - 实时转换语音为文字
  - 支持中文识别

- **🗺️ 地图展示**
  - 高德地图展示行程路线
  - 标记景点和地点位置
  - 可视化行程规划

- **👤 用户系统**
  - 注册登录功能
  - 云端保存所有数据
  - 多设备同步访问

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | Flask + Flask-SocketIO |
| **前端** | HTML5 + CSS3 + JavaScript |
| **AI大模型** | 火山方舟 DeepSeek API |
| **语音识别** | 火山方舟流式语音识别 |
| **地图服务** | 高德地图 API |
| **数据库** | Supabase (PostgreSQL) |

---

## 🚀 快速开始

### 🐳 方式一：Docker部署（推荐）

**最简单的方式，一键启动！**

```bash
# 1. 拉取镜像
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest

# 2. 运行容器（需要配置环境变量）
docker run -d \
  --name ai-travel-planner \
  -p 8080:8080 \
  -e ARK_API_KEY=your_key \
  -e DEEPSEEK_MODEL=your_model \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest

# 3. 访问应用
# 打开浏览器访问 http://localhost:8080
```

**或使用docker-compose：**

```bash
# 1. 下载docker-compose.yml和.env.example
# 2. 配置.env文件
cp .env.example .env
# 编辑.env文件填入API密钥

# 3. 启动
docker-compose up -d
```

📖 详细说明请查看：[给助教的使用说明](给助教的使用说明.md)

---

### 💻 方式二：本地部署

#### 1️⃣ 环境要求

- Python 3.8+
- pip 包管理器
- 现代浏览器（Chrome/Firefox/Edge）

#### 2️⃣ 安装依赖

```bash
# 克隆或下载项目后，进入项目目录
cd homework_3

# 安装Python依赖
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量

创建 `.env` 文件并填入以下配置：

```env
相关API Key请助教在pdf文件中查看
```

> **⚠️ 安全提示**：以上密钥仅供开发测试使用，生产环境请更换为您自己的密钥。

### 4️⃣ 初始化数据库

在 [Supabase控制台](https://supabase.com) 的SQL编辑器中执行 `database/schema.sql` 文件。

**重要**：如果遇到RLS（行级安全）错误，执行以下SQL：

```sql
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 5️⃣ 启动应用

**方式一：使用启动脚本（推荐）**

```bash
# Windows
快速启动.bat
```

**方式二：直接运行**

```bash
python app.py
```

### 6️⃣ 访问应用

打开浏览器访问：**http://localhost:8080**

---

## 📖 使用说明

### 第一步：注册/登录

1. 首次访问会看到欢迎页面
2. 点击右上角"注册"按钮创建账号
3. 填写邮箱和密码完成注册
4. 登录后自动跳转到主应用界面

### 第二步：设置旅游偏好（推荐）

1. 点击导航栏的 **"⚙️ 偏好设置"** 按钮
2. 选择您的旅行偏好：
   - 旅行风格（休闲、探险、文化等）
   - 住宿类型（经济型、舒适型、豪华型等）
   - 饮食偏好（中餐、西餐、素食等）
   - 交通偏好（公共交通、出租车、租车等）
   - 活动偏好（博物馆、户外、购物等）
   - 预算等级（经济、中等、高端）
   - 行程节奏（轻松、适中、紧凑）
   - 特殊需求（无障碍、带小孩等）
3. 点击"保存偏好"
4. 之后生成的计划会自动结合您的偏好

### 第三步：生成旅行计划

#### 📝 文字输入方式

1. 在输入框中输入旅行需求，例如：
   ```
   我想去北京玩3天，预算5000元，喜欢历史文化
   ```
2. 点击 **"生成旅行计划"** 按钮
3. 等待AI生成计划（约10-30秒）

#### 🎤 语音输入方式

1. 点击 **麦克风图标** 按钮
2. 允许浏览器访问麦克风
3. 说出您的旅行需求
4. 点击"停止"按钮
5. 系统自动识别并生成计划

### 第四步：查看行程

生成的旅行计划包含：

- **📍 地图展示**：右侧地图标记所有景点位置
- **📅 详细行程**：每日活动安排、时间、地点
- **🏨 住宿推荐**：具体酒店名称、地址、价格、特色
- **🍽️ 餐厅推荐**：餐厅名称、菜系、招牌菜、人均消费
- **🚗 交通建议**：出行方式和路线
- **💵 预算明细**：各项费用估算

### 第五步：记录费用

1. 点击导航栏的 **"💰 费用记录"** 按钮
2. 在弹出的模态框中：
   - 选择关联的旅行计划（可选）
   - 输入金额
   - 选择类别（交通、住宿、餐饮、景点、购物、其他）
   - 选择日期
   - 填写描述（可选）
3. 点击"添加"按钮
4. 查看费用汇总和分类统计

### 第六步：管理计划

- **查看历史计划**：在左侧"我的旅行计划"列表中查看所有计划
- **加载计划**：点击计划项查看详情
- **删除计划**：点击计划右侧的 🗑️ 按钮删除不需要的计划

---

## 📂 项目结构

```
homework_3/
├── 📄 app.py                    # Flask主应用（包含启动逻辑）
├── ⚙️ config.py                 # 配置管理
├── 📦 requirements.txt          # Python依赖
├── 🔐 .env                      # 环境变量（需自行创建）
├── 🪟 快速启动.bat              # Windows快速启动脚本
├── 📁 database/
│   └── schema.sql              # 数据库结构
├── 📁 services/                # 服务层
│   ├── deepseek_service.py     # AI生成服务
│   ├── speech_recognition_service.py  # 语音识别
│   ├── supabase_service.py     # 数据库服务
│   ├── amap_service.py         # 地图服务
│   ├── preference_service.py   # 偏好设置服务
│   └── expense_service.py      # 费用记录服务
├── 📁 templates/               # HTML模板
│   ├── landing.html            # 欢迎页
│   └── app.html                # 主应用页
└── 📁 static/                  # 静态资源
    ├── 📁 css/
    │   ├── landing.css
    │   └── style.css
    └── 📁 js/
        ├── landing.js
        ├── app.js
        └── audio-recorder.js
```

---

## 🎨 界面预览

### 欢迎页面
- 简洁美观的首页
- 功能介绍和特性展示
- 快速注册/登录入口

### 主应用界面
- 左侧：输入区域、我的计划列表
- 右侧：地图展示、行程详情
- 顶部：导航栏（偏好设置、费用记录、用户信息）

### 偏好设置模态框
- 8大类偏好选项
- 多选和单选结合
- 实时保存到云端

### 费用记录模态框
- 费用汇总卡片
- 添加费用表单
- 费用列表和删除功能

---

## ❓ 常见问题

### 1. RLS策略错误

**问题**：遇到 "new row violates row-level security policy" 错误

**解决方案**：在Supabase SQL编辑器中执行：

```sql
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 2. 语音识别不工作

**问题**：点击麦克风按钮没有反应或报错

**解决方案**：
- ✅ 必须使用 `http://localhost:8080` 或 HTTPS
- ✅ 检查浏览器麦克风权限（地址栏左侧图标）
- ✅ 关闭其他占用麦克风的应用（Zoom、Teams等）
- ✅ 推荐使用Chrome浏览器
- ✅ 在浏览器控制台测试：
  ```javascript
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => { 
      stream.getTracks().forEach(t => t.stop()); 
      console.log('麦克风正常'); 
    })
    .catch(err => console.error('麦克风错误:', err));
  ```

### 3. API配置问题

**问题**：提示API未配置或调用失败

**解决方案**：
- 检查 `.env` 文件是否存在且配置正确
- 确认所有API密钥都已填写
- 验证API密钥是否有效（未过期、未超额）
- 重启应用使配置生效

### 4. 端口占用

**问题**：启动时提示端口8080已被占用

**解决方案**：
- 方式一：关闭占用8080端口的程序
- 方式二：修改 `app.py` 中的端口号（文件末尾）：
  ```python
  socketio.run(app, host='0.0.0.0', port=8081, debug=True, allow_unsafe_werkzeug=True)
  ```

### 5. 数据库连接失败

**问题**：无法连接到Supabase数据库

**解决方案**：
- 检查 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确
- 确认网络连接正常
- 检查Supabase项目是否已暂停（免费版会自动暂停）
- 在Supabase控制台检查数据库表是否已创建

---

## 🔒 安全注意事项

1. **API密钥安全**
   - ⚠️ 不要将 `.env` 文件提交到公开代码库
   - ⚠️ 生产环境请更换所有默认密钥
   - ⚠️ 定期更新和轮换API密钥

2. **数据隐私**
   - 用户数据存储在Supabase云端
   - 建议启用RLS策略保护数据
   - 定期备份重要数据

3. **浏览器兼容性**
   - 需要支持WebSocket和MediaRecorder API
   - 推荐使用Chrome、Firefox、Edge等现代浏览器
   - 不支持IE浏览器

---

## 🎯 功能路线图

### ✅ 已完成
- [x] 智能行程规划
- [x] 语音输入识别
- [x] 地图展示
- [x] 用户系统
- [x] 旅游偏好设置
- [x] 费用记录管理
- [x] 计划删除功能

### 🚧 计划中
- [ ] 多语言支持
- [ ] 行程分享功能
- [ ] 费用导出（Excel/PDF）
- [ ] 天气预报集成
- [ ] 移动端适配
- [ ] 离线地图支持

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python app.py
```

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📞 联系方式

如有问题或建议，请提交Issue或联系开发者。

---

## 🙏 致谢

感谢以下服务提供商：

- [火山方舟](https://www.volcengine.com/) - AI大模型和语音识别
- [高德地图](https://lbs.amap.com/) - 地图服务
- [Supabase](https://supabase.com/) - 数据库服务
- [Flask](https://flask.palletsprojects.com/) - Web框架

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个Star支持一下！**

Made with ❤️ by AI Travel Planner Team

</div>
