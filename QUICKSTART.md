# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

**重要**: 确保已安装 FFmpeg（pydub 需要）

## 2. 配置API密钥

### 方式一：创建 .env 文件（推荐）

复制 `.env.example` 并重命名为 `.env`，填入你的API密钥：

```env
IFLYTEK_APP_ID=c80a4c00
IFLYTEK_API_KEY=be6071e8028efa1bac85a18023221559
IFLYTEK_API_SECRET=OTcyNDQ5ZTI0MjUzNDg0ZTUxODViNjcw
AMAP_API_KEY=62b0a02ed7213d7753d65007051c0c6f
DEEPSEEK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
SUPABASE_URL=https://hfhxiwcuikcmtpcyyevl.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhmaHhpd2N1aWtjbXRwY3l5ZXZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MzczNDksImV4cCI6MjA3ODExMzM0OX0.u9xX7WOMuYq4fBwJI313vc14OfOuSgabylXqUWFSwTQ
```

### 方式二：在应用内配置

启动应用后，点击右上角"设置"按钮，在设置页面输入API密钥。

## 3. 配置Supabase（可选，用于用户功能）

1. 在 [Supabase](https://supabase.com) 创建项目
2. 在SQL编辑器中运行 `database/schema.sql` 中的SQL语句创建表
3. 在 `.env` 文件中填入 Supabase URL 和 Key

## 4. 启动应用

```bash
python run.py
```

## 5. 使用应用

1. 打开浏览器访问 `http://localhost:8080`
2. 选择输入方式（文字或语音）
3. 输入或说出你的旅行需求，例如：
   - "我想去日本，5天，预算1万元，喜欢美食和动漫，带孩子"
   - "计划一次北京3日游，预算5000元，2个人"
4. 点击"生成旅行计划"
5. 查看生成的行程和地图标记

## 常见问题

### Q: 语音识别不工作？
A: 检查以下几点：
- 浏览器是否允许麦克风权限
- 科大讯飞API密钥是否正确配置
- 网络连接是否正常

### Q: 地图不显示？
A: 检查高德地图API Key是否正确配置，并在高德开放平台设置正确的域名白名单。

### Q: 无法生成旅行计划？
A: 检查DeepSeek API Key是否正确配置，以及账户余额是否充足。

### Q: 用户注册/登录失败？
A: 确保Supabase已正确配置，并且运行了数据库表创建脚本。

## 技术支持

如有问题，请查看完整的 [README.md](README.md) 文档。




