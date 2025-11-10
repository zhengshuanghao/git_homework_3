"""
火山方舟流式语音识别服务 (SAUC BigModel)
基于官方 WebSocket API 实现
"""
import asyncio
import aiohttp
import json
import struct
import gzip
import uuid
import base64
from typing import Optional, Dict, Any, Callable


# ==================== 协议常量 ====================

class ProtocolVersion:
    V1 = 0b0001

class MessageType:
    CLIENT_FULL_REQUEST = 0b0001
    CLIENT_AUDIO_ONLY_REQUEST = 0b0010
    SERVER_FULL_RESPONSE = 0b1001
    SERVER_ERROR_RESPONSE = 0b1111

class MessageTypeSpecificFlags:
    NO_SEQUENCE = 0b0000
    POS_SEQUENCE = 0b0001
    NEG_SEQUENCE = 0b0010
    NEG_WITH_SEQUENCE = 0b0011

class SerializationType:
    NO_SERIALIZATION = 0b0000
    JSON = 0b0001

class CompressionType:
    NO_COMPRESSION = 0b0000
    GZIP = 0b0001


# ==================== 请求头构建 ====================

class AsrRequestHeader:
    """ASR 请求头"""
    
    def __init__(self):
        self.message_type = MessageType.CLIENT_FULL_REQUEST
        self.message_type_specific_flags = MessageTypeSpecificFlags.POS_SEQUENCE
        self.serialization_type = SerializationType.JSON
        self.compression_type = CompressionType.GZIP
        self.reserved_data = bytes([0x00])
    
    def with_message_type(self, message_type: int):
        self.message_type = message_type
        return self
    
    def with_message_type_specific_flags(self, flags: int):
        self.message_type_specific_flags = flags
        return self
    
    def to_bytes(self) -> bytes:
        """转换为字节"""
        header = bytearray()
        header.append((ProtocolVersion.V1 << 4) | 1)
        header.append((self.message_type << 4) | self.message_type_specific_flags)
        header.append((self.serialization_type << 4) | self.compression_type)
        header.extend(self.reserved_data)
        return bytes(header)


# ==================== 请求构建器 ====================

class RequestBuilder:
    """构建ASR请求"""
    
    @staticmethod
    def new_auth_headers(app_key: str, access_key: str) -> Dict[str, str]:
        """生成认证头"""
        reqid = str(uuid.uuid4())
        return {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Request-Id": reqid,
            "X-Api-Access-Key": access_key,
            "X-Api-App-Key": app_key
        }
    
    @staticmethod
    def new_full_client_request(seq: int) -> bytes:
        """生成完整客户端请求（第一个包）"""
        header = AsrRequestHeader() \
            .with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        
        payload = {
            "user": {
                "uid": "web_user"
            },
            "audio": {
                "format": "wav",
                "codec": "raw",
                "rate": 16000,
                "bits": 16,
                "channel": 1
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
                "show_utterances": True,
                "enable_nonstream": False  # 双向流式模式
            }
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        compressed_payload = gzip.compress(payload_bytes)
        payload_size = len(compressed_payload)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))
        request.extend(struct.pack('>I', payload_size))
        request.extend(compressed_payload)
        
        return bytes(request)
    
    @staticmethod
    def new_audio_only_request(seq: int, segment: bytes, is_last: bool = False) -> bytes:
        """生成纯音频请求"""
        header = AsrRequestHeader()
        
        if is_last:
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.NEG_WITH_SEQUENCE)
            seq = -seq  # 最后一个包用负数
        else:
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        
        header.with_message_type(MessageType.CLIENT_AUDIO_ONLY_REQUEST)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))
        
        compressed_segment = gzip.compress(segment)
        request.extend(struct.pack('>I', len(compressed_segment)))
        request.extend(compressed_segment)
        
        return bytes(request)


# ==================== 响应解析 ====================

