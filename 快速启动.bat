@echo off
chcp 65001 >nul
echo ============================================================
echo AI旅行规划师 - 快速启动脚本
echo ============================================================
echo.

echo [1/3] 检查配置...
python diagnose_speech.py
if errorlevel 1 (
    echo.
    echo ❌ 配置检查失败，请查看上面的错误信息
    pause
    exit /b 1
)

echo.
echo [2/3] 测试语音识别连接...
python test_speech_connection.py
if errorlevel 1 (
    echo.
    echo ❌ 连接测试失败，请查看上面的错误信息
    pause
    exit /b 1
)

echo.
echo [3/3] 启动应用...
echo.
echo ============================================================
echo 应用即将启动
echo 请在浏览器中访问: http://localhost:8080
echo 按 Ctrl+C 停止服务器
echo ============================================================
echo.

python run.py
