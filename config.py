"""
配置文件管理
从环境变量或配置文件读取API密钥
"""
import os
import json
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 科大讯飞配置
    IFLYTEK_APP_ID = os.getenv('IFLYTEK_APP_ID', '')
    IFLYTEK_API_KEY = os.getenv('IFLYTEK_API_KEY', '')
    IFLYTEK_API_SECRET = os.getenv('IFLYTEK_API_SECRET', '')
    
    # 高德地图配置
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', '')
    AMAP_API_SECRET = os.getenv('AMAP_API_SECRET', '')
    
    # 火山方舟配置
    DEEPSEEK_API_KEY = os.getenv('ARK_API_KEY', '')
    # Ark REST base URL，用于回退请求
    ARK_BASE_URL = os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
    # 使用的模型 ID
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-v3-1-250821')

    # Supabase配置
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    @classmethod
    def load_from_file(cls, filepath='config.json'):
        """从JSON文件加载配置"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(cls, key.upper()):
                            setattr(cls, key.upper(), value)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    @classmethod
    def save_to_file(cls, filepath='config.json'):
        """保存配置到JSON文件"""
        config_data = {
            'IFLYTEK_APP_ID': cls.IFLYTEK_APP_ID,
            'IFLYTEK_API_KEY': cls.IFLYTEK_API_KEY,
            'IFLYTEK_API_SECRET': cls.IFLYTEK_API_SECRET,
            'AMAP_API_KEY': cls.AMAP_API_KEY,
            'AMAP_API_SECRET': cls.AMAP_API_SECRET,
            'DEEPSEEK_API_KEY': cls.DEEPSEEK_API_KEY,
            'ARK_BASE_URL': cls.ARK_BASE_URL,
            'DEEPSEEK_MODEL': cls.DEEPSEEK_MODEL,
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_KEY': cls.SUPABASE_KEY,
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    @classmethod
    def update_config(cls, config_dict):
        """更新配置"""
        for key, value in config_dict.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)




