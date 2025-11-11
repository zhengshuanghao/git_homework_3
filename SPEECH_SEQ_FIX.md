# 语音识别序列号问题修复报告

## 问题描述

语音识别服务在重新连接时出现序列号不匹配错误：

```
autoAssignedSequence (1) mismatch sequence in request (3/4)
```

## 根本原因

在`SpeechRecognitionService`类中：
1. 序列号`self.seq`在初始化时设置为1
2. 每次发送请求后序列号递增
3. **问题**：当连接失败后重新连接时，序列号没有重置，导致服务器期望的序列号(1)与客户端发送的序列号(3/4)不匹配

## 修复方案

在两个关键位置重置序列号和音频缓冲区：

### 1. `connect()` 方法开始时

```python
async def connect(self):
    """建立 WebSocket 连接"""
    try:
        # 重置序列号和缓冲区
        self.seq = 1
        self.audio_buffer.clear()
        
        # ... 其余连接代码
```

### 2. `disconnect()` 方法中

```python
async def disconnect(self):
    """断开连接"""
    try:
        self.is_connected = False
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        if self.session:
            await self.session.close()
            self.session = None
        
        # 重置序列号和缓冲区
        self.seq = 1
        self.audio_buffer.clear()
        
        print("[OK] 语音识别连接已关闭")
```

## 修复效果

- ✅ 每次新连接都从序列号1开始
- ✅ 音频缓冲区被清空，避免旧数据干扰
- ✅ 解决了序列号不匹配的错误
- ✅ 支持多次重连而不会出现序列号问题

## 测试建议

1. 启动应用
2. 开始语音识别
3. 停止语音识别
4. 再次开始语音识别
5. 重复多次，确认不会出现序列号错误

## 相关文件

- `services/speech_recognition_service.py` - 已修复

## 注意事项

序列号管理是WebSocket协议的关键部分，必须确保：
- 每个新连接从1开始
- 每次发送后递增
- 断开连接后重置
