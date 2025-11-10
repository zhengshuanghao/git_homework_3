"""
DeepSeek LLM服务 - 用于行程规划和费用预算
使用火山方舟-模型广场提供的在线推理服务
"""
import json
import os
import time
import requests
try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    raise ImportError("请先安装火山方舟SDK: pip install volcenginesdkarkruntime")

from config import Config


class DeepSeekService:
    """DeepSeek LLM服务"""
    
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = getattr(Config, 'ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.model = getattr(Config, 'DEEPSEEK_MODEL', 'deepseek-v3-1-250821')  # 火山方舟模型ID
        try:
            self.client = Ark(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except Exception as e:
            raise Exception(f"初始化火山方舟客户端失败: {str(e)}")
    
    def is_configured(self):
        """检查配置是否完整"""
        return bool(self.api_key)
    
    def _call_api(self, messages, temperature=0.7, max_tokens=2000):
        """调用火山方舟 API"""
        if not self.is_configured():
            raise Exception("DeepSeek API未配置")
        
        # 首先尝试使用官方 SDK（推荐）
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            # 如果怀疑是 SSL / 握手超时或 EOF 错误，尝试使用 requests 回退（临时关闭证书验证用于排查）
            low = err_msg.lower()
            if any(k in low for k in ("ssl", "handshake", "unexpected_eof", "eof occurred", "timed out")):
                # 尝试通过 requests 直接调用 REST 接口以获得更明确的错误或成功
                try:
                    # 构建 REST URL：Ark SDK base path 为 /api/v3，直接调用 chat/completions
                    rest_url = f"{self.base_url}/chat/completions"
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }

                    # 决定是否校验证书：优先使用 certifi 提供的 CA 证书；允许通过环境变量 DISABLE_SSL_VERIFY=1 来临时禁用
                    verify = True
                    try:
                        import certifi
                        verify = certifi.where()
                    except Exception:
                        # certifi 不可用时，仍然允许 requests 使用系统默认 CA，除非环境变量要求禁用
                        if os.getenv('DISABLE_SSL_VERIFY', '0') == '1':
                            verify = False

                    # 使用带重试的 Session 减少瞬时网络错误影响
                    session = requests.Session()
                    try:
                        from requests.adapters import HTTPAdapter
                        from urllib3.util.retry import Retry
                        retries = Retry(total=2, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
                        adapter = HTTPAdapter(max_retries=retries)
                        session.mount('https://', adapter)
                        session.mount('http://', adapter)
                    except Exception:
                        # 如果无法导入 Retry，也继续使用默认 session
                        pass

                    resp = session.post(rest_url, json=payload, headers=headers, timeout=60, verify=verify)
                    resp.raise_for_status()
                    result = resp.json()
                    return result.get('choices', [{}])[0].get('message', {}).get('content', '')
                except Exception as re:
                    # 将原始 SDK 错误和回退请求的错误一并返回，便于定位
                    raise Exception(f"DeepSeek API调用失败 (SDK: {err_msg})；回退请求失败: {str(re)}")
            # 非 SSL 类问题，直接抛出 SDK 的错误
            raise Exception(f"DeepSeek API调用失败: {err_msg}")
    
    def generate_travel_plan(self, user_input):
        """生成旅行计划"""
        system_prompt = """你是一个专业的旅行规划师。根据用户的输入，生成详细的旅行计划。
请以JSON格式返回，包含以下字段：
{
    "destination": "目的地",
    "duration": "天数",
    "budget": "预算",
    "people": "人数",
    "preferences": ["偏好1", "偏好2"],
    "itinerary": [
        {
            "day": 1,
            "date": "日期",
            "activities": [
                {
                    "time": "时间",
                    "type": "类型（交通/住宿/景点/餐厅）",
                    "name": "名称",
                    "description": "描述",
                    "location": {
                        "name": "地点名称",
                        "lng": 经度,
                        "lat": 纬度
                    },
                    "cost": 费用,
                    "duration": "预计时长"
                }
            ],
            "total_cost": 当日总费用
        }
    ],
    "total_budget": 总预算,
    "tips": ["建议1", "建议2"]
}

请确保返回的是有效的JSON格式，不要包含其他文字。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self._call_api(messages, temperature=0.7, max_tokens=4000)
            
            # 尝试解析JSON响应
            try:
                # 去除可能的markdown代码块标记
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(response)
                return plan
            except json.JSONDecodeError:
                # 如果解析失败，返回结构化文本
                return {
                    "destination": "未识别",
                    "duration": "未指定",
                    "budget": "未指定",
                    "people": "未指定",
                    "preferences": [],
                    "itinerary": [],
                    "total_budget": 0,
                    "tips": [],
                    "raw_response": response
                }
        except Exception as e:
            raise Exception(f"生成旅行计划失败: {str(e)}")
    
    def estimate_budget(self, travel_plan):
        """估算费用预算"""
        system_prompt = """你是一个专业的旅行费用估算师。根据旅行计划，估算各项费用并分析预算合理性。
请以JSON格式返回：
{
    "estimated_cost": 总估算费用,
    "breakdown": {
        "transportation": 交通费用,
        "accommodation": 住宿费用,
        "food": 餐饮费用,
        "attractions": 景点费用,
        "shopping": 购物费用,
        "other": 其他费用
    },
    "budget_status": "预算状态（充足/紧张/不足）",
    "suggestions": ["建议1", "建议2"]
}"""
        
        plan_text = json.dumps(travel_plan, ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分析以下旅行计划的费用：\n{plan_text}"}
        ]
        
        try:
            response = self._call_api(messages, temperature=0.5, max_tokens=1000)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                budget = json.loads(response)
                return budget
            except json.JSONDecodeError:
                return {
                    "estimated_cost": 0,
                    "breakdown": {},
                    "budget_status": "未知",
                    "suggestions": []
                }
        except Exception as e:
            raise Exception(f"估算费用失败: {str(e)}")










