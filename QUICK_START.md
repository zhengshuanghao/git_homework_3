# 快速启动指南

## 🚀 立即开始

### 1. 数据库配置（首次使用）

在Supabase控制台执行以下SQL：

```sql
-- 创建用户偏好表
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    travel_style TEXT[],
    accommodation_type TEXT[],
    food_preference TEXT[],
    transportation_preference TEXT[],
    activity_preference TEXT[],
    budget_level TEXT,
    pace TEXT,
    special_requirements TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- 启用RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own preferences" ON user_preferences
    FOR DELETE USING (auth.uid() = user_id);
```

### 2. 启动应用

```bash
python run.py
```

或使用快捷方式：
```bash
快速启动.bat
```

### 3. 访问应用

打开浏览器访问：
```
http://localhost:8080
```

---

## 📋 功能清单

### ✅ 已实现的功能

#### 前端界面
- [x] 紧凑的欢迎页面
- [x] 登录/注册系统
- [x] 主应用界面
- [x] 偏好设置模态框
- [x] 费用记录模态框

#### 核心功能
- [x] 文字输入旅行需求
- [x] 语音输入旅行需求
- [x] AI生成旅行计划
- [x] 地图展示行程
- [x] 旅行计划列表

#### 新增功能
- [x] 旅游偏好设置（8大类）
- [x] 费用记录管理
- [x] 费用汇总统计
- [x] 智能推荐（结合偏好）
- [x] 具体酒店推荐
- [x] 具体餐厅推荐

---

## 🎯 使用流程

### 第一次使用

1. **注册账号**
   - 访问首页
   - 点击"注册"
   - 填写邮箱和密码
   - 自动跳转到主应用

2. **设置偏好**（推荐）
   - 点击导航栏"⚙️ 偏好设置"
   - 选择您的旅行偏好
   - 保存设置

3. **生成旅行计划**
   - 输入旅行需求（例如："我想去北京3天，预算5000元"）
   - 点击"生成旅行计划"
   - 查看AI生成的详细计划

4. **记录费用**（旅行中）
   - 点击导航栏"💰 费用记录"
   - 添加实际支出
   - 查看费用统计

---

## 💡 使用技巧

### 1. 偏好设置技巧
- **多选项目**：可以选择多个，AI会综合考虑
- **预算等级**：影响酒店和餐厅档次
- **行程节奏**：影响每天的活动安排
- **特殊需求**：详细描述，AI会特别关注

### 2. 生成计划技巧
- **明确需求**：目的地、天数、预算、人数
- **提及偏好**：即使设置了偏好，也可以在输入中强调
- **具体要求**：如"需要具体的酒店名称和地址"

### 3. 费用记录技巧
- **及时记录**：当天记录，避免遗忘
- **分类清晰**：选择正确的类别便于统计
- **添加描述**：方便后续查看

---

## 🔧 配置检查

### 必需配置（.env文件）

```env
# Supabase配置
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 火山方舟DeepSeek配置
ARK_API_KEY=your_ark_api_key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DEEPSEEK_MODEL=your_endpoint_id

# 语音识别配置
SPEECH_APP_ID=your_app_id
SPEECH_ACCESS_KEY=your_access_key
SPEECH_SECRET_KEY=your_secret_key

# 高德地图配置
AMAP_API_KEY=your_amap_key
```

### 检查配置状态

访问：`http://localhost:8080/api/config/all`

---

## 📊 数据库表结构

### user_preferences（新增）
- 用户偏好设置
- 每个用户一条记录
- 支持更新

### travel_plans（已有）
- 旅行计划
- 关联用户ID
- 存储JSON格式计划

### expenses（已有）
- 费用记录
- 可关联计划
- 支持分类统计

---

## 🐛 常见问题

### Q: 偏好设置保存后不生效？
**A:** 需要重新生成旅行计划，不是查看旧计划。

### Q: 费用记录无法添加？
**A:** 检查是否已登录，Supabase配置是否正确。

### Q: 酒店餐厅推荐不具体？
**A:** 在输入中明确要求："请推荐具体的酒店名称和地址"。

### Q: 语音识别不工作？
**A:** 检查麦克风权限，确保使用HTTPS或localhost。

---

## 📝 更新内容

### 本次更新（2025-11-11）

#### 界面优化
- ✅ 首页更紧凑（减少30%空白）
- ✅ 导航栏新增2个功能按钮
- ✅ 新增2个大型模态框

#### 功能新增
- ✅ 旅游偏好设置（8大类，30+选项）
- ✅ 费用记录管理（增删查改）
- ✅ 费用汇总统计（总额+分类）
- ✅ AI推荐增强（结合偏好）

#### 技术改进
- ✅ 新增2个Python服务
- ✅ 新增6个API接口
- ✅ 新增1个数据库表
- ✅ 新增270+行JavaScript
- ✅ 新增300+行CSS

---

## 🎉 开始使用

1. 确保数据库已更新（执行上面的SQL）
2. 启动应用：`python run.py`
3. 访问：`http://localhost:8080`
4. 注册/登录
5. 设置偏好
6. 生成计划
7. 记录费用

**祝您使用愉快！** ✈️🗺️💰
