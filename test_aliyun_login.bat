@echo off
echo ========================================
echo 测试阿里云容器镜像服务登录
echo ========================================
echo.
echo 请输入您在阿里云容器镜像服务"访问凭证"页面看到的用户名
set /p USERNAME="用户名: "
echo.
echo 请输入您设置的固定密码
set /p PASSWORD="密码: "
echo.
echo 正在尝试登录...
echo.
docker login --username=%USERNAME% --password=%PASSWORD% registry.cn-hangzhou.aliyuncs.com
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo ✓ 登录成功！
    echo ========================================
    echo.
    echo 请将以下信息添加到GitHub Secrets:
    echo.
    echo ALIYUN_REGISTRY_USERNAME = %USERNAME%
    echo ALIYUN_REGISTRY_PASSWORD = [您刚才输入的密码]
    echo.
) else (
    echo ========================================
    echo ✗ 登录失败！
    echo ========================================
    echo.
    echo 请检查:
    echo 1. 用户名是否正确（从阿里云控制台复制）
    echo 2. 密码是否正确（固定密码）
    echo 3. 是否已在阿里云设置了固定密码
    echo.
)
pause
