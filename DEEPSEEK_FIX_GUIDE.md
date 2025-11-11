# DeepSeek 火山方舟配置修复指南

## 问题诊断

当前错误：`AuthenticationError: The API key format is incorrect`

**根本原因**：模型ID配置错误。火山方舟需要使用**接入点ID（endpoint_id）**，而不是模型名称。

## 当前配置（错误）

```env
ARK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DEEPSEEK_MODEL=deepseek-v3-1-250821  ❌ 这不是正确的格式
```

## 正确配置步骤

### 1. 登录火山方舟控制台

访问：https://console.volcengine.com/ark

### 2. 创建推理接入点

1. 点击左侧菜单 **"在线推理"**
2. 点击 **"创建推理接入点"**
3. 输入接入点名称（例如：`DeepSeek-V3-接入点`）
4. 点击 **"添加模型"**
5. 选择 **DeepSeek-V3** 模型
6. 点击 **"确认"** 添加模型
7. 点击 **"确认接入"** 完成创建

### 3. 获取接入点ID

创建完成后，在接入点列表中会显示你创建的接入点。

**重要**：复制接入点ID，格式类似：`ep-20250111-xxxxx`

### 4. 更新.env配置

将.env文件中的`DEEPSEEK_MODEL`改为你复制的接入点ID：

```env
ARK_API_KEY=sk-ef1bae9821a140baaafca8f4ed3495bb
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DEEPSEEK_MODEL=ep-20250111-xxxxx  ✓ 使用你的接入点ID
```

### 5. 重启应用

更新配置后，重启Flask应用：

```bash
python run.py
```

## 验证配置

运行测试脚本验证配置：

```bash
python test_deepseek.py
```

如果配置正确，应该能成功生成旅行计划。

## 常见问题

### Q1: 找不到接入点ID在哪里？

A: 在火山方舟控制台 -> 在线推理 -> 推理接入点列表中，每个接入点都有一个ID，通常以`ep-`开头。

### Q2: API Key在哪里获取？

A: 火山方舟控制台 -> 左下角 "API Key管理" -> 创建API Key

### Q3: 还是报401错误？

A: 请检查：
- API Key是否正确（不要有多余的空格）
- 接入点ID是否正确
- 接入点是否已经激活
- 账户是否有足够的额度

### Q4: 如何查看接入点详情？

A: 在接入点列表中点击接入点名称，可以看到：
- 接入点ID
- 使用的模型
- API调用示例
- 调用统计

## 参考资料

- 火山方舟文档：https://www.volcengine.com/docs/82379/1273557
- 火山方舟控制台：https://console.volcengine.com/ark

## 修复后的代码改动

已修复的文件：
- ✅ `app.py` - 修复了配置属性名错误（DEEPSEEK_BASE_URL -> ARK_BASE_URL）
- ✅ `requirements.txt` - 添加了火山方舟SDK依赖
- ✅ `config.py` - 配置读取正确

只需要更新.env文件中的`DEEPSEEK_MODEL`为正确的接入点ID即可。
