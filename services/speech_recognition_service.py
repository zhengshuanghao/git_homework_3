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
                "format": "pcm",  # 改为 pcm，因为我们发送的是原始 PCM 数据
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
    """解析服务器响应（完全按照官方示例实现）"""
    
    @staticmethod
    def parse_response(msg: bytes) -> Dict[str, Any]:
        """解析二进制响应"""
        try:
            if len(msg) < 4:
                return {"error": f"Response too short: {len(msg)} bytes"}
            
            # 解析头部（与官方示例完全一致）
            header_size = msg[0] & 0x0f
            message_type = msg[1] >> 4
            message_type_specific_flags = msg[1] & 0x0f
            serialization_method = msg[2] >> 4
            message_compression = msg[2] & 0x0f
            
            print(f"[调试响应] header_size={header_size}, msg_type={message_type}, flags={message_type_specific_flags:04b}, serialization={serialization_method}, compression={message_compression}")
            
            # 跳过头部，获取payload部分
            payload = msg[header_size * 4:]
            
            if len(payload) == 0:
                return {"error": "Empty payload after header"}
            
            # 解析序列号（根据flags条件解析）
            seq = 0
            if message_type_specific_flags & 0x01:  # 如果有序列号标志
                if len(payload) < 4:
                    return {"error": "Payload too short for sequence"}
                seq = struct.unpack('>i', payload[:4])[0]
                payload = payload[4:]
                print(f"[调试响应] 解析到序列号: {seq}")
            
            # 解析is_last标志
            is_last = False
            if message_type_specific_flags & 0x02:  # 如果是最后一个包
                is_last = True
                print(f"[调试响应] 这是最后一个包")
            
            # 解析event（如果有）
            event = 0
            if message_type_specific_flags & 0x04:  # 如果有event标志
                if len(payload) < 4:
                    return {"error": "Payload too short for event"}
                event = struct.unpack('>i', payload[:4])[0]
                payload = payload[4:]
                print(f"[调试响应] 解析到event: {event}")
            
            # 根据message_type解析payload_size
            payload_size = 0
            code = 0
            if message_type == MessageType.SERVER_FULL_RESPONSE:
                if len(payload) < 4:
                    return {"error": "Payload too short for payload_size"}
                payload_size = struct.unpack('>I', payload[:4])[0]
                payload = payload[4:]
                print(f"[调试响应] SERVER_FULL_RESPONSE, payload_size={payload_size}")
            elif message_type == MessageType.SERVER_ERROR_RESPONSE:
                if len(payload) < 8:
                    return {"error": "Payload too short for error code and payload_size"}
                code = struct.unpack('>i', payload[:4])[0]
                payload_size = struct.unpack('>I', payload[4:8])[0]
                payload = payload[8:]
                print(f"[调试响应] SERVER_ERROR_RESPONSE, code={code}, payload_size={payload_size}")
            
            # 提取实际的payload数据
            if payload_size > 0:
                if len(payload) < payload_size:
                    print(f"[警告] Payload数据不完整: 需要{payload_size}, 实际{len(payload)}")
                    payload_data = payload
                else:
                    payload_data = payload[:payload_size]
            else:
                payload_data = payload
            
            print(f"[调试响应] payload_data长度: {len(payload_data)}")
            
            # 解压缩
            if message_compression == CompressionType.GZIP:
                try:
                    payload_data = gzip.decompress(payload_data)
                    print(f"[调试响应] 解压后长度: {len(payload_data)}")
                except Exception as e:
                    print(f"[调试响应] 解压失败: {e}")
                    return {"error": f"Decompression failed: {str(e)}"}
            
            # 反序列化
            payload_msg = None
            if serialization_method == SerializationType.JSON:
                if len(payload_data) == 0:
                    print("[调试响应] Payload为空")
                    payload_msg = {}
                else:
                    try:
                        payload_str = payload_data.decode('utf-8')
                        print(f"[调试响应] JSON字符串 (前200字符): {payload_str[:200]}")
                        payload_msg = json.loads(payload_str)
                        print(f"[调试响应] JSON解析成功")
                    except Exception as e:
                        print(f"[调试响应] JSON解析失败: {e}")
                        print(f"[调试响应] 原始数据 (hex): {payload_data[:100].hex()}")
                        return {"error": f"JSON parse failed: {str(e)}"}
            
            return {
                "message_type": message_type,
                "seq": seq,
                "code": code,
                "event": event,
                "is_last": is_last,
                "payload": payload_msg or {},
                "payload_size": payload_size
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
            # 重置序列号和缓冲区
            self.seq = 1
            self.audio_buffer.clear()
            
            headers = RequestBuilder.new_auth_headers(self.app_key, self.access_key)
            print(f"[调试] 准备连接: {self.url}")
            print(f"[调试] 请求头: {list(headers.keys())}")
            
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.url, headers=headers)
            
            self.is_connected = True
            print(f"[OK] 语音识别服务已连接: {self.url}")
            
            # 发送初始化请求
            await self._send_full_request()
            
            # 启动接收任务
            asyncio.create_task(self._receive_messages())
            
        except aiohttp.ClientError as e:
            error_msg = f"网络连接失败: {str(e)}"
            print(f"[X] {error_msg}")
            print(f"[X] 详细错误: {type(e).__name__}: {e}")
            self.is_connected = False
            if self.on_error_callback:
                self.on_error_callback(error_msg)
            raise
        except Exception as e:
            error_msg = f"连接失败: {type(e).__name__}: {str(e)}"
            print(f"[X] {error_msg}")
            import traceback
            traceback.print_exc()
            self.is_connected = False
            if self.on_error_callback:
                self.on_error_callback(error_msg)
            raise
    
    async def _send_full_request(self):
        """发送初始化请求"""
        try:
            request = RequestBuilder.new_full_client_request(self.seq)
            print(f"[调试] 发送初始化请求，seq={self.seq}, request_size={len(request)}")
            self.seq += 1
            
            await self.ws.send_bytes(request)
            print("[OK] 已发送初始化请求")
            
            # 等待初始化响应（设置超时）
            try:
                msg = await asyncio.wait_for(self.ws.receive(), timeout=10.0)
            except asyncio.TimeoutError:
                error_msg = "等待初始化响应超时（10秒）"
                print(f"[X] {error_msg}")
                self.is_connected = False
                raise Exception(error_msg)
            
            print(f"[调试] 收到响应类型: {msg.type}")
            
            if msg.type == aiohttp.WSMsgType.BINARY:
                print(f"[调试] 响应数据长度: {len(msg.data)}")
                response = ResponseParser.parse_response(msg.data)
                print(f"[调试] 解析后的响应: {response}")
                
                # 检查是否有解析错误
                if 'error' in response:
                    error_msg = f"响应解析错误: {response['error']}"
                    print(f"[X] {error_msg}")
                    self.is_connected = False
                    raise Exception(error_msg)
                
                # 检查消息类型
                message_type = response.get('message_type')
                payload = response.get('payload', {})
                
                # SERVER_ERROR_RESPONSE (0x0F) 才需要检查 code
                if message_type == MessageType.SERVER_ERROR_RESPONSE:
                    code = response.get('code', 0)
                    if code != 0:
                        error_msg = payload.get('message', f"初始化失败，错误码: {code}")
                        print(f"[X] 初始化失败 (code={code}): {error_msg}")
                        print(f"[X] 完整响应: {payload}")
                        self.is_connected = False
                        raise Exception(error_msg)
                
                # SERVER_FULL_RESPONSE (0x09) 表示成功，不需要检查 code
                if message_type == MessageType.SERVER_FULL_RESPONSE:
                    print(f"[OK] 初始化成功: {payload}")
                else:
                    print(f"[OK] 初始化成功 (message_type={message_type}): {payload}")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                error_msg = f"WebSocket错误: {msg.data}"
                print(f"[X] {error_msg}")
                self.is_connected = False
                raise Exception(error_msg)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                error_msg = "WebSocket连接已关闭"
                print(f"[X] {error_msg}")
                self.is_connected = False
                raise Exception(error_msg)
            else:
                error_msg = f"意外的消息类型: {msg.type}"
                print(f"[X] {error_msg}")
                self.is_connected = False
                raise Exception(error_msg)
            
        except Exception as e:
            print(f"[X] 发送初始化请求失败: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
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
            message_type = response.get('message_type')
            payload = response.get('payload', {})
            
            # 检查解析错误
            if 'error' in response:
                print(f"[X] 响应解析错误: {response['error']}")
                if self.on_error_callback:
                    self.on_error_callback(f"响应解析错误: {response['error']}")
                return
            
            # 检查错误响应类型
            if message_type == MessageType.SERVER_ERROR_RESPONSE:
                code = response.get('code', 0)
                error_msg = payload.get('error', payload.get('message', f'错误码: {code}'))
                print(f"[X] 识别错误 (code={code}): {error_msg}")
                if self.on_error_callback:
                    self.on_error_callback(error_msg)
                return
            
            # 处理正常响应
            if message_type == MessageType.SERVER_FULL_RESPONSE:
                # 检查payload中的错误
                if 'error' in payload:
                    error_msg = payload.get('error', '未知错误')
                    print(f"[X] 识别错误: {error_msg}")
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
            else:
                # 其他类型的响应（可能是中间结果）
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
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _pcm_to_wav_data(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """将PCM数据包装成WAV格式的data chunk
        
        根据错误信息"invalid WAV file format"，API期望WAV格式。
        但根据官方示例，应该发送WAV文件的data部分（去掉WAV头）。
        这里先尝试发送WAV的data chunk（包含"data"标识和大小）。
        """
        # WAV格式的data chunk结构：
        # - "data" (4 bytes)
        # - data size (4 bytes, little-endian)
        # - PCM data
        
        data_size = len(pcm_data)
        wav_data = bytearray()
        wav_data.extend(b'data')  # data chunk ID
        wav_data.extend(struct.pack('<I', data_size))  # data size (little-endian)
        wav_data.extend(pcm_data)  # PCM data
        
        return bytes(wav_data)
    
    @staticmethod
    def _pcm_to_full_wav(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """将PCM数据包装成完整的WAV文件格式（包含RIFF头和fmt子块）
        
        如果data chunk方式不行，可以尝试这种方式。
        """
        data_size = len(pcm_data)
        byte_rate = sample_rate * channels * (bits_per_sample // 8)
        block_align = channels * (bits_per_sample // 8)
        
        wav = bytearray()
        # RIFF头
        wav.extend(b'RIFF')
        wav.extend(struct.pack('<I', 36 + data_size))  # 文件大小 - 8
        wav.extend(b'WAVE')
        
        # fmt子块
        wav.extend(b'fmt ')
        wav.extend(struct.pack('<I', 16))  # fmt子块大小
        wav.extend(struct.pack('<H', 1))  # 音频格式 (1 = PCM)
        wav.extend(struct.pack('<H', channels))  # 声道数
        wav.extend(struct.pack('<I', sample_rate))  # 采样率
        wav.extend(struct.pack('<I', byte_rate))  # 字节率
        wav.extend(struct.pack('<H', block_align))  # 块对齐
        wav.extend(struct.pack('<H', bits_per_sample))  # 位深度
        
        # data子块
        wav.extend(b'data')
        wav.extend(struct.pack('<I', data_size))  # data大小
        wav.extend(pcm_data)  # PCM数据
        
        return bytes(wav)
    
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
                
                # 根据官方示例，直接发送原始PCM数据（从WAV文件中提取的data部分）
                # 不包装成任何格式，API会根据初始化请求中的配置来解析
                
                # 构建音频请求
                request = RequestBuilder.new_audio_only_request(
                    self.seq,
                    chunk,  # 直接发送原始PCM数据
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
                # 直接发送原始PCM数据
                request = RequestBuilder.new_audio_only_request(
                    self.seq,
                    chunk,  # 直接发送原始PCM数据
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
            
            # 重置序列号和缓冲区
            self.seq = 1
            self.audio_buffer.clear()
            
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
        self._connection_error = None  # 存储连接错误
        
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.is_running = True
            
            try:
                # 连接服务
                self.loop.run_until_complete(self.service.connect())
            except Exception as e:
                # 捕获连接错误
                self._connection_error = str(e)
                print(f"[X] 连接线程中的错误: {e}")
                import traceback
                traceback.print_exc()
                if on_error:
                    on_error(f"连接失败: {str(e)}")
                return
            
            # 保持循环运行
            try:
                self.loop.run_forever()
            finally:
                self.loop.close()
                self.is_running = False
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # 等待连接建立（最多等待3秒）
        for i in range(30):  # 30 * 0.1 = 3秒
            time.sleep(0.1)
            if self._connection_error:
                raise Exception(self._connection_error)
            if self.service.is_connected:
                return
        
        # 如果3秒后还没连接，检查是否有错误
        if self._connection_error:
            raise Exception(self._connection_error)
        if not self.service.is_connected:
            raise Exception("连接超时：3秒内未能建立连接")
    
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
