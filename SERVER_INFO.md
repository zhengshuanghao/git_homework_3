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
REMOVED: 内容已合并到 `README.md`。此文件为精简占位，原始文档已保存在 `README.md` 中。
使用 `run.py` 启动开发服务器：


