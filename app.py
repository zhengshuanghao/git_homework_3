"""
AI Travel Planner - 主应用文件
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json

from config import Config
from services.speech_recognition_service import SpeechRecognitionSyncWrapper
from services.deepseek_service import DeepSeekService
from services.supabase_service import SupabaseService
from services.amap_service import AmapService
from services.preference_service import PreferenceService
from services.expense_service import ExpenseService
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化服务
speech_recognition_service = SpeechRecognitionSyncWrapper(
    app_id=Config.SPEECH_APP_ID,
    access_key=Config.SPEECH_ACCESS_KEY,
    secret_key=Config.SPEECH_SECRET_KEY,
    model_id=Config.SPEECH_MODEL_ID
)
deepseek_service = DeepSeekService()
supabase_service = SupabaseService()
amap_service = AmapService()
preference_service = PreferenceService()
expense_service = ExpenseService()

@app.route('/')
def landing():
    """欢迎页面"""
    return render_template('landing.html')

@app.route('/app')
def app_page():
    """主应用页面（需要登录）"""
    return render_template('app.html')

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
            'base_url': Config.ARK_BASE_URL,
            'model': Config.DEEPSEEK_MODEL
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
        
        # 获取用户偏好设置
        user_preferences = None
        if user_id and supabase_service.is_configured():
            user_preferences = preference_service.get_user_preferences(user_id)
        
        # 使用DeepSeek生成旅行计划（结合用户偏好）
        plan = deepseek_service.generate_travel_plan(user_input, user_preferences)
        
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

@app.route('/api/travel/plan/<plan_id>', methods=['DELETE'])
def delete_travel_plan(plan_id):
    """删除旅行计划"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        # 删除计划
        supabase_service.client.table('travel_plans').delete().eq('id', plan_id).eq('user_id', user_id).execute()
        return jsonify({'success': True, 'message': '计划已删除'})
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
    """开始语音识别"""
    try:
        # 定义回调函数
        def on_result(result):
            """接收到识别结果"""
            text = result.get('text', '')
            is_final = result.get('is_final', False)
            
            socketio.emit('recognition_result', {
                'text': text,
                'is_final': is_final
            })
            print(f"[语音识别] {'最终' if is_final else '临时'}结果: {text}")
        
        def on_error(error_msg):
            """接收到错误"""
            socketio.emit('error', {'message': error_msg})
            print(f"[X] 语音识别错误: {error_msg}")
        
        # 启动语音识别服务
        speech_recognition_service.start(
            on_result=on_result,
            on_error=on_error
        )
        
        # 检查是否成功连接
        if not speech_recognition_service.is_connected:
            raise Exception("语音识别服务连接失败")
        
        emit('recording_started', {'status': 'success', 'message': '语音识别已启动，请开始说话'})
        print("[OK] 语音识别已启动")
        
    except Exception as e:
        emit('error', {'message': f'启动语音识别失败: {str(e)}'})
        print(f"[X] 启动语音识别失败: {str(e)}")

@socketio.on('audio_data')
def handle_audio_data(data):
    """接收音频数据并发送给语音识别服务（流式）"""
    try:
        if not speech_recognition_service.is_connected:
            print("[WARN] 语音识别服务未连接，忽略音频数据")
            return
        
        # 发送音频数据到语音识别服务
        speech_recognition_service.send_audio(data)
        # print(f"[语音识别] 已发送音频数据")
        
    except Exception as e:
        print(f"[X] 处理音频数据错误: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('stop_recording')
def handle_stop_recording():
    """停止语音识别"""
    try:
        if speech_recognition_service.is_connected:
            speech_recognition_service.stop()
            emit('recording_stopped', {'status': 'success', 'message': '语音识别已结束'})
            print("[OK] 语音识别已停止")
        else:
            print("[WARN] 语音识别服务未连接")
    except Exception as e:
        print(f"[X] 停止语音识别失败: {str(e)}")
        emit('error', {'message': f'停止语音识别失败: {str(e)}'})

# ==================== 用户偏好设置API ====================

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """获取用户偏好设置"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        preferences = preference_service.get_user_preferences(user_id)
        return jsonify({'success': True, 'preferences': preferences})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    """保存用户偏好设置"""
    try:
        data = request.json
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        result = preference_service.save_user_preferences(user_id, preferences)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 费用记录API ====================

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """获取费用记录"""
    try:
        user_id = request.args.get('user_id')
        plan_id = request.args.get('plan_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        expenses = expense_service.get_user_expenses(user_id, plan_id)
        return jsonify({'success': True, 'expenses': expenses})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """添加费用记录"""
    try:
        data = request.json
        user_id = data.get('user_id')
        expense_data = data.get('expense', {})
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        result = expense_service.add_expense(user_id, expense_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """更新费用记录"""
    try:
        data = request.json
        user_id = data.get('user_id')
        expense_data = data.get('expense', {})
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        result = expense_service.update_expense(expense_id, user_id, expense_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """删除费用记录"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        result = expense_service.delete_expense(expense_id, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/summary', methods=['GET'])
def get_expense_summary():
    """获取费用汇总"""
    try:
        user_id = request.args.get('user_id')
        plan_id = request.args.get('plan_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id参数'}), 400
        
        if not supabase_service.is_configured():
            return jsonify({'success': False, 'message': 'Supabase未配置'}), 400
        
        summary = expense_service.get_expense_summary(user_id, plan_id)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # 从文件加载配置
    Config.load_from_file()
    
    print("=" * 60)
    print("AI旅行规划师 - 火山方舟流式语音识别版")
    print("=" * 60)
    print(f"服务器地址: http://localhost:8080")
    print(f"语音服务: 火山方舟流式语音识别大模型")
    print("=" * 60)
    print("\n正在启动服务器...\n")
    
    # 启动应用
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)

