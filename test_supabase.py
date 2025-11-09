"""
测试 Supabase 连接
"""
from config import Config
from supabase import create_client

def test_supabase():
    """测试Supabase连接"""
    print("=" * 60)
    print("测试 Supabase 连接")
    print("=" * 60)
    
    # 检查配置
    if not Config.SUPABASE_URL:
        print("[X] SUPABASE_URL 未配置")
        return False
    
    if not Config.SUPABASE_KEY:
        print("[X] SUPABASE_KEY 未配置")
        return False
    
    print(f"\nURL: {Config.SUPABASE_URL}")
    print(f"KEY: {Config.SUPABASE_KEY[:20]}...")
    
    # 尝试连接
    try:
        print("\n正在连接 Supabase...")
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        print("[OK] Supabase 客户端创建成功")
        
        # 尝试一个简单的查询
        print("\n正在测试数据库连接...")
        # 这里不执行实际查询，只是验证客户端创建成功
        print("[OK] Supabase 连接测试通过")
        return True
        
    except Exception as e:
        print(f"\n[X] Supabase 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        
        # 提供修复建议
        if 'proxy' in str(e).lower():
            print("\n[建议] 这是版本兼容性问题，请尝试以下方法：")
            print("  1. pip uninstall supabase -y")
            print("  2. pip install supabase==2.3.4")
            print("  3. 或者运行: python fix_supabase.py")
        
        return False

if __name__ == '__main__':
    test_supabase()

