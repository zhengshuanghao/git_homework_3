"""
AI Travel Planner - 主应用文件
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json

from config import Config
from services.iflytek_service import IflytekService
from services.deepseek_service import DeepSeekService
from services.supabase_service import SupabaseService
from services.amap_service import AmapService
from services.audio_converter import AudioConverter

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化服务
iflytek_service = IflytekService()
deepseek_service = DeepSeekService()
supabase_service = SupabaseService()
amap_service = AmapService()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置（仅返回前端需要的配置）"""
    return jsonify({
        'amap_api_key': Config.AMAP_API_KEY if Config.AMAP_API_KEY else '',
        'supabase_url': Config.SUPABASE_URL if Config.SUPABASE_URL else '',
        'supabase_key': Config.SUPABASE_KEY if Config.SUPABASE_KEY else ''
    })

@app.route('/api/config/all', methods=['GET'])
def get_all_config():
    """获取所有配置（用于调试，不返回敏感信息）"""
    # 检查配置是否已设置（不返回实际值）
    config_status = {
        'flask': {
            'secret_key_set': bool(app.config.get('SECRET_KEY')),
            'env': app.config.get('ENV', 'production')
        },
        'iflytek': {
            'app_id_set': bool(Config.IFLYTEK_APP_ID),
            'api_key_set': bool(Config.IFLYTEK_API_KEY),
            'api_secret_set': bool(Config.IFLYTEK_API_SECRET)
        },
        'amap': {
            'api_key_set': bool(Config.AMAP_API_KEY),
            'api_secret_set': bool(Config.AMAP_API_SECRET)
        },
        'deepseek': {
            'api_key_set': bool(Config.DEEPSEEK_API_KEY),
            'base_url': Config.DEEPSEEK_BASE_URL
        },
        'supabase': {
            'url_set': bool(Config.SUPABASE_URL),
            'key_set': bool(Config.SUPABASE_KEY)
        }
    }
    return jsonify(config_status)

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        config_data = request.json
        Config.update_config(config_data)
        Config.save_to_file()
        return jsonify({'success': True, 'message': '配置更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/travel/plan', methods=['POST'])
def create_travel_plan():
    """创建旅行计划"""
    try:
        data = request.json
        user_input = data.get('input', '')
        user_id = data.get('user_id')
        
        # 使用DeepSeek生成旅行计划
        plan = deepseek_service.generate_travel_plan(user_input)
        
        # 保存到Supabase
        if user_id and supabase_service.is_configured():
            plan_id = supabase_service.save_travel_plan(user_id, plan, user_input)
            plan['id'] = plan_id
        
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/travel/plans', methods=['GET'])
def get_travel_plans():
    """获取用户的旅行计划列表"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        plans = supabase_service.get_travel_plans(user_id)
        return jsonify({'success': True, 'plans': plans})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/travel/plan/<plan_id>', methods=['GET'])
def get_travel_plan(plan_id):
    """获取单个旅行计划"""
    try:
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        plan = supabase_service.get_travel_plan(plan_id)
        if plan:
            return jsonify({'success': True, 'plan': plan})
        else:
            return jsonify({'success': False, 'message': '计划不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/travel/expense', methods=['POST'])
def add_expense():
    """添加费用记录"""
    try:
        data = request.json
        user_id = data.get('user_id')
        plan_id = data.get('plan_id')
        expense = data.get('expense')
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        expense_id = supabase_service.add_expense(user_id, plan_id, expense)
        return jsonify({'success': True, 'expense_id': expense_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        user = supabase_service.login(email, password)
        if user:
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': '登录失败'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        user = supabase_service.register(email, password, name)
        if user:
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': '注册失败'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    print('Client connected')
    emit('connected', {'status': 'connected'})

@socketio.on('start_recording')
def handle_start_recording():
    """开始录音"""
    if not iflytek_service.is_configured():
        emit('error', {'message': '语音识别服务未配置'})
        return
    
    try:
        iflytek_service.start_recording(socketio)
        emit('recording_started', {'status': 'success'})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('audio_data')
def handle_audio_data(data):
    """接收音频数据（WebM格式，需要转换为PCM）"""
    try:
        # 如果数据是Base64编码的WebM格式，需要先转换
        if isinstance(data, str):
            # 尝试转换为PCM格式
            try:
                # 新方法，自动检测格式，默认提示为webm
                pcm_data = AudioConverter.base64_audio_to_pcm(data, format_hint='webm')
                iflytek_service.send_audio_data(pcm_data)
            except Exception as e:
                # 如果转换失败，尝试直接发送（可能是已经是PCM格式）
                print(f"音频转换失败，尝试直接发送: {str(e)}")
                iflytek_service.send_audio_data(data)
        else:
            iflytek_service.send_audio_data(data)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_recording')
def handle_stop_recording():
    """停止录音"""
    try:
        result = iflytek_service.stop_recording()
        emit('recording_result', {'text': result})
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    # 从文件加载配置
    Config.load_from_file()
    
    # 启动应用
    # 注意: 警告信息是 Flask 开发服务器的正常提示，不影响功能
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)

