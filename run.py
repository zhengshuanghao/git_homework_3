"""
启动脚本
"""
import os
import sys

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

from app import app, socketio
from config import Config

if __name__ == '__main__':
    # 加载配置文件
    Config.load_from_file()
    
    # 检查必要的配置（语音识别版本）
    missing_configs = []
    if not Config.SPEECH_APP_ID:
        missing_configs.append("语音识别 APP ID")
    if not Config.SPEECH_ACCESS_KEY:
        missing_configs.append("语音识别 Access Key")
    if not Config.AMAP_API_KEY:
        missing_configs.append("高德地图 API Key")
    if not Config.DEEPSEEK_API_KEY:
        missing_configs.append("DeepSeek API Key")
    
    if missing_configs:
        print("警告: 以下配置未设置，某些功能可能无法使用:")
        for config in missing_configs:
            print(f"  - {config}")
        print("\n请在设置页面或.env文件中配置API密钥。")
        print("按 Enter 继续启动，或 Ctrl+C 退出...")
        try:
            input()
        except KeyboardInterrupt:
            sys.exit(0)
    
    print("=" * 60)
    print("AI旅行规划师 - 火山方舟流式语音识别版")
    print("=" * 60)
    print(f"服务器地址: http://localhost:8080")
    print(f"网络地址: http://0.0.0.0:8080")
    print(f"语音服务: 火山方舟流式语音识别大模型")
    print("=" * 60)
    print("提示: 这是开发服务器，仅用于开发和测试")
    print("=" * 60)
    print("\n正在启动服务器...\n")
    
    # 启动应用
    # 注意: 警告信息是 Flask 开发服务器的正常提示，不影响功能
    # 在 Windows 上，禁用 reloader 可以避免某些兼容性问题
    import platform
    use_reloader = platform.system() != 'Windows'
    
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=8080, 
        allow_unsafe_werkzeug=True,
        use_reloader=use_reloader  # Windows 上禁用 reloader
    )
