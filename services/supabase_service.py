"""
Supabase服务 - 用户认证和数据存储
"""
from supabase import create_client, Client
from config import Config
import json
from datetime import datetime


class SupabaseService:
    """Supabase服务类"""
    
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.client: Client = None
        
        if self.is_configured():
            try:
                # 尝试标准初始化方式
                self.client = create_client(self.url, self.key)
            except Exception as e:
                # 如果初始化失败，记录错误但不阻止应用启动
                error_msg = str(e)
                if 'proxy' in error_msg.lower():
                    print(f"Supabase初始化失败: {error_msg}")
                    print("提示: 这可能是supabase-py库版本兼容性问题。")
                    print("建议: 运行 'pip install --upgrade supabase' 或使用虚拟环境。")
                    print("应用将继续运行，但Supabase功能将不可用。")
                else:
                    print(f"Supabase初始化失败: {error_msg}")
                self.client = None
    
    def is_configured(self):
        """检查配置是否完整"""
        return bool(self.url and self.key)
    
    def login(self, email, password):
        """用户登录"""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    'id': response.user.id,
                    'email': response.user.email,
                    'access_token': response.session.access_token if response.session else None
                }
            return None
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return None
    
    def register(self, email, password, name=''):
        """用户注册"""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if response.user:
                return {
                    'id': response.user.id,
                    'email': response.user.email
                }
            return None
        except Exception as e:
            print(f"注册失败: {str(e)}")
            return None
    
    def save_travel_plan(self, user_id, plan, user_input):
        """保存旅行计划"""
        if not self.client:
            return None
        
        try:
            # 确保travel_plans表存在（如果不存在，需要在Supabase中创建）
            data = {
                'user_id': user_id,
                'user_input': user_input,
                'plan_data': json.dumps(plan, ensure_ascii=False),
                'destination': plan.get('destination', ''),
                'duration': plan.get('duration', ''),
                'budget': plan.get('total_budget', 0),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('travel_plans').insert(data).execute()
            if result.data:
                return result.data[0].get('id')
            return None
        except Exception as e:
            print(f"保存旅行计划失败: {str(e)}")
            # 如果表不存在，返回一个模拟ID
            return f"plan_{user_id}_{int(datetime.now().timestamp())}"
    
    def get_travel_plans(self, user_id):
        """获取用户的旅行计划列表"""
        if not self.client:
            return []
        
        try:
            result = self.client.table('travel_plans').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取旅行计划失败: {str(e)}")
            return []
    
    def get_travel_plan(self, plan_id):
        """获取单个旅行计划"""
        if not self.client:
            return None
        
        try:
            result = self.client.table('travel_plans').select('*').eq('id', plan_id).execute()
            if result.data:
                plan = result.data[0]
                # 解析plan_data
                if isinstance(plan.get('plan_data'), str):
                    plan['plan_data'] = json.loads(plan['plan_data'])
                return plan
            return None
        except Exception as e:
            print(f"获取旅行计划失败: {str(e)}")
            return None
    
    def add_expense(self, user_id, plan_id, expense):
        """添加费用记录"""
        if not self.client:
            return None
        
        try:
            data = {
                'user_id': user_id,
                'plan_id': plan_id,
                'expense_data': json.dumps(expense, ensure_ascii=False),
                'amount': expense.get('amount', 0),
                'category': expense.get('category', '其他'),
                'description': expense.get('description', ''),
                'date': expense.get('date', datetime.now().isoformat()),
                'created_at': datetime.now().isoformat()
            }
            
            result = self.client.table('expenses').insert(data).execute()
            if result.data:
                return result.data[0].get('id')
            return None
        except Exception as e:
            print(f"添加费用记录失败: {str(e)}")
            return f"expense_{user_id}_{int(datetime.now().timestamp())}"
    
    def get_expenses(self, user_id, plan_id=None):
        """获取费用记录"""
        if not self.client:
            return []
        
        try:
            query = self.client.table('expenses').select('*').eq('user_id', user_id)
            if plan_id:
                query = query.eq('plan_id', plan_id)
            result = query.order('date', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取费用记录失败: {str(e)}")
            return []