class ResponseParser:
    """解析服务器响应"""
    
    @staticmethod
    def parse_response(data: bytes) -> Dict[str, Any]:
        """解析二进制响应"""
        try:
            if len(data) < 4:
                return {"error": f"Response too short: {len(data)} bytes"}
            
            # 解析头部第一个字节
            header_byte = data[0]
            version = (header_byte >> 4) & 0x0F
            header_size = header_byte & 0x0F  # 头部实际大小（单位：4字节）
            
            # 计算实际头部字节数
            actual_header_bytes = header_size * 4
            
            message_type_byte = data[1]
            message_type = (message_type_byte >> 4) & 0x0F
            message_type_specific_flags = message_type_byte & 0x0F
            
            serialization_compression_byte = data[2]
            serialization_type = (serialization_compression_byte >> 4) & 0x0F
            compression_type = serialization_compression_byte & 0x0F
            
            # 调试信息
            print(f"[调试响应] version={version}, header_size={header_size} ({actual_header_bytes}字节), msg_type={message_type}, serialization={serialization_type}, compression={compression_type}")
            
            # 检查数据长度是否足够
            if len(data) < actual_header_bytes + 8:
                return {"error": f"Data too short for header+seq+size: need {actual_header_bytes+8}, got {len(data)}"}
            
            # 序列号和payload大小在头部之后
            seq = struct.unpack('>i', data[actual_header_bytes:actual_header_bytes+4])[0]
            payload_size = struct.unpack('>I', data[actual_header_bytes+4:actual_header_bytes+8])[0]
            
            print(f"[调试响应] seq={seq}, payload_size={payload_size}, total_data_size={len(data)}")
            
            # 解析payload
            payload_start = actual_header_bytes + 8
            payload_data = data[payload_start:payload_start+payload_size]
            print(f"[调试响应] payload_start={payload_start}, payload_data长度: {len(payload_data)}")
            
            # 解压缩
            if compression_type == CompressionType.GZIP:
                try:
                    payload_data = gzip.decompress(payload_data)
                    print(f"[调试响应] 解压后长度: {len(payload_data)}")
                except Exception as e:
                    print(f"[调试响应] 解压失败: {e}")
                    return {"error": f"Decompression failed: {str(e)}"}
            
            # 反序列化
            payload = {}
            if serialization_type == SerializationType.JSON:
                if len(payload_data) == 0:
                    print("[调试响应] Payload为空，返回空字典")
                    payload = {}
                else:
                    try:
                        payload_str = payload_data.decode('utf-8')
                        print(f"[调试响应] JSON字符串: {payload_str[:200]}")  # 只打印前200字符
                        payload = json.loads(payload_str)
                    except Exception as e:
                        print(f"[调试响应] JSON解析失败: {e}")
                        return {"error": f"JSON parse failed: {str(e)}"}
            elif serialization_type == SerializationType.NO_SERIALIZATION:
                print("[调试响应] 无序列化类型")
                payload = {}
            
            return {
                "message_type": message_type,
                "seq": seq,
                "payload": payload,
                "is_last": message_type_specific_flags == MessageTypeSpecificFlags.NEG_SEQUENCE
            }
        except Exception as e:
            print(f"[调试响应] 解析异常: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to parse response: {str(e)}"}


# ==================== 语音识别服务 ====================

