# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
import json
import time
import threading
import urllib.parse
import logging
import uuid
from websocket import create_connection, WebSocketException
import websocket
import datetime

# 全局配置：与服务端确认的固定参数
FIXED_PARAMS = {
    "audio_encode": "pcm_s16le",
    "lang": "autodialect",
    "samplerate": "16000"  # 固定16k采样率，对应每40ms发送1280字节
}
AUDIO_FRAME_SIZE = 1280  # 每帧音频字节数（16k采样率、16bit位深、40ms）
FRAME_INTERVAL_MS = 40    # 每帧发送间隔（毫秒）


class RTASRClient():
    def __init__(self, app_id, access_key_id, access_key_secret, audio_path):
        self.app_id = app_id
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.audio_path = audio_path
        self.base_ws_url = "wss://office-api-ast-dx.iflyaisol.com/ast/communicate/v1"
        self.ws = None
        self.is_connected = False
        self.recv_thread = None
        self.session_id = None
        self.is_sending_audio = False  # 防止并发发送
        self.audio_file_size = 0  # 音频文件大小（字节）

    def _get_audio_file_size(self):
        """获取音频文件大小（新增方法，修复AttributeError）"""
        try:
            with open(self.audio_path, "rb") as f:
                f.seek(0, 2)  # 移动到文件末尾
                return f.tell()  # 返回文件大小
        except Exception as e:
            print(f"【获取文件大小失败】{str(e)}")
            return 0

    def _generate_auth_params(self):
        """生成鉴权参数（严格按字典序排序，匹配Java TreeMap）"""
        auth_params = {
            "accessKeyId": self.access_key_id,
            "appId": self.app_id,
            "uuid": uuid.uuid4().hex,
            "utc": self._get_utc_time(),
            **FIXED_PARAMS
        }

        # 计算签名：过滤空值 → 字典序排序 → URL编码 → 拼接基础字符串
        sorted_params = dict(sorted([
            (k, v) for k, v in auth_params.items()
            if v is not None and str(v).strip() != ""
        ]))
        base_str = "&".join([
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
            for k, v in sorted_params.items()
        ])

        # HMAC-SHA1 加密 + Base64编码
        signature = hmac.new(
            self.access_key_secret.encode("utf-8"),
            base_str.encode("utf-8"),
            hashlib.sha1
        ).digest()
        auth_params["signature"] = base64.b64encode(signature).decode("utf-8")
        return auth_params

    def _get_utc_time(self):
        """生成服务端要求的UTC时间格式：yyyy-MM-dd'T'HH:mm:ss+0800"""
        beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
        now = datetime.datetime.now(beijing_tz)
        return now.strftime("%Y-%m-%dT%H:%M:%S%z")

    def connect(self):
        """建立WebSocket连接（增加稳定性配置）"""
        try:
            auth_params = self._generate_auth_params()
            params_str = urllib.parse.urlencode(auth_params)
            full_ws_url = f"{self.base_ws_url}?{params_str}"
            print(f"【连接信息】完整URL：{full_ws_url}")

            # 初始化WebSocket连接（禁用自动文本解析，延长超时）
            self.ws = create_connection(
                full_ws_url,
                timeout=15,
                enable_multithread=True  # 支持多线程并发
            )
            self.is_connected = True
            print("【连接成功】WebSocket握手完成，等待服务端就绪...")
            time.sleep(1.5)  # 确保服务端完全初始化

            # 启动接收线程（单独处理服务端消息）
            self.recv_thread = threading.Thread(target=self._recv_msg, daemon=True)
            self.recv_thread.start()
            return True
        except WebSocketException as e:
            print(f"【连接失败】WebSocket错误：{str(e)}")
            if hasattr(e, 'status_code'):
                print(f"【服务端状态码】{e.status_code}")
            return False
        except Exception as e:
            print(f"【连接异常】其他错误：{str(e)}")
            return False

    def _recv_msg(self):
        """接收服务端消息（增加连接状态判断，修复非套接字操作错误）"""
        while True:
            # 先判断连接状态，避免操作已关闭的连接
            if not self.is_connected or not self.ws:
                print("【接收线程】连接已关闭，退出接收循环")
                break

            try:
                msg = self.ws.recv()
                if not msg:
                    print("【接收消息】服务端关闭连接")
                    self.close()
                    break

                # 仅处理文本消息（服务端返回的JSON均为文本）
                if isinstance(msg, str):
                    try:
                        msg_json = json.loads(msg)
                        print(f"【接收消息】{msg_json}")

                        # 更新会话ID（用于结束标记关联）
                        if (msg_json.get('msg_type') == 'action' 
                            and 'sessionId' in msg_json.get('data', {})):
                            self.session_id = msg_json['data']['sessionId']
                    except json.JSONDecodeError:
                        print(f"【接收异常】非JSON文本消息：{msg[:50]}...")
                else:
                    print(f"【接收提示】收到二进制消息（长度：{len(msg)}字节），忽略")

            except WebSocketException as e:
                print(f"【接收异常】连接中断：{str(e)}")
                self.close()
                break
            except OSError as e:
                # 捕获Windows套接字错误（如非套接字操作）
                print(f"【接收异常】系统套接字错误：{str(e)}")
                self.close()
                break
            except Exception as e:
                print(f"【接收异常】未知错误：{str(e)}")
                self.close()
                break

    def send_audio(self):
        """
        精确控制音频发送节奏：
        1. 16k采样率每40ms发送1280字节
        2. 基于起始时间计算理论发送时间，抵消累计误差
        """
        if not self.is_connected or not self.ws:
            print("【发送失败】WebSocket未连接")
            return False
        if self.is_sending_audio:
            print("【发送失败】已有发送任务在执行")
            return False

        self.is_sending_audio = True
        frame_index = 0  # 帧索引（从0开始）
        start_time = None  # 第一次发送的时间戳（毫秒）
        self.audio_file_size = self._get_audio_file_size()  # 提前获取文件大小
        
        try:
            with open(self.audio_path, "rb") as f:
                # 计算总帧数和预估时长
                total_frames = self.audio_file_size // AUDIO_FRAME_SIZE
                remaining_bytes = self.audio_file_size % AUDIO_FRAME_SIZE
                if remaining_bytes > 0:
                    total_frames += 1  # 剩余不足一帧的部分也作为一帧发送
                estimated_duration = (total_frames * FRAME_INTERVAL_MS) / 1000  # 秒
                print(f"【发送配置】音频文件大小：{self.audio_file_size}字节 | 总帧数：{total_frames} | 预估时长：{estimated_duration:.1f}秒")
                print(f"【发送配置】每{FRAME_INTERVAL_MS}ms发送{FRAME_INTERVAL_MS}字节，严格控制节奏")
                f.seek(0)  # 重置文件指针到开头

                # 循环发送音频帧
                while True:
                    chunk = f.read(AUDIO_FRAME_SIZE)
                    if not chunk:
                        print(f"【发送完成】所有音频帧发送完毕（共{frame_index}帧）")
                        break

                    # 1. 记录第一次发送的起始时间（毫秒级）
                    if start_time is None:
                        start_time = time.time() * 1000  # 转换为毫秒
                        print(f"【发送开始】起始时间：{start_time:.0f}ms（基准时间）")

                    # 2. 计算当前帧的理论发送时间（基于起始时间和帧索引）
                    expected_send_time = start_time + (frame_index * FRAME_INTERVAL_MS)

                    # 3. 计算当前实际时间与理论时间的差值，动态调整休眠
                    current_time = time.time() * 1000  # 当前时间（毫秒）
                    time_diff = expected_send_time - current_time  # 差值（ms）

                    # 4. 休眠（仅当差值为正时休眠，避免负向等待）
                    if time_diff > 0.1:  # 差值大于0.1ms才休眠，避免频繁微小休眠
                        time.sleep(time_diff / 1000)  # 转换为秒
                        # 打印节奏控制日志（每10帧打印一次，避免冗余）
                        if frame_index % 10 == 0:
                            actual_send_time = time.time() * 1000
                            print(f"【节奏控制】帧{frame_index} | 理论时间：{expected_send_time:.0f}ms | 实际时间：{actual_send_time:.0f}ms | 误差：{actual_send_time - expected_send_time:.1f}ms")

                    # 5. 发送当前帧（明确为二进制消息）
                    self.ws.send_binary(chunk)
                    frame_index += 1

                # 6. 发送结束标记（标准JSON文本消息）
                end_msg = {"end": True}
                if self.session_id:
                    end_msg["sessionId"] = self.session_id  # 关联当前会话
                end_msg_str = json.dumps(end_msg, ensure_ascii=False)
                self.ws.send(end_msg_str)
                print(f"【发送结束】已发送标准JSON结束标记：{end_msg_str}")
            return True
        except FileNotFoundError:
            print(f"【发送失败】音频文件不存在：{self.audio_path}")
            return False
        except PermissionError:
            print(f"【发送失败】无权限读取音频文件：{self.audio_path}")
            return False
        except WebSocketException as e:
            print(f"【发送失败】WebSocket连接中断：{str(e)}")
            self.close()
            return False
        except Exception as e:
            print(f"【发送异常】未知错误：{str(e)}")
            self.close()
            return False
        finally:
            self.is_sending_audio = False

    def close(self):
        """安全关闭WebSocket连接（增加状态保护）"""
        if self.is_connected and self.ws:
            self.is_connected = False
            try:
                # 先判断连接是否仍处于打开状态
                if self.ws.connected:
                    self.ws.close(status=1000, reason="客户端正常关闭")
                print("【连接关闭】WebSocket已安全关闭")
            except Exception as e:
                print(f"【关闭异常】关闭时出错：{str(e)}")
        else:
            print("【连接关闭】WebSocket已断开或未初始化")

