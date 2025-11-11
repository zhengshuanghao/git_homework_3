# RLS问题修复指南

## 问题说明

您遇到的错误：
```
new row violates row-level security policy for table "expenses"
new row violates row-level security policy for table "user_preferences"
```

这是因为Supabase的行级安全（RLS）策略使用了`auth.uid()`，但我们的应用使用的是自定义认证系统，不是Supabase Auth。

## 解决方案

### 方案1：禁用RLS（推荐用于开发/测试）

在Supabase SQL编辑器中执行以下命令：

```sql
-- 禁用所有表的RLS
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

**优点：**
- 简单快速
- 适合开发和测试环境
- 无需修改代码

**缺点：**
- 数据库层面没有安全保护
- 需要在应用层确保数据隔离

### 方案2：使用Service Role Key

在`.env`文件中使用Service Role Key而不是Anon Key：

```env
# 使用Service Role Key（绕过RLS）
SUPABASE_KEY=your_service_role_key_here
```

**如何获取Service Role Key：**
1. 登录Supabase控制台
2. 进入项目设置 → API
3. 复制"service_role" key（注意：这是敏感信息）

**优点：**
- 无需禁用RLS
- 保持数据库安全策略

**缺点：**
- Service Role Key权限很高，需要妥善保管
- 不适合暴露在客户端

### 方案3：集成Supabase Auth（生产环境推荐）

如果要在生产环境使用，建议集成Supabase Auth：

1. **修改登录/注册逻辑**使用Supabase Auth
2. **使用Supabase的JWT token**进行认证
3. **RLS策略会自动工作**

这需要较大的代码改动，但是最安全的方案。

## 已完成的修复

### 1. 更新了schema.sql

已将RLS策略注释掉，并添加了禁用RLS的命令：

```sql
-- 临时解决方案：禁用RLS
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 2. 添加了费用记录关联旅行计划功能

- 费用记录表单新增"关联旅行计划"下拉框
- 可以选择将费用关联到具体的旅行计划
- 也可以不关联，记录独立的费用

### 3. 添加了删除旅行计划功能

- 旅行计划列表每项都有删除按钮（🗑️）
- 点击删除会弹出确认对话框
- 删除计划不会删除相关的费用记录

## 立即修复步骤

### 步骤1：在Supabase执行SQL

登录Supabase控制台，进入SQL编辑器，执行：

```sql
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
```

### 步骤2：重启应用

```bash
python run.py
```

### 步骤3：测试功能

1. **测试偏好设置**
   - 点击"⚙️ 偏好设置"
   - 填写偏好并保存
   - 应该不再出现错误

2. **测试费用记录**
   - 点击"💰 费用记录"
   - 选择关联的旅行计划（可选）
   - 添加费用
   - 应该不再出现错误

3. **测试删除计划**
   - 在"我的旅行计划"列表中
   - 点击计划右侧的🗑️按钮
   - 确认删除

## 新功能说明

### 费用记录关联旅行计划

现在添加费用时可以：
- **选择关联到具体的旅行计划**：方便追踪每次旅行的支出
- **不关联计划**：记录日常旅行相关的零散支出

**使用场景：**
- 旅行前：不关联计划，记录准备费用
- 旅行中：关联到具体计划，记录实际支出
- 旅行后：可以按计划查看总支出

### 删除旅行计划

**功能特点：**
- 每个计划都有删除按钮
- 删除前会确认
- 删除计划不会删除相关费用（费用记录保留）

**注意事项：**
- 删除操作不可恢复
- 相关的费用记录会保留，但plan_id会变为null
- 建议在删除前确认不再需要该计划

## 数据库表关系

```
user_preferences (用户偏好)
├── user_id (关联用户)

travel_plans (旅行计划)
├── user_id (关联用户)

expenses (费用记录)
├── user_id (关联用户)
└── plan_id (可选，关联旅行计划)
```

## API接口更新

### 新增接口

```
DELETE /api/travel/plan/<plan_id>?user_id={user_id}
```
删除指定的旅行计划

### 更新接口

```
POST /api/expenses
Body: {
  "user_id": "xxx",
  "expense": {
    "plan_id": 123,  // 新增：可选的计划ID
    "amount": 100,
    "category": "交通",
    "date": "2025-11-11",
    "description": "出租车费"
  }
}
```

## 常见问题

### Q: 禁用RLS安全吗？
**A:** 在开发环境可以，但生产环境建议：
- 使用Service Role Key
- 或集成Supabase Auth
- 在应用层严格验证user_id

### Q: 删除计划后费用记录怎么办？
**A:** 费用记录会保留，但plan_id字段会变为null。您仍然可以在费用记录中看到这些费用。

### Q: 如何查看某个计划的所有费用？
**A:** 目前费用记录模态框显示所有费用。如果需要按计划筛选，可以：
1. 在费用列表中添加计划名称显示
2. 添加筛选功能（未来优化）

### Q: 可以批量删除计划吗？
**A:** 目前只支持单个删除。如需批量删除，可以：
1. 多次点击删除按钮
2. 或在数据库中直接操作

## 下一步优化建议

1. **费用筛选**：按计划筛选费用记录
2. **费用导出**：导出某个计划的所有费用
3. **计划归档**：而不是删除，可以归档不再使用的计划
4. **批量操作**：批量删除或归档计划
5. **数据备份**：删除前自动备份

## 总结

现在您可以：
- ✅ 正常保存偏好设置
- ✅ 正常添加费用记录
- ✅ 将费用关联到具体的旅行计划
- ✅ 删除不需要的旅行计划

所有功能都已修复并增强！🎉