class SpeechRecognitionService:
    """火山方舟流式语音识别客户端"""
    
    def __init__(self, app_id: str, access_key: str, secret_key: str, model_id: str):
        self.app_key = str(app_id)  # app_key 就是 app_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.model_id = model_id
        
        # 使用双向流式模式（优化版本）
        self.url = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async"
        
        self.session = None
        self.ws = None
        self.is_connected = False
        self.seq = 1  # 序列号从1开始，不是0
        
        # 回调函数
        self.on_result_callback = None
        self.on_error_callback = None
        
        # 音频缓冲
        self.audio_buffer = bytearray()
        self.chunk_size = 6400  # 200ms @ 16kHz, 16bit, mono = 16000 * 0.2 * 2 = 6400 bytes
    
    async def connect(self):
        """建立 WebSocket 连接"""
        try:
            headers = RequestBuilder.new_auth_headers(self.app_key, self.access_key)
            
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.url, headers=headers)
            
            self.is_connected = True
            print(f"[OK] 语音识别服务已连接: {self.url}")
            
            # 发送初始化请求
            await self._send_full_request()
            
            # 启动接收任务
            asyncio.create_task(self._receive_messages())
            
        except Exception as e:
            print(f"[X] 语音识别连接失败: {str(e)}")
            self.is_connected = False
            if self.on_error_callback:
                self.on_error_callback(f"连接失败: {str(e)}")
    
    async def _send_full_request(self):
        """发送初始化请求"""
        try:
            request = RequestBuilder.new_full_client_request(self.seq)
            print(f"[调试] 发送初始化请求，seq={self.seq}")
            self.seq += 1
            
            await self.ws.send_bytes(request)
            print("[OK] 已发送初始化请求")
            
            # 等待初始化响应
            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.BINARY:
                response = ResponseParser.parse_response(msg.data)
                payload = response.get('payload', {})
                
                # 检查是否有错误
                if 'error' in response:
                    print(f"[X] 初始化响应错误: {response['error']}")
                    raise Exception(response['error'])
                elif payload.get('code') != 0:
                    error_msg = payload.get('message', '未知错误')
                    print(f"[X] 初始化失败 (code={payload.get('code')}): {error_msg}")
                    raise Exception(error_msg)
                else:
                    print(f"[OK] 初始化成功: {payload}")
            
        except Exception as e:
            print(f"[X] 发送初始化请求失败: {str(e)}")
            self.is_connected = False
            raise
    
    async def _receive_messages(self):
        """接收 WebSocket 消息"""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    response = ResponseParser.parse_response(msg.data)
                    self._handle_response(response)
                    
                    if response.get('is_last'):
                        print("[OK] 收到最后一个响应")
                        break
                        
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"[X] WebSocket错误: {msg.data}")
                    if self.on_error_callback:
                        self.on_error_callback(f"WebSocket错误: {msg.data}")
                    break
                    
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print("[OK] WebSocket连接已关闭")
                    self.is_connected = False
                    break
                    
        except Exception as e:
            print(f"[X] 接收消息错误: {str(e)}")
            self.is_connected = False
            if self.on_error_callback:
                self.on_error_callback(f"接收消息错误: {str(e)}")
    
    def _handle_response(self, response: Dict[str, Any]):
        """处理识别结果"""
        try:
            payload = response.get('payload', {})
            
            # 检查错误
            if 'error' in response:
                print(f"[X] 响应错误: {response['error']}")
                return
            
            # 检查code
            code = payload.get('code', 0)
            if code != 0:
                error_msg = payload.get('message', '未知错误')
                print(f"[X] 识别错误 (code={code}): {error_msg}")
                if self.on_error_callback:
                    self.on_error_callback(error_msg)
                return
            
            # 提取识别结果
            result = payload.get('result', {})
            text = result.get('text', '')
            is_final = result.get('is_final', False)
            
            if text:
                print(f"[语音识别] {'最终' if is_final else '临时'}结果: {text}")
                
                if self.on_result_callback:
                    self.on_result_callback({
                        'text': text,
                        'is_final': is_final
                    })
                    
        except Exception as e:
            print(f"[X] 处理响应失败: {str(e)}")
    
    async def send_audio(self, audio_data: bytes):
        """发送音频数据"""
        try:
            if not self.is_connected or not self.ws:
                print("[WARN] 未连接，跳过音频发送")
                return
            
            if self.ws.closed:
                print("[WARN] WebSocket已关闭，跳过音频发送")
                self.is_connected = False
                return
            
            # 如果是Base64编码的，先解码
            if isinstance(audio_data, str):
                audio_data = base64.b64decode(audio_data)
            
            # 添加到缓冲区
            self.audio_buffer.extend(audio_data)
            
            # 当缓冲区达到chunk_size时，发送一个包
            while len(self.audio_buffer) >= self.chunk_size:
                chunk = bytes(self.audio_buffer[:self.chunk_size])
                self.audio_buffer = self.audio_buffer[self.chunk_size:]
                
                # 构建音频请求
                request = RequestBuilder.new_audio_only_request(
                    self.seq,
                    chunk,
                    is_last=False
                )
                self.seq += 1
                
                await self.ws.send_bytes(request)
                # print(f"[语音识别] 已发送音频包 seq={self.seq-1}, size={len(chunk)}")
                
        except Exception as e:
            print(f"[X] 发送音频失败: {str(e)}")
    
    async def send_end_signal(self):
        """发送结束信号"""
        try:
            if not self.is_connected or not self.ws:
                return
            
            # 发送缓冲区剩余数据（如果有）
            if len(self.audio_buffer) > 0:
                chunk = bytes(self.audio_buffer)
                request = RequestBuilder.new_audio_only_request(
                    self.seq,
                    chunk,
                    is_last=True
                )
                await self.ws.send_bytes(request)
                print(f"[OK] 已发送最后一个音频包 (size={len(chunk)})")
                self.audio_buffer.clear()
            else:
                # 发送空的结束包
                request = RequestBuilder.new_audio_only_request(
                    self.seq,
                    b'',
                    is_last=True
                )
                await self.ws.send_bytes(request)
                print("[OK] 已发送结束信号")
                
        except Exception as e:
            print(f"[X] 发送结束信号失败: {str(e)}")
    
    async def disconnect(self):
        """断开连接"""
        try:
            self.is_connected = False
            
            if self.ws:
                await self.ws.close()
                self.ws = None
            
            if self.session:
                await self.session.close()
                self.session = None
            
            print("[OK] 语音识别连接已关闭")
            
        except Exception as e:
            print(f"[X] 断开连接失败: {str(e)}")
    
    def set_callbacks(self, on_result: Optional[Callable] = None, on_error: Optional[Callable] = None):
        """设置回调函数"""
        if on_result:
            self.on_result_callback = on_result
        if on_error:
            self.on_error_callback = on_error


