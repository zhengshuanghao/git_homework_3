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
REMOVED: 内容已合并到 `README.md`。此文件为精简占位，原始文档已保存在 `README.md` 中。
```


