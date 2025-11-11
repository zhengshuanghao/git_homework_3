# Docker 部署指南

## 📦 获取Docker镜像

### 方式一：从阿里云镜像仓库拉取（推荐）

```bash
# 拉取最新版本
docker pull registry.cn-hangzhou.aliyuncs.com/ai-travel-planner/ai-travel-planner:latest

# 或拉取指定版本
docker pull registry.cn-hangzhou.aliyuncs.com/ai-travel-planner/ai-travel-planner:v1.0.0
```

### 方式二：本地构建

```bash
# 克隆项目
git clone <your-repo-url>
cd homework_3

# 构建镜像
docker build -t ai-travel-planner:latest .
```

## 🚀 运行容器

### 方式一：使用docker run

```bash
docker run -d \
  --name ai-travel-planner \
  -p 8080:8080 \
  -e SPEECH_APP_ID=your_app_id \
  -e SPEECH_ACCESS_KEY=your_access_key \
  -e SPEECH_SECRET_KEY=your_secret_key \
  -e SPEECH_MODEL_ID=your_model_id \
  -e AMAP_API_KEY=your_amap_key \
  -e ARK_API_KEY=your_ark_key \
  -e DEEPSEEK_MODEL=your_model_id \
  -e SUPABASE_URL=your_supabase_url \
  -e SUPABASE_KEY=your_supabase_key \
  registry.cn-hangzhou.aliyuncs.com/ai-travel-planner/ai-travel-planner:latest
```

### 方式二：使用docker-compose（推荐）

1. **创建.env文件**

```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件，填入您的API密钥
nano .env
```

2. **启动服务**

```bash
docker-compose up -d
```

3. **查看日志**

```bash
docker-compose logs -f
```

4. **停止服务**

```bash
docker-compose down
```

## 🔧 配置说明

### 环境变量

所有配置通过环境变量传递，支持以下变量：

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `SPEECH_APP_ID` | 火山方舟语音识别APP ID | 否 |
| `SPEECH_ACCESS_KEY` | 火山方舟语音识别Access Key | 否 |
| `SPEECH_SECRET_KEY` | 火山方舟语音识别Secret Key | 否 |
| `SPEECH_MODEL_ID` | 火山方舟语音识别Model ID | 否 |
| `AMAP_API_KEY` | 高德地图API Key | 否 |
| `AMAP_API_SECRET` | 高德地图API Secret | 否 |
| `ARK_API_KEY` | 火山方舟DeepSeek API Key | 是 |
| `ARK_BASE_URL` | 火山方舟API Base URL | 否 |
| `DEEPSEEK_MODEL` | DeepSeek模型ID | 是 |
| `SUPABASE_URL` | Supabase数据库URL | 是 |
| `SUPABASE_KEY` | Supabase数据库Key | 是 |
| `FLASK_SECRET_KEY` | Flask会话密钥 | 否 |
| `FLASK_ENV` | Flask环境 | 否 |

### 配置方式

#### 1. 环境变量（推荐）

```bash
docker run -e SPEECH_APP_ID=xxx -e ARK_API_KEY=xxx ...
```

#### 2. .env文件

```bash
docker run --env-file .env ...
```

#### 3. docker-compose.yml

```yaml
environment:
  - SPEECH_APP_ID=xxx
  - ARK_API_KEY=xxx
```

## 📝 使用示例

### 完整示例（使用.env文件）

1. **创建.env文件**

```env
# 火山方舟语音识别
SPEECH_APP_ID=1356755714
SPEECH_ACCESS_KEY=your_access_key
SPEECH_SECRET_KEY=your_secret_key
SPEECH_MODEL_ID=your_model_id

# 高德地图
AMAP_API_KEY=your_amap_key

# 火山方舟 DeepSeek
ARK_API_KEY=your_ark_key
DEEPSEEK_MODEL=your_model_id

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key
```

2. **启动容器**

```bash
docker-compose up -d
```

3. **访问应用**

打开浏览器访问：http://localhost:8080

## 🔍 故障排查

### 查看容器日志

```bash
# docker run方式
docker logs ai-travel-planner

# docker-compose方式
docker-compose logs -f
```

### 进入容器调试

```bash
docker exec -it ai-travel-planner /bin/bash
```

### 检查容器状态

```bash
docker ps -a
docker inspect ai-travel-planner
```

### 常见问题

#### 1. 端口被占用

```bash
# 修改端口映射
docker run -p 8081:8080 ...
```

#### 2. 配置未生效

```bash
# 检查环境变量
docker exec ai-travel-planner env | grep SPEECH
```

#### 3. 容器无法启动

```bash
# 查看详细日志
docker logs ai-travel-planner --tail 100
```

## 🔄 更新镜像

```bash
# 拉取最新镜像
docker pull registry.cn-hangzhou.aliyuncs.com/ai-travel-planner/ai-travel-planner:latest

# 停止并删除旧容器
docker-compose down

# 启动新容器
docker-compose up -d
```

## 🛡️ 生产环境建议

1. **使用具体版本标签**
   ```bash
   docker pull registry.cn-hangzhou.aliyuncs.com/ai-travel-planner/ai-travel-planner:v1.0.0
   ```

2. **配置资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
       reservations:
         cpus: '1'
         memory: 1G
   ```

3. **配置健康检查**
   已在docker-compose.yml中配置

4. **使用HTTPS**
   建议在前端配置Nginx反向代理

5. **定期备份数据**
   Supabase数据需要定期备份

## 📊 监控

### 查看资源使用

```bash
docker stats ai-travel-planner
```

### 健康检查

```bash
docker inspect --format='{{.State.Health.Status}}' ai-travel-planner
```

## 🔗 相关链接

- GitHub仓库：<your-repo-url>
- 阿里云镜像仓库：https://cr.console.aliyun.com/
- 项目文档：README.md

## 💡 提示

- 首次运行需要配置所有必需的API密钥
- 可以在运行后通过界面的"API设置"功能配置密钥
- 建议使用docker-compose方式部署，更易管理
