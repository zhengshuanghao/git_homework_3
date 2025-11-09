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

REMOVED: 内容已合并到 `README.md`。此文件为精简占位，原始文档已保存在 `README.md` 中。


1. 在 [Supabase](https://supabase.com) 创建项目

2. 在SQL编辑器中运行 `database/schema.sql` 中的SQL语句创建表

3. 在 `.env` 文件中填入 Supabase URL 和 Key


