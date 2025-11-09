"""
修复Supabase依赖问题的脚本
"""
import subprocess
import sys

def fix_supabase():
    """修复Supabase依赖"""
    print("正在修复Supabase依赖...")
    
    # 卸载旧版本
    print("\n1. 卸载旧版本...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "supabase"], 
                   capture_output=True)
    
    # 安装兼容版本
    print("\n2. 安装兼容版本...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "supabase==2.3.4"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Supabase安装成功")
    else:
        print(f"✗ 安装失败: {result.stderr}")
        return False
    
    # 检查安装
    print("\n3. 验证安装...")
    try:
        import supabase
        print(f"✓ Supabase版本: {supabase.__version__ if hasattr(supabase, '__version__') else '未知'}")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

if __name__ == '__main__':
    if fix_supabase():
        print("\n✓ 修复完成！请重新运行应用。")
    else:
        print("\n✗ 修复失败，请手动运行: pip install supabase==2.3.4")

