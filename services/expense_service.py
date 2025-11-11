"""
费用记录服务
"""
from services.supabase_service import SupabaseService
from datetime import datetime

class ExpenseService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_user_expenses(self, user_id, plan_id=None):
        """获取用户的费用记录"""
        try:
            query = self.supabase.client.table('expenses').select('*').eq('user_id', user_id)
            
            if plan_id:
                query = query.eq('plan_id', plan_id)
            
            result = query.order('date', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取费用记录失败: {str(e)}")
            return []
    
    def add_expense(self, user_id, expense_data):
        """添加费用记录"""
        try:
            data = {
                'user_id': user_id,
                'plan_id': expense_data.get('plan_id'),
                'amount': expense_data.get('amount'),
                'category': expense_data.get('category'),
                'description': expense_data.get('description'),
                'date': expense_data.get('date', datetime.now().isoformat()),
                'expense_data': expense_data.get('expense_data', {})
            }
            
            result = self.supabase.client.table('expenses').insert(data).execute()
            return {'success': True, 'data': result.data[0] if result.data else None}
        except Exception as e:
            print(f"添加费用记录失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_expense(self, expense_id, user_id, expense_data):
        """更新费用记录"""
        try:
            data = {
                'amount': expense_data.get('amount'),
                'category': expense_data.get('category'),
                'description': expense_data.get('description'),
                'date': expense_data.get('date'),
                'expense_data': expense_data.get('expense_data', {})
            }
            
            result = self.supabase.client.table('expenses').update(data).eq('id', expense_id).eq('user_id', user_id).execute()
            return {'success': True, 'data': result.data[0] if result.data else None}
        except Exception as e:
            print(f"更新费用记录失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_expense(self, expense_id, user_id):
        """删除费用记录"""
        try:
            self.supabase.client.table('expenses').delete().eq('id', expense_id).eq('user_id', user_id).execute()
            return {'success': True}
        except Exception as e:
            print(f"删除费用记录失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_expense_summary(self, user_id, plan_id=None):
        """获取费用汇总"""
        try:
            expenses = self.get_user_expenses(user_id, plan_id)
            
            if not expenses:
                return {
                    'total': 0,
                    'by_category': {},
                    'count': 0
                }
            
            total = sum(float(exp['amount']) for exp in expenses if exp.get('amount'))
            
            # 按类别统计
            by_category = {}
            for exp in expenses:
                category = exp.get('category', '其他')
                amount = float(exp.get('amount', 0))
                if category in by_category:
                    by_category[category] += amount
                else:
                    by_category[category] = amount
            
            return {
                'total': total,
                'by_category': by_category,
                'count': len(expenses)
            }
        except Exception as e:
            print(f"获取费用汇总失败: {str(e)}")
            return {
                'total': 0,
                'by_category': {},
                'count': 0
            }
