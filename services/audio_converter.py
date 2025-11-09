"""
音频格式转换服务
将WebM等格式转换为PCM格式（16kHz, 16bit, 单声道）
"""
import io
import base64
from pydub import AudioSegment


class AudioConverter:
    """音频格式转换类"""
    
    @staticmethod
    def audio_to_pcm(audio_data, sample_rate=16000, format_hint=None):
        """
        自动检测并转换音频为PCM格式（支持webm、wav、mp3）
        :param audio_data: 音频数据（bytes）
        :param sample_rate: 目标采样率，默认16kHz
        :param format_hint: 可选，前端传递的格式提示（如 'webm', 'wav', 'mp3'）
        :return: PCM格式的音频数据（bytes）
        """
        formats = ["webm", "wav", "mp3"]
        if format_hint:
            formats = [format_hint] + [f for f in formats if f != format_hint]
        for fmt in formats:
            try:
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=fmt)
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(sample_rate)
                audio = audio.set_sample_width(2)
                return audio.raw_data
            except Exception:
                continue
        raise Exception("音频格式转换失败: 不支持的或损坏的音频数据")
    
    @staticmethod
    def base64_audio_to_pcm(base64_data, sample_rate=16000, format_hint=None):
        """
        将Base64编码的音频转换为PCM格式，自动检测格式
        :param base64_data: Base64编码的音频数据
        :param sample_rate: 目标采样率，默认16kHz
        :param format_hint: 可选，前端传递的格式提示（如 'webm', 'wav', 'mp3'）
        :return: PCM格式的音频数据（bytes）
        """
        try:
            audio_data = base64.b64decode(base64_data)
            return AudioConverter.audio_to_pcm(audio_data, sample_rate, format_hint)
        except Exception as e:
            raise Exception(f"Base64音频转换失败: {str(e)}")
    
    @staticmethod
    def pcm_to_base64(pcm_data):
        """
        将PCM数据转换为Base64编码
        :param pcm_data: PCM格式的音频数据（bytes）
        :return: Base64编码的字符串
        """
        return base64.b64encode(pcm_data).decode('utf-8')

