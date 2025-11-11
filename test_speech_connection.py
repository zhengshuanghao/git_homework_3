"""
测试火山方舟语音识别服务连接
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 加载环境变量
load_dotenv()

# 导入语音识别服务
from services.speech_recognition_service import SpeechRecognitionService

async def test_connection():
    """测试连接"""
    print("=" * 60)
    print("测试火山方舟语音识别服务连接")
    print("=" * 60)
    
    # 获取配置
    app_id = os.getenv('SPEECH_APP_ID', '')
    access_key = os.getenv('SPEECH_ACCESS_KEY', '')
    secret_key = os.getenv('SPEECH_SECRET_KEY', '')
    model_id = os.getenv('SPEECH_MODEL_ID', 'Speech_Recognition_Seed_streaming2000000451913596898')
    
    if not app_id or not access_key or not secret_key:
        print("\n❌ 错误：缺少必需的配置")
        print("   请在 .env 文件中设置：")
        print("   - SPEECH_APP_ID")
        print("   - SPEECH_ACCESS_KEY")
        print("   - SPEECH_SECRET_KEY")
        return False
    
    print(f"\n配置信息：")
    print(f"  APP_ID: {app_id[:10]}...")
    print(f"  ACCESS_KEY: {access_key[:10]}...")
    print(f"  SECRET_KEY: {secret_key[:10]}...")
    print(f"  MODEL_ID: {model_id}")
    
    # 创建服务实例
    print("\n正在创建服务实例...")
    service = SpeechRecognitionService(app_id, access_key, secret_key, model_id)
    
    # 设置回调
    results = []
    errors = []
    
    def on_result(result):
        results.append(result)
        print(f"\n✅ 收到识别结果: {result}")
    
    def on_error(error):
        errors.append(error)
        print(f"\n❌ 收到错误: {error}")
    
    service.set_callbacks(on_result, on_error)
    
    # 尝试连接
    print("\n正在连接到火山方舟语音识别服务...")
    try:
        await service.connect()
        print("\n✅ 连接成功！")
        print("   服务已准备好接收音频数据")
        
        # 等待一小段时间
        await asyncio.sleep(2)
        
        # 断开连接
        print("\n正在断开连接...")
        await service.disconnect()
        print("✅ 已断开连接")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n开始测试...\n")
    success = asyncio.run(test_connection())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过！语音识别服务可以正常连接")
        print("\n下一步：")
        print("  1. 启动应用: python run.py")
        print("  2. 打开浏览器: http://localhost:8080")
        print("  3. 点击'语音输入'标签")
        print("  4. 点击'开始录音'按钮")
        print("  5. 说出旅行需求")
    else:
        print("❌ 测试失败！请检查：")
        print("  1. 网络连接是否正常")
        print("  2. API凭证是否正确")
        print("  3. 防火墙是否阻止了连接")
    print("=" * 60)
