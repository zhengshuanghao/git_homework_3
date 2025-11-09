"""
配置检查工具
用于查看当前Flask应用的配置状态
"""
import os
from config import Config

def print_config():
    """打印所有配置信息"""
    print("=" * 60)
    print("Flask 配置信息")
    print("=" * 60)
    
    print("\n【Flask配置】")
    print(f"  SECRET_KEY: {'已设置' if Config.SECRET_KEY else '未设置'}")
    print(f"  ENV: {os.getenv('FLASK_ENV', '未设置')}")
    
    print("\n【科大讯飞配置】")
    print(f"  APP_ID: {'已设置' if Config.IFLYTEK_APP_ID else '未设置'} ({Config.IFLYTEK_APP_ID[:10] + '...' if Config.IFLYTEK_APP_ID else 'None'})")
    print(f"  API_KEY: {'已设置' if Config.IFLYTEK_API_KEY else '未设置'}")
    print(f"  API_SECRET: {'已设置' if Config.IFLYTEK_API_SECRET else '未设置'}")
    
    print("\n【高德地图配置】")
    print(f"  API_KEY: {'已设置' if Config.AMAP_API_KEY else '未设置'} ({Config.AMAP_API_KEY[:10] + '...' if Config.AMAP_API_KEY else 'None'})")
    print(f"  API_SECRET: {'已设置' if Config.AMAP_API_SECRET else '未设置'}")
    
    print("\n【DeepSeek配置】")
    print(f"  API_KEY: {'已设置' if Config.DEEPSEEK_API_KEY else '未设置'}")
    print(f"  BASE_URL: {Config.DEEPSEEK_BASE_URL}")
    
    print("\n【Supabase配置】")
    print(f"  URL: {'已设置' if Config.SUPABASE_URL else '未设置'}")
    if Config.SUPABASE_URL:
        print(f"    {Config.SUPABASE_URL}")
    print(f"  KEY: {'已设置' if Config.SUPABASE_KEY else '未设置'}")
    
    print("\n【环境变量来源】")
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"  [OK] .env 文件存在: {os.path.abspath(env_file)}")
    else:
        print(f"  [X] .env 文件不存在")
    
    config_file = 'config.json'
    if os.path.exists(config_file):
        print(f"  [OK] config.json 文件存在: {os.path.abspath(config_file)}")
    else:
        print(f"  [X] config.json 文件不存在")
    
    print("\n" + "=" * 60)
    
    # 检查配置完整性
    print("\n【配置完整性检查】")
    missing = []
    if not Config.IFLYTEK_APP_ID:
        missing.append("科大讯飞 APP_ID")
    if not Config.IFLYTEK_API_KEY:
        missing.append("科大讯飞 API_KEY")
    if not Config.AMAP_API_KEY:
        missing.append("高德地图 API_KEY")
    if not Config.DEEPSEEK_API_KEY:
        missing.append("DeepSeek API_KEY")
    if not Config.SUPABASE_URL:
        missing.append("Supabase URL")
    
    if missing:
        print("  [WARNING] 以下配置缺失:")
        for item in missing:
            print(f"    - {item}")
    else:
        print("  [OK] 所有必需配置已设置")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    # 加载配置文件
    Config.load_from_file()
    print_config()

