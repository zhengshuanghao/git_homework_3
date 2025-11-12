"""
DeepSeek LLM服务 - 用于行程规划和费用预算
使用火山方舟-模型广场提供的在线推理服务
"""
import json
import os
import time
import requests
import textwrap
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
    
    def generate_travel_plan(self, user_input, user_preferences=None):
        """生成旅行计划
        
        Args:
            user_input: 用户输入的旅行需求
            user_preferences: 用户偏好设置（可选）
        """
        system_prompt = """你是一个专业的旅行规划师。根据用户的输入和偏好设置，生成详细的旅行计划。

**重要要求：**
1. 住宿推荐必须具体，包括酒店名称、地址、价格区间、特色
2. 餐厅推荐必须具体，包括餐厅名称、招牌菜、人均消费、地址
3. 根据用户预算推荐合适档次的酒店和餐厅
4. 考虑用户的偏好设置（如有）
5. **必须返回完整的、格式正确的JSON，不要截断**

请以JSON格式返回，包含以下字段：
{
    "destination": "目的地",
    "duration": 5,
    "budget": 5000,
    "people": 1,
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
                    "details": {
                        "address": "具体地址（住宿和餐厅必填）",
                        "price_range": "价格区间",
                        "rating": "评分",
                        "highlights": ["特色1", "特色2"],
                        "contact": "联系方式（可选）"
                    },
                    "location": {
                        "name": "地点名称",
                        "lng": 104.06,
                        "lat": 30.67
                    },
                    "cost": 100,
                    "duration": "预计时长"
                }
            ],
            "total_cost": 500
        }
    ],
    "accommodation_summary": [
        {
            "hotel_name": "酒店名称",
            "nights": 4,
            "total_cost": 1200,
            "address": "地址",
            "features": ["特色1", "特色2"]
        }
    ],
    "restaurant_recommendations": [
        {
            "name": "餐厅名称",
            "cuisine": "菜系",
            "signature_dishes": ["招牌菜1", "招牌菜2"],
            "avg_cost": 80,
            "address": "地址"
        }
    ],
    "total_budget": 5000,
    "tips": ["建议1", "建议2"]
}

**关键：请确保返回的是完整的、有效的JSON格式，所有括号和引号必须闭合，不要包含其他文字或注释。**"""
        
        # 构建完整的用户输入
        full_input = user_input
        
        # 如果有用户偏好，添加到输入中
        if user_preferences:
            from services.preference_service import PreferenceService
            pref_service = PreferenceService()
            pref_text = pref_service.format_preferences_for_prompt(user_preferences)
            if pref_text:
                full_input = f"{user_input}\n\n{pref_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_input}
        ]
        
        try:
            # 增加 max_tokens 以确保响应不被截断
            response = self._call_api(messages, temperature=0.7, max_tokens=8000)
            
            print(f"[DeepSeekService] 收到响应，长度: {len(response)} 字符")
            print(f"[DeepSeekService] 响应前200字符: {response[:200]}")
            print(f"[DeepSeekService] 响应后200字符: {response[-200:]}")
            
            parsed_plan = self._parse_plan_response(response)
            if parsed_plan is not None:
                print("[DeepSeekService] JSON 解析成功")
                return parsed_plan
            
            # 兜底：返回包含原始响应的占位结构
            cleaned_response = self._strip_code_fences(str(response))
            print("[DeepSeekService] 无法解析模型响应，返回占位数据。")
            print(f"[DeepSeekService] 完整响应: {cleaned_response}")
            return {
                "destination": "未识别",
                "duration": "未指定",
                "budget": "未指定",
                "people": "未指定",
                "preferences": [],
                "itinerary": [],
                "total_budget": 0,
                "tips": [],
                "raw_response": cleaned_response
            }
        except Exception as e:
            print(f"[DeepSeekService] 生成旅行计划异常: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"生成旅行计划失败: {str(e)}")
    
    # ------------------------- 辅助方法 -------------------------
    def _strip_code_fences(self, text):
        """移除 Markdown 代码块包裹"""
        if not text:
            return text
        stripped = text.strip()
        if stripped.startswith("```"):
            parts = stripped.split("```")
            # 可能形式：```json ... ``` 或 ``` ... ```
            if len(parts) >= 3:
                return parts[1 if parts[1].strip() else 2].strip()
            return parts[-1].strip()
        # 处理可能的 "json" 或 "JSON" 前缀
        lowered = stripped.lower()
        if lowered.startswith("json") and len(stripped) > 4:
            remainder = stripped[4:]
            if remainder[:1].isspace() or remainder[:1] in ("{", "["):
                return remainder.lstrip()
        return stripped
    
    def _extract_json_candidate(self, text):
        """尝试从文本中提取最大 JSON 对象"""
        if not text:
            return None
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return text[start:end + 1]
    
    def _parse_plan_response(self, response_text):
        """解析模型返回的文本为 JSON。必要时尝试一次自动修复。"""
        if not response_text:
            print("[DeepSeekService] 响应为空")
            return None
            
        cleaned = self._strip_code_fences(response_text)
        candidates = []
        if cleaned:
            candidates.append(cleaned)
            extracted = self._extract_json_candidate(cleaned)
            if extracted and extracted not in candidates:
                candidates.append(extracted)
        
        # 尝试解析所有候选项
        for i, candidate in enumerate(candidates):
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                print(f"[DeepSeekService] 候选项 {i+1} 解析成功")
                return parsed
            except json.JSONDecodeError as e:
                print(f"[DeepSeekService] 候选项 {i+1} 解析失败: {str(e)}")
                print(f"[DeepSeekService] 失败位置: 第 {e.lineno} 行, 第 {e.colno} 列")
                print(f"[DeepSeekService] 错误附近内容: {candidate[max(0, e.pos-50):min(len(candidate), e.pos+50)]}")
        
        # 若直接解析失败，尝试让模型自我修复一次
        print("[DeepSeekService] 尝试自动修复 JSON...")
        repaired = self._attempt_repair_json(cleaned or response_text)
        if repaired:
            try:
                parsed = json.loads(repaired)
                print("[DeepSeekService] 修复后的 JSON 解析成功")
                return parsed
            except json.JSONDecodeError as e:
                print(f"[DeepSeekService] 修复后的 JSON 仍然解析失败: {str(e)}")
                # 再次直接解析失败，尝试截取主体后重试
                extracted = self._extract_json_candidate(repaired)
                if extracted:
                    try:
                        parsed = json.loads(extracted)
                        print("[DeepSeekService] 从修复结果中提取的 JSON 解析成功")
                        return parsed
                    except json.JSONDecodeError as e2:
                        print(f"[DeepSeekService] 提取后仍然失败: {str(e2)}")
        
        print("[DeepSeekService] 所有解析尝试均失败")
        return None
    
    def _attempt_repair_json(self, raw_text):
        """调用模型将输出修正为合法 JSON"""
        if not raw_text:
            return None
        try:
            repair_prompt = textwrap.dedent(
                """
                你是一个严格的JSON修复工具。请将下面的内容转换为**完整的、合法的JSON字符串**：
                - 严格遵循JSON标准：使用双引号、不能有注释、不能有悬挂逗号
                - 确保所有括号、引号都正确闭合
                - 不要添加任何解释或额外文本，只输出 JSON 本身
                - 如果内容被截断，请补全缺失的部分（根据上下文推断合理值）
                - 如果内容中缺失字段，可根据上下文推断合理值；无法确定时使用空字符串、0 或空数组
                - 确保返回的JSON是完整的，可以被 json.loads() 成功解析
                """
            ).strip()
            
            messages = [
                {"role": "system", "content": repair_prompt},
                {
                    "role": "user",
                    "content": f"原始内容（可能不完整或格式错误）：\n{raw_text[:3000]}\n\n请输出修复后的完整JSON："
                }
            ]
            print("[DeepSeekService] 调用模型修复 JSON...")
            repaired = self._call_api(messages, temperature=0.0, max_tokens=8000)
            cleaned = self._strip_code_fences(repaired)
            print(f"[DeepSeekService] 修复后的 JSON 长度: {len(cleaned)} 字符")
            return cleaned
        except Exception as repair_error:
            print(f"[DeepSeekService] JSON修复调用失败: {repair_error}")
            import traceback
            traceback.print_exc()
            return None
    
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










