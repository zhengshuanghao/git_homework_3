"""
科大讯飞语音识别服务
"""
import hashlib
import hmac
import base64
import json
import time
import threading
import urllib.parse
import datetime
import uuid
from websocket import create_connection, WebSocketException
from config import Config

# 固定参数
FIXED_PARAMS = {
    "audio_encode": "pcm_s16le",
    "lang": "autodialect",
    "samplerate": "16000"
}
AUDIO_FRAME_SIZE = 1280  # 每帧音频字节数
FRAME_INTERVAL_MS = 40   # 每帧发送间隔（毫秒）


class IflytekService:
    """科大讯飞实时语音识别服务"""
    
    def __init__(self):
        self.app_id = Config.IFLYTEK_APP_ID
        self.api_key = Config.IFLYTEK_API_KEY
        self.api_secret = Config.IFLYTEK_API_SECRET
        self.base_ws_url = "wss://office-api-ast-dx.iflyaisol.com/ast/communicate/v1"
        self.ws = None
        self.is_connected = False
        self.recv_thread = None
        self.session_id = None
        self.recognition_result = ""
        self.socketio = None
        self.audio_buffer = bytearray()
        self.is_recording = False
    
    def is_configured(self):
        """检查配置是否完整"""
        return bool(self.app_id and self.api_key and self.api_secret)
    
    def _get_utc_time(self):
        """生成UTC时间格式"""
        beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
        now = datetime.datetime.now(beijing_tz)
        return now.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    def _generate_auth_params(self):
        """生成鉴权参数"""
        auth_params = {
            "accessKeyId": self.api_key,
            "appId": self.app_id,
            "uuid": uuid.uuid4().hex,
            "utc": self._get_utc_time(),
            **FIXED_PARAMS
        }
        
        # 计算签名
        sorted_params = dict(sorted([
            (k, v) for k, v in auth_params.items()
            if v is not None and str(v).strip() != ""
        ]))
        base_str = "&".join([
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
            for k, v in sorted_params.items()
        ])
        
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            base_str.encode("utf-8"),
            hashlib.sha1
        ).digest()
        auth_params["signature"] = base64.b64encode(signature).decode("utf-8")
        return auth_params
    
    def connect(self):
        """建立WebSocket连接"""
        if not self.is_configured():
            raise Exception("科大讯飞API未配置")
        
        try:
            auth_params = self._generate_auth_params()
            params_str = urllib.parse.urlencode(auth_params)
            full_ws_url = f"{self.base_ws_url}?{params_str}"
            
            self.ws = create_connection(full_ws_url, timeout=15, enable_multithread=True)
            self.is_connected = True
            time.sleep(1.5)
            
            # 启动接收线程
            self.recv_thread = threading.Thread(target=self._recv_msg, daemon=True)
            self.recv_thread.start()
            return True
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False
    
    def _recv_msg(self):
        """接收服务端消息"""
        while self.is_connected and self.ws:
            try:
                msg = self.ws.recv()
                if not msg:
                    self.close()
                    break
                
                if isinstance(msg, str):
                    try:
                        msg_json = json.loads(msg)
                        
                        # 更新会话ID
                        if (msg_json.get('msg_type') == 'action' 
                            and 'sessionId' in msg_json.get('data', {})):
                            self.session_id = msg_json['data']['sessionId']
                        
                        # 处理识别结果
                        if msg_json.get('msg_type') == 'result':
                            result_text = msg_json.get('data', {}).get('text', '')
                            if result_text:
                                self.recognition_result += result_text
                                if self.socketio:
                                    self.socketio.emit('recognition_interim', {'text': result_text})
                        
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"接收消息错误: {str(e)}")
                self.close()
                break
    
    def start_recording(self, socketio=None):
        """开始录音"""
        self.socketio = socketio
        self.recognition_result = ""
        self.audio_buffer = bytearray()
        self.is_recording = True
        
        if not self.is_connected:
            if not self.connect():
                raise Exception("无法连接到语音识别服务")
    
    def send_audio_data(self, audio_data):
        """发送音频数据（PCM格式，16kHz，16bit，单声道）"""
        if not self.is_connected or not self.ws:
            return
        
        try:
            # 将数据添加到缓冲区
            if isinstance(audio_data, str):
                # Base64编码的PCM音频数据
                audio_bytes = base64.b64decode(audio_data)
                self.audio_buffer.extend(audio_bytes)
            elif isinstance(audio_data, bytes):
                self.audio_buffer.extend(audio_data)
            
            # 如果缓冲区有足够的数据，发送一帧
            while len(self.audio_buffer) >= AUDIO_FRAME_SIZE:
                chunk = bytes(self.audio_buffer[:AUDIO_FRAME_SIZE])
                self.audio_buffer = self.audio_buffer[AUDIO_FRAME_SIZE:]
                if self.ws and self.is_connected:
                    try:
                        self.ws.send_binary(chunk)
                        # 控制发送速率：每帧40ms
                        time.sleep(FRAME_INTERVAL_MS / 1000.0)
                    except Exception as e:
                        print(f"发送音频帧失败: {str(e)}")
                        break
        except Exception as e:
            print(f"发送音频数据失败: {str(e)}")
    
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        
        # 发送缓冲区剩余数据
        if self.audio_buffer and self.is_connected and self.ws:
            try:
                # 发送剩余数据，不足一帧的也发送
                if len(self.audio_buffer) > 0:
                    chunk = bytes(self.audio_buffer)
                    self.ws.send_binary(chunk)
                    self.audio_buffer = []
            except Exception as e:
                print(f"发送剩余音频数据失败: {str(e)}")
        
        if self.is_connected and self.ws and self.session_id:
            # 发送结束标记
            end_msg = {"end": True, "sessionId": self.session_id}
            try:
                self.ws.send(json.dumps(end_msg, ensure_ascii=False))
            except Exception:
                pass
            
            # 等待结果
            time.sleep(2)
            result = self.recognition_result
            self.recognition_result = ""
            return result
        
        return ""
    
    def close(self):
        """关闭连接"""
        self.is_connected = False
        if self.ws:
            try:
                if self.ws.connected:
                    self.ws.close()
            except Exception:
                pass
            self.ws = None

