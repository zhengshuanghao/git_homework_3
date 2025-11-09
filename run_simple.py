"""
简化启动脚本（禁用 reloader，避免兼容性问题）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app, socketio
from config import Config

if __name__ == '__main__':
    Config.load_from_file()
    
    print("=" * 50)
    print("AI旅行规划师")
    print("=" * 50)
    print(f"服务器地址: http://localhost:8080")
    print("=" * 50)
    print("\n正在启动服务器...\n")
    
    # 禁用 reloader 以避免兼容性问题
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=8080, 
        allow_unsafe_werkzeug=True,
        use_reloader=False  # 禁用自动重载
    )

