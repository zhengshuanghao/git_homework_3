-- Supabase数据库表结构

-- 用户旅游偏好设置表
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    travel_style TEXT[], -- 旅行风格：['休闲', '探险', '文化', '美食', '购物', '自然']
    accommodation_type TEXT[], -- 住宿偏好：['经济型', '舒适型', '豪华型', '民宿', '酒店', '青旅']
    food_preference TEXT[], -- 饮食偏好：['中餐', '西餐', '日韩料理', '东南亚菜', '素食', '清真']
    transportation_preference TEXT[], -- 交通偏好：['公共交通', '出租车', '租车', '步行', '自行车']
    activity_preference TEXT[], -- 活动偏好：['博物馆', '景点', '户外', '购物', '美食探店', '夜生活']
    budget_level TEXT, -- 预算等级：'经济', '中等', '高端'
    pace TEXT, -- 行程节奏：'轻松', '适中', '紧凑'
    special_requirements TEXT, -- 特殊需求（如无障碍、带小孩等）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 旅行计划表
CREATE TABLE IF NOT EXISTS travel_plans (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    user_input TEXT,
    plan_data JSONB,
    destination TEXT,
    duration TEXT,
    budget NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 费用记录表
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    plan_id INTEGER REFERENCES travel_plans(id) ON DELETE CASCADE,
    expense_data JSONB,
    amount NUMERIC,
    category TEXT,
    description TEXT,
    date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_travel_plans_user_id ON travel_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_travel_plans_created_at ON travel_plans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_plan_id ON expenses(plan_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date DESC);

-- 启用Row Level Security (RLS) - 可选
-- 注意：如果使用Supabase Auth，启用RLS；如果使用自定义认证，可以禁用RLS
-- ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE travel_plans ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- 如果启用了RLS，需要创建策略
-- 如果使用Supabase Auth，使用以下策略：

-- 用户偏好策略
-- CREATE POLICY "Users can view own preferences" ON user_preferences
--     FOR SELECT USING (auth.uid() = user_id);
-- CREATE POLICY "Users can insert own preferences" ON user_preferences
--     FOR INSERT WITH CHECK (auth.uid() = user_id);
-- CREATE POLICY "Users can update own preferences" ON user_preferences
--     FOR UPDATE USING (auth.uid() = user_id);
-- CREATE POLICY "Users can delete own preferences" ON user_preferences
--     FOR DELETE USING (auth.uid() = user_id);

-- 旅行计划策略
-- CREATE POLICY "Users can view own travel plans" ON travel_plans
--     FOR SELECT USING (auth.uid() = user_id);
-- CREATE POLICY "Users can insert own travel plans" ON travel_plans
--     FOR INSERT WITH CHECK (auth.uid() = user_id);
-- CREATE POLICY "Users can update own travel plans" ON travel_plans
--     FOR UPDATE USING (auth.uid() = user_id);
-- CREATE POLICY "Users can delete own travel plans" ON travel_plans
--     FOR DELETE USING (auth.uid() = user_id);

-- 费用记录策略
-- CREATE POLICY "Users can view own expenses" ON expenses
--     FOR SELECT USING (auth.uid() = user_id);
-- CREATE POLICY "Users can insert own expenses" ON expenses
--     FOR INSERT WITH CHECK (auth.uid() = user_id);
-- CREATE POLICY "Users can update own expenses" ON expenses
--     FOR UPDATE USING (auth.uid() = user_id);
-- CREATE POLICY "Users can delete own expenses" ON expenses
--     FOR DELETE USING (auth.uid() = user_id);

-- 临时解决方案：禁用RLS或使用service_role key
-- 在Supabase控制台执行以下命令禁用RLS：
ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;










