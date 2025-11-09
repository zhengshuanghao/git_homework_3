# 如何获取Flask配置内容

本项目提供了多种方式来查看和获取Flask配置信息：

## 方法一：使用配置检查工具（推荐）

运行配置检查脚本：

```bash
python check_config.py
```

这个工具会显示：
- 所有配置项的设置状态
- 配置值的部分预览（不显示完整敏感信息）
- 配置文件来源（.env 或 config.json）
- 配置完整性检查

## 方法二：在Python代码中访问

### 1. 通过Config类访问

```python
from config import Config

# 访问配置值
app_id = Config.IFLYTEK_APP_ID
api_key = Config.AMAP_API_KEY
supabase_url = Config.SUPABASE_URL
```

### 2. 通过Flask应用对象访问

```python
from app import app

# 访问Flask配置
secret_key = app.config.get('SECRET_KEY')
env = app.config.get('ENV')
```

### 3. 在Flask路由中访问

```python
@app.route('/example')
def example():
    from config import Config
    return f"API Key: {Config.AMAP_API_KEY}"
```

## 方法三：通过API接口获取

### 1. 获取前端需要的配置

```bash
curl http://localhost:8080/api/config
```

返回：
```json
{
  "amap_api_key": "...",
  "supabase_url": "...",
  "supabase_key": "..."
}
```

### 2. 获取所有配置状态（新增）

```bash
curl http://localhost:8080/api/config/all
```

返回配置状态（不包含敏感信息）：
```json
{
  "flask": {
    "secret_key_set": true,
    "env": "development"
  },
  "iflytek": {
    "app_id_set": true,
    "api_key_set": true,
    "api_secret_set": true
  },
  "amap": {
    "api_key_set": true,
    "api_secret_set": true
  },
  "deepseek": {
    "api_key_set": true,
    "base_url": "https://api.deepseek.com"
  },
  "supabase": {
    "url_set": true,
    "key_set": true
  }
}
```

## 方法四：在Python交互式环境中查看

启动Python交互式环境：

```bash
python
```

然后执行：

```python
# 导入配置
from config import Config

# 查看所有配置属性
print("Flask配置:")
print(f"  SECRET_KEY: {Config.SECRET_KEY}")

print("\n科大讯飞配置:")
print(f"  APP_ID: {Config.IFLYTEK_APP_ID}")
print(f"  API_KEY: {Config.IFLYTEK_API_KEY}")
print(f"  API_SECRET: {Config.IFLYTEK_API_SECRET}")

print("\n高德地图配置:")
print(f"  API_KEY: {Config.AMAP_API_KEY}")
print(f"  API_SECRET: {Config.AMAP_API_SECRET}")

print("\nDeepSeek配置:")
print(f"  API_KEY: {Config.DEEPSEEK_API_KEY}")
print(f"  BASE_URL: {Config.DEEPSEEK_BASE_URL}")

print("\nSupabase配置:")
print(f"  URL: {Config.SUPABASE_URL}")
print(f"  KEY: {Config.SUPABASE_KEY}")
```

## 方法五：直接查看配置文件

### 查看.env文件

```bash
# Windows PowerShell
Get-Content .env

# Linux/Mac
cat .env
```

### 查看config.json文件（如果存在）

```bash
# Windows PowerShell
Get-Content config.json

# Linux/Mac
cat config.json
```

## 配置加载顺序

配置按以下顺序加载：

1. **环境变量**（.env文件） - 优先级最高
2. **config.json文件** - 如果存在
3. **默认值** - 在Config类中定义

## 注意事项

⚠️ **安全提示**：
- 不要在代码中硬编码API密钥
- 不要将包含敏感信息的配置文件提交到Git
- 生产环境中使用环境变量而不是配置文件
- API接口 `/api/config/all` 只返回配置状态，不返回实际密钥值

## 示例：在代码中使用配置

```python
from config import Config
from services.iflytek_service import IflytekService

# 检查配置是否已设置
if Config.IFLYTEK_APP_ID:
    service = IflytekService()
    if service.is_configured():
        print("语音识别服务已配置")
    else:
        print("语音识别服务配置不完整")
else:
    print("请先配置科大讯飞API密钥")
```

## 快速检查配置

运行以下命令快速检查所有配置：

```bash
python check_config.py
```

这会显示所有配置的状态和完整性检查结果。

