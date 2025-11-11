# 🚀 Docker快速开始指南

## 5分钟快速部署

### 前置要求

- 已安装Docker（[下载Docker](https://www.docker.com/get-started)）
- 有可用的API密钥

### 步骤1：拉取镜像

```bash
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

### 步骤2：准备配置

创建一个`.env`文件，内容如下：

```env
# 必需配置
ARK_API_KEY=你的火山方舟API密钥
DEEPSEEK_MODEL=你的模型ID
SUPABASE_URL=你的Supabase URL
SUPABASE_KEY=你的Supabase密钥

# 可选配置（如需使用相关功能）
SPEECH_APP_ID=语音识别APP_ID
SPEECH_ACCESS_KEY=语音识别Access Key
SPEECH_SECRET_KEY=语音识别Secret Key
SPEECH_MODEL_ID=语音识别Model ID
AMAP_API_KEY=高德地图API Key
```

### 步骤3：启动容器

**方式A：使用环境变量文件**

```bash
docker run -d \
  --name ai-travel-planner \
  -p 8080:8080 \
  --env-file .env \
  crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

**方式B：直接指定环境变量**

```bash
docker run -d \
  --name ai-travel-planner \
  -p 8080:8080 \
  -e ARK_API_KEY=你的密钥 \
  -e DEEPSEEK_MODEL=你的模型ID \
  -e SUPABASE_URL=你的URL \
  -e SUPABASE_KEY=你的密钥 \
  crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

### 步骤4：访问应用

打开浏览器访问：**http://localhost:8080**

## 🎉 完成！

现在您可以：
1. 注册/登录账号
2. 在"API设置"中配置其他密钥（可选）
3. 开始使用AI旅行规划功能

## 📋 常用命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs ai-travel-planner

# 停止容器
docker stop ai-travel-planner

# 启动容器
docker start ai-travel-planner

# 删除容器
docker rm -f ai-travel-planner

# 更新到最新版本
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
docker stop ai-travel-planner
docker rm ai-travel-planner
# 然后重新运行步骤3
```

## 🐛 遇到问题？

### 端口被占用

修改端口映射：
```bash
docker run -d -p 8081:8080 ...  # 使用8081端口
```

### 容器无法启动

查看详细日志：
```bash
docker logs ai-travel-planner --tail 100
```

### 配置未生效

检查环境变量：
```bash
docker exec ai-travel-planner env
```

## 📚 更多信息

- [完整Docker部署指南](DOCKER_DEPLOYMENT.md)
- [GitHub Actions自动构建配置](GITHUB_ACTIONS_SETUP.md)
- [项目README](README.md)
