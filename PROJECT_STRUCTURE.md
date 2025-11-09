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
REMOVED: 内容已合并到 `README.md`。此文件为精简占位，原始文档已保存在 `README.md` 中。
│   │   └── style.css         # 样式文件

│   └── js/

│       └── app.js            # 前端JavaScript

│

├── database/                  # 数据库相关
