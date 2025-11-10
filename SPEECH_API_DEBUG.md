# 火山方舟语音识别API调试指南

## 🔍 当前问题

**错误信息**：`server rejected WebSocket connection: HTTP 404`

这表示 WebSocket 连接的 URL 或认证参数不正确。

---

## 🛠️ 临时解决方案

### 方案1：使用文字输入模式（推荐）

目前语音识别API连接有问题，**请先使用文字输入模式**：

1. 点击页面顶部的 **"文字输入"** 标签
2. 在文本框中输入旅行需求
3. 点击 **"生成旅行计划"** 按钮
4. AI会生成旅行计划并显示在地图上

**示例输入**：
```
我想去北京旅游，5天时间，预算1万元，喜欢历史文化和美食
```

### 方案2：修复语音识别API（需要API文档）

要修复语音识别功能，需要火山方舟的**官方API文档**来确认：

#### 需要确认的信息：

1. **WebSocket 端点 URL**
   - 当前尝试：`wss://openspeech.bytedance.com/api/v1/asr`
   - 可能的其他格式：
     - `wss://openspeech.bytedance.com/api/v2/asr`
     - `wss://api.volcengine.com/v1/speech/asr`
     - 需要查看官方文档

2. **认证方式**
   - 当前尝试：使用 `token` 参数传递 Access Key
   - 可能需要的其他方式：
     - HTTP Header 认证：`Authorization: Bearer {access_token}`
     - 签名认证：使用 HMAC-SHA256 生成签名
     - 需要查看官方文档

3. **必需参数**
   - `appid`: 1356755714
   - `token`: oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP
   - `model`: Speech_Recognition_Seed_streaming2000000451913596898
   - 其他参数可能需要根据文档调整

---

## 📝 调试步骤

### 1. 检查API文档

请查看火山方舟控制台提供的API文档：
- 登录火山方舟控制台
- 找到"语音识别"服务
- 查看API文档和示例代码
- 确认WebSocket连接的正确格式

### 2. 测试API连接

创建一个简单的测试脚本：

```python
# test_speech_api.py
import asyncio
import websockets
from urllib.parse import urlencode

async def test_connection():
    # 方式1: 基本格式
    params = {
        'appid': '1356755714',
        'token': 'oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP',
        'model': 'Speech_Recognition_Seed_streaming2000000451913596898',
        'format': 'pcm',
        'rate': '16000'
    }
    
    url = f"wss://openspeech.bytedance.com/api/v1/asr?{urlencode(params)}"
    
    try:
        print(f"正在连接: {url[:100]}...")
        async with websockets.connect(url) as ws:
            print("✅ 连接成功!")
            # 可以尝试发送测试数据
    except Exception as e:
        print(f"❌ 连接失败: {e}")

asyncio.run(test_connection())
```

运行测试：
```bash
python test_speech_api.py
```

### 3. 根据错误信息调整

根据测试脚本的输出，调整 `services/speech_recognition_service.py` 中的：
- WebSocket URL
- 认证参数
- 连接头部信息

---

## 🔧 可能的API格式

### 格式1: 查询参数认证

```python
base_url = "wss://openspeech.bytedance.com/api/v1/asr"
params = {
    'appid': '1356755714',
    'token': 'oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP',
    'model': 'Speech_Recognition_Seed_streaming2000000451913596898'
}
```

### 格式2: Header认证

```python
base_url = "wss://openspeech.bytedance.com/api/v1/asr"
headers = {
    'Authorization': f'Bearer oPxND_k8BQJveNLg7Mdq9VXRvKgFnIlP',
    'X-App-Id': '1356755714'
}
```

### 格式3: 签名认证

```python
import hmac
import hashlib
import time

timestamp = int(time.time())
signature = hmac.new(
    secret_key.encode(),
    f"{app_id}{timestamp}".encode(),
    hashlib.sha256
).hexdigest()

params = {
    'appid': '1356755714',
    'timestamp': timestamp,
    'signature': signature
}
```

---

## 📋 当前代码位置

如果获得正确的API格式，需要修改以下文件：

**`services/speech_recognition_service.py`**
- 第 43-61 行：`_get_ws_url()` 方法
- 第 63-79 行：`connect()` 方法

---

## ✅ 成功标志

当API配置正确后，您应该看到：

**服务器控制台**：
```
[语音识别] 连接到: wss://openspeech...
[OK] 语音识别服务已连接
[语音识别] 临时结果: 你好
[语音识别] 最终结果: 你好，我想去北京旅游
```

**浏览器控制台**：
```
[语音识别] 服务器已启动: 语音识别已启动，请开始说话
[录音] 流式录音已启动 (PCM 16kHz)
[语音识别] 临时结果: 你好
```

---

## 📞 获取帮助

如果需要火山方舟API的官方支持：

1. **控制台文档**：登录火山方舟控制台查看API文档
2. **技术支持**：联系火山方舟技术支持团队
3. **示例代码**：查看官方提供的Python示例代码

---

## 🎯 下一步

1. **立即可用**：使用文字输入模式生成旅行计划
2. **长期修复**：获取正确的API文档，更新连接代码
3. **测试验证**：使用测试脚本验证API连接

---

**当前状态**：✅ 文字输入功能正常，⚠️ 语音识别功能待修复

