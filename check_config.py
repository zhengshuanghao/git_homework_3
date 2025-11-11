"""
检查配置文件
"""
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

print("=" * 60)
print("配置检查")
print("=" * 60)

print(f"\n火山方舟 DeepSeek 配置:")
print(f"  ARK_API_KEY: {Config.DEEPSEEK_API_KEY[:20]}... (长度: {len(Config.DEEPSEEK_API_KEY)})")
print(f"  ARK_BASE_URL: {Config.ARK_BASE_URL}")
print(f"  DEEPSEEK_MODEL: {Config.DEEPSEEK_MODEL}")

print(f"\n语音识别配置:")
print(f"  SPEECH_APP_ID: {'已设置' if Config.SPEECH_APP_ID else '未设置'}")
print(f"  SPEECH_ACCESS_KEY: {'已设置' if Config.SPEECH_ACCESS_KEY else '未设置'}")
print(f"  SPEECH_SECRET_KEY: {'已设置' if Config.SPEECH_SECRET_KEY else '未设置'}")

print(f"\n高德地图配置:")
print(f"  AMAP_API_KEY: {'已设置' if Config.AMAP_API_KEY else '未设置'}")

print(f"\nSupabase配置:")
print(f"  SUPABASE_URL: {'已设置' if Config.SUPABASE_URL else '未设置'}")
print(f"  SUPABASE_KEY: {'已设置' if Config.SUPABASE_KEY else '未设置'}")

print("\n" + "=" * 60)
