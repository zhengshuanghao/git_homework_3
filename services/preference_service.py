"""
用户偏好设置服务
"""
from services.supabase_service import SupabaseService

class PreferenceService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_user_preferences(self, user_id):
        """获取用户偏好设置"""
        try:
            result = self.supabase.client.table('user_preferences').select('*').eq('user_id', user_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"获取用户偏好失败: {str(e)}")
            return None
    
    def save_user_preferences(self, user_id, preferences):
        """保存或更新用户偏好设置"""
        try:
            # 检查是否已存在
            existing = self.get_user_preferences(user_id)
            
            preference_data = {
                'user_id': user_id,
                'travel_style': preferences.get('travel_style', []),
                'accommodation_type': preferences.get('accommodation_type', []),
                'food_preference': preferences.get('food_preference', []),
                'transportation_preference': preferences.get('transportation_preference', []),
                'activity_preference': preferences.get('activity_preference', []),
                'budget_level': preferences.get('budget_level', ''),
                'pace': preferences.get('pace', ''),
                'special_requirements': preferences.get('special_requirements', '')
            }
            
            if existing:
                # 更新
                result = self.supabase.client.table('user_preferences').update(preference_data).eq('user_id', user_id).execute()
            else:
                # 插入
                result = self.supabase.client.table('user_preferences').insert(preference_data).execute()
            
            return {'success': True, 'data': result.data[0] if result.data else None}
        except Exception as e:
            print(f"保存用户偏好失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_user_preferences(self, user_id):
        """删除用户偏好设置"""
        try:
            self.supabase.client.table('user_preferences').delete().eq('user_id', user_id).execute()
            return {'success': True}
        except Exception as e:
            print(f"删除用户偏好失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def format_preferences_for_prompt(self, preferences):
        """将偏好设置格式化为提示词"""
        if not preferences:
            return ""
        
        prompt_parts = []
        
        # 旅行风格
        if preferences.get('travel_style'):
            styles = ', '.join(preferences['travel_style'])
            prompt_parts.append(f"旅行风格偏好：{styles}")
        
        # 住宿偏好
        if preferences.get('accommodation_type'):
            acc_types = ', '.join(preferences['accommodation_type'])
            prompt_parts.append(f"住宿偏好：{acc_types}")
        
        # 饮食偏好
        if preferences.get('food_preference'):
            food_prefs = ', '.join(preferences['food_preference'])
            prompt_parts.append(f"饮食偏好：{food_prefs}")
        
        # 交通偏好
        if preferences.get('transportation_preference'):
            trans_prefs = ', '.join(preferences['transportation_preference'])
            prompt_parts.append(f"交通偏好：{trans_prefs}")
        
        # 活动偏好
        if preferences.get('activity_preference'):
            act_prefs = ', '.join(preferences['activity_preference'])
            prompt_parts.append(f"活动偏好：{act_prefs}")
        
        # 预算等级
        if preferences.get('budget_level'):
            prompt_parts.append(f"预算等级：{preferences['budget_level']}")
        
        # 行程节奏
        if preferences.get('pace'):
            prompt_parts.append(f"行程节奏：{preferences['pace']}")
        
        # 特殊需求
        if preferences.get('special_requirements'):
            prompt_parts.append(f"特殊需求：{preferences['special_requirements']}")
        
        if prompt_parts:
            return "用户偏好设置：\n" + "\n".join(prompt_parts)
        return ""
