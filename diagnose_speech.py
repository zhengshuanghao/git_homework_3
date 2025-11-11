"""
语音识别配置诊断工具
检查所有必需的配置是否正确设置
"""
import os
import sys
from dotenv import load_dotenv
import json

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 加载环境变量
load_dotenv()

print("=" * 60)
print("语音识别配置诊断")
print("=" * 60)

# 检查 .env 文件
print("\n1. 检查 .env 文件...")
if os.path.exists('.env'):
    print("   ✅ .env 文件存在")
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
        if 'SPEECH_APP_ID' in env_content:
            print("   ✅ 包含 SPEECH_APP_ID")
        else:
            print("   ❌ 缺少 SPEECH_APP_ID")
        
        if 'SPEECH_ACCESS_KEY' in env_content:
            print("   ✅ 包含 SPEECH_ACCESS_KEY")
        else:
            print("   ❌ 缺少 SPEECH_ACCESS_KEY")
        
        if 'SPEECH_SECRET_KEY' in env_content:
            print("   ✅ 包含 SPEECH_SECRET_KEY")
        else:
            print("   ❌ 缺少 SPEECH_SECRET_KEY")
else:
    print("   ❌ .env 文件不存在")

# 检查环境变量
print("\n2. 检查环境变量...")
speech_app_id = os.getenv('SPEECH_APP_ID', '')
speech_access_key = os.getenv('SPEECH_ACCESS_KEY', '')
speech_secret_key = os.getenv('SPEECH_SECRET_KEY', '')
speech_model_id = os.getenv('SPEECH_MODEL_ID', 'Speech_Recognition_Seed_streaming2000000451913596898')

if speech_app_id:
    print(f"   ✅ SPEECH_APP_ID: {speech_app_id[:10]}...")
else:
    print("   ❌ SPEECH_APP_ID 未设置")

if speech_access_key:
    print(f"   ✅ SPEECH_ACCESS_KEY: {speech_access_key[:10]}...")
else:
    print("   ❌ SPEECH_ACCESS_KEY 未设置")

if speech_secret_key:
    print(f"   ✅ SPEECH_SECRET_KEY: {speech_secret_key[:10]}...")
else:
    print("   ❌ SPEECH_SECRET_KEY 未设置")

print(f"   ℹ️  SPEECH_MODEL_ID: {speech_model_id}")

# 检查 config.json
print("\n3. 检查 config.json...")
if os.path.exists('config.json'):
    print("   ✅ config.json 文件存在")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if 'SPEECH_APP_ID' in config:
                print(f"   ✅ SPEECH_APP_ID: {config['SPEECH_APP_ID'][:10] if config['SPEECH_APP_ID'] else '(空)'}...")
            else:
                print("   ❌ 缺少 SPEECH_APP_ID")
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
else:
    print("   ⚠️  config.json 文件不存在（将使用环境变量）")

# 检查依赖
print("\n4. 检查依赖...")
try:
    import aiohttp
    print(f"   ✅ aiohttp 已安装 (版本: {aiohttp.__version__})")
except ImportError:
    print("   ❌ aiohttp 未安装")

try:
    import flask_socketio
    print(f"   ✅ flask-socketio 已安装")
except ImportError:
    print("   ❌ flask-socketio 未安装")

# 总结
print("\n" + "=" * 60)
print("诊断总结")
print("=" * 60)

issues = []
if not speech_app_id:
    issues.append("SPEECH_APP_ID 未设置")
if not speech_access_key:
    issues.append("SPEECH_ACCESS_KEY 未设置")
if not speech_secret_key:
    issues.append("SPEECH_SECRET_KEY 未设置")

if issues:
    print("\n❌ 发现以下问题：")
    for issue in issues:
        print(f"   - {issue}")
    print("\n📝 解决方法：")
    print("   1. 在 .env 文件中添加以下配置：")
    print("      SPEECH_APP_ID=你的APP_ID")
    print("      SPEECH_ACCESS_KEY=你的ACCESS_KEY")
    print("      SPEECH_SECRET_KEY=你的SECRET_KEY")
    print("   2. 或者在应用的设置页面中配置")
else:
    print("\n✅ 所有配置正确！")
    print("   如果语音识别仍然无法工作，请检查：")
    print("   - 浏览器麦克风权限")
    print("   - 网络连接")
    print("   - 服务器日志中的错误信息")

print("\n" + "=" * 60)
