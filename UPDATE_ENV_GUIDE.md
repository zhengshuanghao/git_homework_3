# 更新 .env 文件指南

## 📝 说明

您的 `.env` 文件还包含旧的科大讯飞配置，需要更新为豆包配置。

## 🔄 更新步骤

### 方法 1：手动编辑（推荐）

1. 打开您的 `.env` 文件
2. **删除**以下科大讯飞相关配置：
   ```env
   # 科大讯飞语音识别API
   IFLYTEK_APP_ID=c80a4c00
   IFLYTEK_API_KEY=be6071e8028efa1bac85a18023221559
   IFLYTEK_API_SECRET=OTcyNDQ5ZTI0MjUzNDg0ZTUxODViNjcw
   ```

3. **添加**以下豆包配置（在文件顶部）：
   ```env
   # 豆包实时语音大模型API（已替换科大讯飞）
   DOUBAO_APP_ID=1356755714
   DOUBAO_ACCESS_KEY=oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP
   DOUBAO_SECRET_KEY=Aj8WnzaLDOeWTiIcF9zC-7dN2QPypq6h
   DOUBAO_MODEL_ID=Doubao_scene_SLM_Doubao_realtime_voice_model2000000451087472322
   ```

4. 保存文件

### 方法 2：完全替换

1. **备份**当前的 `.env` 文件（以防万一）
2. 删除当前的 `.env` 文件
3. 将 `.env.doubao` 文件重命名为 `.env`
4. 检查其他配置（高德地图、Supabase等）是否正确

## ✅ 更新后的完整 .env 文件内容

```env
# ============================================================
# AI旅行规划师 - 环境变量配置
# 豆包实时语音版
# ============================================================

# ============================================================
# 豆包实时语音大模型API（已替换科大讯飞）
# ============================================================
DOUBAO_APP_ID=1356755714
DOUBAO_ACCESS_KEY=oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP
DOUBAO_SECRET_KEY=Aj8WnzaLDOeWTiIcF9zC-7dN2QPypq6h
DOUBAO_MODEL_ID=Doubao_scene_SLM_Doubao_realtime_voice_model2000000451087472322

# ============================================================
# 高德地图API
# ============================================================
AMAP_API_KEY=62b0a02ed7213d7753d65007051c0c6f
AMAP_API_SECRET=66a262e19c64cdc1109b2c70dd89fee0

# ============================================================
# DeepSeek LLM API（旅行规划）
# ============================================================
DEEPSEEK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v3-1-250821

# ============================================================
# 火山方舟配置（备用）
# ============================================================
ARK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# ============================================================
# Supabase数据库配置
# ============================================================
SUPABASE_URL=https://hfhxiwcuikcmtpcyyevl.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhmaHhpd2N1aWtjbXRwY3l5ZXZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MzczNDksImV4cCI6MjA3ODExMzM0OX0.u9xX7WOMuYq4fBwJI313vc14OfOuSgabylXqUWFSwTQ

# ============================================================
# Flask配置
# ============================================================
FLASK_SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
```

## 🔍 验证更新

更新后，运行以下命令验证配置：

```bash
python -c "from config import Config; from dotenv import load_dotenv; load_dotenv(); print('豆包APP_ID:', Config.DOUBAO_APP_ID); print('豆包ACCESS_KEY:', Config.DOUBAO_ACCESS_KEY[:10] + '...' if Config.DOUBAO_ACCESS_KEY else 'None')"
```

应该看到：
```
豆包APP_ID: 1356755714
豆包ACCESS_KEY: oPxND_k8BQ...
```

## ⚠️ 重要说明

### 1. 科大讯飞 vs 豆包

| 项目 | 科大讯飞 | 豆包 |
|------|----------|------|
| 功能 | 仅语音识别 | 端到端对话 |
| 输出 | 仅文字 | 文字+语音 |
| AI能力 | 无 | 内置大模型 |
| 配置数量 | 3个 | 4个 |

### 2. 配置对照表

**旧配置（科大讯飞）- 已删除：**
- ❌ `IFLYTEK_APP_ID`
- ❌ `IFLYTEK_API_KEY`
- ❌ `IFLYTEK_API_SECRET`

**新配置（豆包）- 已添加：**
- ✅ `DOUBAO_APP_ID`
- ✅ `DOUBAO_ACCESS_KEY`
- ✅ `DOUBAO_SECRET_KEY`
- ✅ `DOUBAO_MODEL_ID`

### 3. 其他配置保持不变

以下配置无需修改：
- ✅ 高德地图API（AMAP_*）
- ✅ DeepSeek API（DEEPSEEK_*）
- ✅ Supabase配置（SUPABASE_*）
- ✅ Flask配置（FLASK_*）

## 🚀 更新后测试

### 1. 重启服务器

```bash
python run.py
```

### 2. 查看启动日志

应该看到：
```
============================================================
AI旅行规划师 - 豆包实时语音版
============================================================
服务器地址: http://localhost:8080
语音服务: 豆包端到端实时语音大模型
============================================================
```

### 3. 测试语音对话

1. 打开浏览器：`http://localhost:8080`
2. 点击"开始录音"
3. 说话测试
4. 应该听到AI的语音回复

## ❓ 常见问题

### Q1: 找不到豆包配置？

**A:** 检查 `config.py` 文件，应该包含：
```python
DOUBAO_APP_ID = os.getenv('DOUBAO_APP_ID', '')
DOUBAO_ACCESS_KEY = os.getenv('DOUBAO_ACCESS_KEY', '')
DOUBAO_SECRET_KEY = os.getenv('DOUBAO_SECRET_KEY', '')
DOUBAO_MODEL_ID = os.getenv('DOUBAO_MODEL_ID', '...')
```

### Q2: 启动时报错找不到科大讯飞配置？

**A:** 说明代码中还有引用科大讯飞的地方，请检查：
- `app.py` - 应该使用 `doubao_service`
- `services/` - 不应该有 `iflytek_service.py`

### Q3: 如何确认使用的是豆包而不是科大讯飞？

**A:** 查看启动日志，应该显示"豆包实时语音版"而不是科大讯飞。

## 📞 需要帮助？

如果更新后遇到问题：
1. 检查 `.env` 文件格式是否正确
2. 确认所有等号前后没有空格
3. 确认密钥没有换行
4. 重启服务器

---

**完成更新后，您就可以使用强大的豆包实时语音对话功能了！** 🎉




