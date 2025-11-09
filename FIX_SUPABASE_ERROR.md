# 修复 Supabase 初始化错误

## 错误信息
```
Supabase初始化失败: Client.__init__() got an unexpected keyword argument 'proxy'
```

## 问题原因
这个错误通常是由于 `supabase-py` 库与其依赖项版本不兼容导致的。

## 解决方案

### 方案一：重新安装 Supabase（推荐）

1. **卸载旧版本**
   ```bash
   pip uninstall supabase -y
   ```

2. **安装指定版本**
   ```bash
   pip install supabase==2.3.4
   ```

3. **或者使用修复脚本**
   ```bash
   python fix_supabase.py
   ```

### 方案二：在虚拟环境中重新安装

1. **激活虚拟环境**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **重新安装所有依赖**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### 方案三：升级到最新版本

```bash
pip install --upgrade supabase
```

### 方案四：清理并重新安装

```bash
# 卸载相关包
pip uninstall supabase postgrest storage3 gotrue realtime -y

# 重新安装
pip install supabase==2.3.4
```

## 验证安装

运行以下命令检查 Supabase 是否正确安装：

```bash
python -c "from supabase import create_client; print('Supabase导入成功')"
```

## 如果问题仍然存在

### 1. 检查 Python 版本
确保使用 Python 3.8 或更高版本：
```bash
python --version
```

### 2. 检查依赖冲突
```bash
pip list | findstr supabase
pip list | findstr postgrest
```

### 3. 使用虚拟环境
如果系统中有多个 Python 环境，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
# 或
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 4. 临时解决方案
如果 Supabase 功能不是必需的，应用仍然可以运行，只是用户认证和数据存储功能将不可用。

## 当前状态

应用已经修改为：即使 Supabase 初始化失败，应用也会继续运行。你会在控制台看到警告信息，但应用不会崩溃。

## 测试 Supabase 连接

创建测试脚本 `test_supabase.py`:

```python
from config import Config
from supabase import create_client

try:
    client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    print("✓ Supabase 连接成功")
except Exception as e:
    print(f"✗ Supabase 连接失败: {e}")
```

运行测试：
```bash
python test_supabase.py
```

## 联系支持

如果以上方法都无法解决问题，请：
1. 检查 Supabase 官方文档
2. 查看 GitHub Issues: https://github.com/supabase/supabase-py/issues
3. 提供完整的错误信息和环境信息

