@echo off
chcp 65001 >nul

echo.
echo ============================================================
echo           🗺️  AI旅行规划师 - 快速启动
echo ============================================================
echo.

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在！
    echo.
    echo 请先创建虚拟环境并安装依赖：
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/2] 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 启动应用
echo [2/2] 启动应用...
echo.
python app.py

echo.
echo 服务器已停止。
pause