if __name__ == "__main__":
    # 配置日志（过滤冗余信息）
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("websocket").setLevel(logging.WARNING)

    # 1. 从控制台获取密钥信息：https://console.xfyun.cn/services/rta_new
    APP_ID = "XXXXXXXX"
    ACCESS_KEY_ID = "XXXXXXXXXXXXXXXXXXXXXXXX"
    ACCESS_KEY_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXX"
    # 建议使用绝对路径，避免相对路径错误
    AUDIO_FILE_PATH = r"python\\test_1.pcm"

    # 2. 执行核心流程
    client = RTASRClient(APP_ID, ACCESS_KEY_ID, ACCESS_KEY_SECRET, AUDIO_FILE_PATH)
    try:
        # 建立连接
        if not client.connect():
            print("【程序退出】连接失败")
            exit(1)

        # 发送音频（精确节奏控制）
        if not client.send_audio():
            print("【程序退出】音频发送失败")
            exit(1)

        # 等待识别结果（基于音频预估时长+5秒）
        estimated_duration = (client.audio_file_size // AUDIO_FRAME_SIZE) * FRAME_INTERVAL_MS / 1000
        wait_time = int(estimated_duration) + 5
        print(f"【等待结果】预估识别时长{estimated_duration:.1f}秒，等待{wait_time}秒接收结果...")
        
        # 等待期间持续检查连接状态
        for _ in range(wait_time):
            if not client.is_connected:
                print("【等待中断】连接已关闭，提前结束等待")
                break
            time.sleep(1)

        print("【程序结束】识别流程完成")
    except KeyboardInterrupt:
        print("【程序退出】用户手动中断")
    finally:
        client.close()
