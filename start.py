"""
生产环境启动脚本（可选）
使用 gunicorn 或 waitress 作为生产服务器
"""
import os
import sys

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

from config import Config

def start_with_gunicorn():
    """使用 Gunicorn 启动（Linux/Mac）"""
    try:
        import gunicorn
        from app import app
        
        Config.load_from_file()
        
        # Gunicorn 配置
        bind = "0.0.0.0:8080"
        workers = 4
        worker_class = "eventlet"  # 支持 WebSocket
        
        print("=" * 50)
        print("AI旅行规划师 - 生产环境")
        print("=" * 50)
        print(f"使用 Gunicorn 启动")
        print(f"服务器地址: http://localhost:8080")
        print("=" * 50)
        
        os.system(f"gunicorn -w {workers} -k {worker_class} -b {bind} app:app")
    except ImportError:
        print("错误: 未安装 Gunicorn")
        print("安装命令: pip install gunicorn eventlet")
        sys.exit(1)

def start_with_waitress():
    """使用 Waitress 启动（Windows/Linux/Mac）"""
    try:
        from waitress import serve
        from app import app, socketio
        
        Config.load_from_file()
        
        print("=" * 50)
        print("AI旅行规划师 - 生产环境")
        print("=" * 50)
        print(f"使用 Waitress 启动")
        print(f"服务器地址: http://localhost:8080")
        print("=" * 50)
        print("\n注意: Waitress 不支持 WebSocket，SocketIO 功能可能受限")
        print("建议开发环境使用 run.py，生产环境使用 Gunicorn + eventlet")
        print("=" * 50)
        
        serve(app, host='0.0.0.0', port=8080)
    except ImportError:
        print("错误: 未安装 Waitress")
        print("安装命令: pip install waitress")
        sys.exit(1)

if __name__ == '__main__':
    import platform
    
    if platform.system() == 'Windows':
        print("Windows 系统建议使用 run.py 启动开发服务器")
        print("或安装 Waitress: pip install waitress")
        start_with_waitress()
    else:
        print("Linux/Mac 系统可以使用 Gunicorn")
        start_with_gunicorn()

