"""
测试DeepSeek服务（火山方舟）
"""
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.deepseek_service import DeepSeekService
from config import Config

def test_deepseek_service():
    """测试DeepSeek服务"""
    print("=" * 60)
    print("测试火山方舟 DeepSeek 服务")
    print("=" * 60)
    
    # 检查配置
    print(f"\n1. 检查配置:")
    print(f"   API Key: {'已设置' if Config.DEEPSEEK_API_KEY else '未设置'}")
    print(f"   Base URL: {Config.ARK_BASE_URL}")
    print(f"   Model: {Config.DEEPSEEK_MODEL}")
    
    if not Config.DEEPSEEK_API_KEY:
        print("\n❌ 错误: ARK_API_KEY 未配置")
        print("请在 .env 文件中设置 ARK_API_KEY")
        return
    
    # 初始化服务
    print(f"\n2. 初始化服务...")
    try:
        service = DeepSeekService()
        print("   ✓ 服务初始化成功")
    except Exception as e:
        print(f"   ❌ 服务初始化失败: {e}")
        return
    
    # 测试生成旅行计划
    print(f"\n3. 测试生成旅行计划...")
    test_input = "我想去北京旅游3天，预算5000元，喜欢历史文化"
    print(f"   输入: {test_input}")
    
    try:
        print("   正在调用API...")
        plan = service.generate_travel_plan(test_input)
        print("   ✓ 旅行计划生成成功")
        print(f"\n   目的地: {plan.get('destination', '未知')}")
        print(f"   天数: {plan.get('duration', '未知')}")
        print(f"   预算: {plan.get('budget', '未知')}")
        
        if 'itinerary' in plan and plan['itinerary']:
            print(f"   行程天数: {len(plan['itinerary'])} 天")
        
        if 'raw_response' in plan:
            print(f"\n   原始响应:\n{plan['raw_response'][:200]}...")
            
    except Exception as e:
        print(f"   ❌ 生成旅行计划失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_deepseek_service()