# ==================== 同步包装器 ====================

class SpeechRecognitionSyncWrapper:
    """语音识别服务的同步包装器（用于 Flask-SocketIO）"""
    
    def __init__(self, app_id: str, access_key: str, secret_key: str, model_id: str):
        self.service = SpeechRecognitionService(app_id, access_key, secret_key, model_id)
        self.loop = None
        self.thread = None
        self.is_running = False
    
    def start(self, on_result: Optional[Callable] = None, on_error: Optional[Callable] = None):
        """启动服务"""
        import threading
        import time
        
        self.service.set_callbacks(on_result, on_error)
        
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.is_running = True
            
            # 连接服务
            self.loop.run_until_complete(self.service.connect())
            
            # 保持循环运行
            try:
                self.loop.run_forever()
            finally:
                self.loop.close()
                self.is_running = False
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # 等待连接建立
        time.sleep(1.5)
    
    def send_audio(self, audio_data):
        """发送音频数据（线程安全）"""
        if self.loop and self.is_running:
            asyncio.run_coroutine_threadsafe(
                self.service.send_audio(audio_data),
                self.loop
            )
    
    def stop(self):
        """停止服务"""
        if self.loop and self.is_running:
            # 发送结束信号
            asyncio.run_coroutine_threadsafe(
                self.service.send_end_signal(),
                self.loop
            )
            
            # 断开连接
            asyncio.run_coroutine_threadsafe(
                self.service.disconnect(),
                self.loop
            )
            
            # 停止事件循环
            self.loop.call_soon_threadsafe(self.loop.stop)
    
    @property
    def is_connected(self):
        """是否已连接"""
        return self.service.is_connected
