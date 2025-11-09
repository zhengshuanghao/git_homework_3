# 服务器启动说明

## 关于警告信息

当你看到以下警告信息时，**这是正常的**，不是错误：

```
Werkzeug appears to be used in a production deployment.
WARNING: This is a development server.
```

这些是 Flask 开发服务器的标准提示信息，提醒你这是开发环境，不应该在生产环境使用。

## 应用状态

如果看到以下信息，说明应用已**成功启动**：

```
 * Running on http://127.0.0.1:8080
 * Running on http://10.36.10.87:8080
 * Debugger is active!
```

应用现在可以通过以下地址访问：
- `http://localhost:8080`
- `http://127.0.0.1:8080`
- `http://10.36.10.87:8080` (局域网地址)

## 启动方式

### 1. 开发环境（推荐）

使用 `run.py` 启动开发服务器：

```bash
python run.py
```

**特点**：
- 支持热重载（代码修改自动重启）
- 支持调试模式
- 完整的 WebSocket 支持
- 适合开发和测试

### 2. 抑制警告信息

如果你不想看到警告信息，可以使用修改后的 `run.py`，它已经抑制了这些警告。

### 3. 生产环境（可选）

如果需要部署到生产环境，建议使用专业的 WSGI 服务器：

#### Windows: 使用 Waitress

```bash
pip install waitress
python start.py
```

#### Linux/Mac: 使用 Gunicorn

```bash
pip install gunicorn eventlet
gunicorn -w 4 -k eventlet -b 0.0.0.0:8080 app:app
```

## 常见问题

### Q: 警告信息会影响功能吗？

**A:** 不会。这些只是提示信息，不影响应用功能。

### Q: 如何消除这些警告？

**A:** 
1. 使用修改后的 `run.py`（已抑制警告）
2. 或者设置环境变量：`export FLASK_ENV=development`

### Q: 可以在生产环境使用开发服务器吗？

**A:** **不建议**。开发服务器（Werkzeug）不适合生产环境，因为：
- 性能较低
- 安全性较差
- 不支持多进程

生产环境应使用 Gunicorn、uWSGI 或 Waitress 等专业服务器。

### Q: 如何判断应用是否正常启动？

**A:** 如果看到以下信息，说明启动成功：
- `Running on http://127.0.0.1:8080`
- `Debugger is active!`
- 没有错误信息（Error/Traceback）

然后打开浏览器访问 `http://localhost:8080`，如果能看到页面，说明一切正常。

## 当前状态

根据你提供的日志，应用已经**成功启动**：
- ✅ 服务器运行在 8080 端口
- ✅ 调试模式已激活
- ✅ 可以通过多个地址访问

现在可以：
1. 打开浏览器访问 `http://localhost:8080`
2. 开始使用 AI 旅行规划师功能
3. 测试语音识别、行程生成等功能

## 总结

**这些警告信息是正常的，可以安全忽略。** 应用已经成功启动并运行。如果担心警告信息，可以使用修改后的 `run.py`，它已经抑制了这些警告输出。

