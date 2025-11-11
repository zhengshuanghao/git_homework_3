# Docker 环境故障排查指南

## 问题：语音识别功能在 Docker 中返回 401 错误

### 症状
```
错误: 网络连接失败: 401, message='Invalid response status', 
url=URL('wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async')
```

### 原因分析
401 错误表示认证失败，通常是因为：
1. 环境变量未正确传递到 Docker 容器
2. `.env` 文件不存在或未被正确加载
3. API 密钥配置错误或已过期

### 解决方案

#### 方案 1：确保 .env 文件存在并包含正确的配置

1. **检查 .env 文件是否存在**
   ```bash
   # 在项目根目录下
   ls -la .env
   ```

2. **如果不存在，从示例文件创建**
   ```bash
   cp .env.example .env
   ```

3. **编辑 .env 文件，填入您的实际 API 密钥**
   ```bash
   # 使用文本编辑器打开
   notepad .env  # Windows
   # 或
   nano .env     # Linux/Mac
   ```

4. **确保包含以下必需配置**
   ```env
   # 火山方舟流式语音识别
   SPEECH_APP_ID=your_actual_app_id
   SPEECH_ACCESS_KEY=your_actual_access_key
   SPEECH_SECRET_KEY=your_actual_secret_key
   SPEECH_MODEL_ID=your_actual_model_id
   
   # 其他必需配置...
   AMAP_API_KEY=your_amap_key
   ARK_API_KEY=your_ark_api_key
   DEEPSEEK_MODEL=your_endpoint_id
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

#### 方案 2：验证 Docker 容器中的环境变量

1. **启动容器后，进入容器检查环境变量**
   ```bash
   docker exec -it ai-travel-planner bash
   
   # 在容器内执行
   echo $SPEECH_APP_ID
   echo $SPEECH_ACCESS_KEY
   echo $SPEECH_SECRET_KEY
   ```

2. **检查应用启动日志**
   ```bash
   docker logs ai-travel-planner
   ```
   
   应该看到类似输出：
   ```
   ============================================================
   应用启动 - 配置状态检查
   ============================================================
   语音识别 APP_ID: 已设置
   语音识别 ACCESS_KEY: 已设置
   语音识别 SECRET_KEY: 已设置
   语音识别 MODEL_ID: Speech_Recognition_Seed_streaming2000000451913596898
   ...
   ```

3. **如果显示"❌ 未设置"，说明环境变量未正确加载**

#### 方案 3：重新构建和启动容器

1. **停止并删除现有容器**
   ```bash
   docker-compose down
   ```

2. **确保 .env 文件在项目根目录**
   ```bash
   pwd  # 确认当前目录
   ls .env  # 确认文件存在
   ```

3. **重新启动容器**
   ```bash
   docker-compose up -d
   ```

4. **查看启动日志**
   ```bash
   docker-compose logs -f
   ```

#### 方案 4：使用环境变量文件挂载（备选方案）

如果 `env_file` 方式不工作，可以尝试直接挂载：

修改 `docker-compose.yml`：
```yaml
services:
  ai-travel-planner:
    # ... 其他配置 ...
    volumes:
      - ./.env:/app/.env:ro  # 只读挂载 .env 文件
```

### 验证步骤

1. **检查配置加载**
   访问：`http://localhost:8080/api/config/all`
   
   应该看到所有配置项都显示为 `true`（已设置）

2. **测试语音功能**
   - 打开应用
   - 点击麦克风按钮
   - 说话测试
   - 检查浏览器控制台是否还有 401 错误

### 常见错误

#### 错误 1：.env 文件格式错误
```bash
# 错误示例（有空格）
SPEECH_APP_ID = your_app_id

# 正确示例（无空格）
SPEECH_APP_ID=your_app_id
```

#### 错误 2：.env 文件被 .gitignore 忽略
确保 `.env` 文件存在于本地，即使它在 `.gitignore` 中。

#### 错误 3：API 密钥包含特殊字符
如果密钥包含特殊字符，使用引号：
```env
SPEECH_SECRET_KEY="your-key-with-special-chars!@#"
```

### 调试命令

```bash
# 1. 查看容器日志
docker logs ai-travel-planner --tail 100

# 2. 进入容器检查
docker exec -it ai-travel-planner bash
cat .env  # 查看 .env 文件内容（如果挂载了）
env | grep SPEECH  # 查看语音相关环境变量

# 3. 重启容器
docker-compose restart

# 4. 完全重建
docker-compose down
docker-compose up --build -d
```

### 获取帮助

如果问题仍未解决：
1. 检查火山方舟控制台，确认 API 密钥是否有效
2. 确认 API 密钥的权限和配额
3. 查看完整的错误日志：`docker logs ai-travel-planner > error.log`
