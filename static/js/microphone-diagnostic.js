/**
 * 麦克风诊断工具
 * 帮助用户排查麦克风访问问题
 */

async function diagnoseMicrophone() {
    const results = {
        browserSupport: false,
        secureContext: false,
        devicesAvailable: false,
        permissionGranted: false,
        streamAccessible: false,
        errors: []
    };
    
    console.log('=== 麦克风诊断开始 ===');
    
    // 1. 检查浏览器支持
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        results.browserSupport = true;
        console.log('✅ 浏览器支持 getUserMedia API');
    } else {
        results.browserSupport = false;
        results.errors.push('浏览器不支持 getUserMedia API');
        console.error('❌ 浏览器不支持 getUserMedia API');
        return results;
    }
    
    // 2. 检查安全上下文
    const isSecure = window.isSecureContext || 
                     location.protocol === 'https:' || 
                     location.hostname === 'localhost' || 
                     location.hostname === '127.0.0.1';
    results.secureContext = isSecure;
    if (isSecure) {
        console.log('✅ 在安全上下文中运行');
    } else {
        results.errors.push('不在安全上下文中（需要使用 HTTPS 或 localhost）');
        console.error('❌ 不在安全上下文中:', location.href);
    }
    
    // 3. 枚举音频设备
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(d => d.kind === 'audioinput');
        results.devicesAvailable = audioInputs.length > 0;
        
        if (audioInputs.length > 0) {
            console.log(`✅ 找到 ${audioInputs.length} 个音频输入设备:`);
            audioInputs.forEach((device, index) => {
                console.log(`  ${index + 1}. ${device.label || '未命名设备'} (${device.deviceId.substring(0, 20)}...)`);
            });
        } else {
            results.errors.push('未找到音频输入设备');
            console.error('❌ 未找到音频输入设备');
        }
    } catch (err) {
        results.errors.push('枚举设备失败: ' + err.message);
        console.error('❌ 枚举设备失败:', err);
    }
    
    // 4. 检查权限状态
    try {
        if (navigator.permissions && navigator.permissions.query) {
            const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
            results.permissionGranted = permissionStatus.state === 'granted';
            
            console.log(`权限状态: ${permissionStatus.state}`);
            if (permissionStatus.state === 'granted') {
                console.log('✅ 麦克风权限已授予');
            } else if (permissionStatus.state === 'prompt') {
                console.log('⚠️ 麦克风权限需要用户确认');
            } else {
                console.log('❌ 麦克风权限被拒绝');
                results.errors.push('麦克风权限被拒绝');
            }
        } else {
            console.log('⚠️ 无法检查权限状态（浏览器不支持 Permissions API）');
        }
    } catch (err) {
        console.warn('检查权限状态失败:', err);
    }
    
    // 5. 尝试访问麦克风
    let testStream = null;
    try {
        console.log('尝试访问麦克风...');
        testStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        results.streamAccessible = true;
        console.log('✅ 成功访问麦克风');
        
        // 检查流的详细信息
        const tracks = testStream.getAudioTracks();
        tracks.forEach(track => {
            console.log(`  轨道: ${track.label}`);
            console.log(`  设置:`, track.getSettings());
            console.log(`  状态: ${track.readyState}`);
        });
        
        // 清理
        testStream.getTracks().forEach(track => track.stop());
    } catch (err) {
        results.streamAccessible = false;
        results.errors.push(`${err.name}: ${err.message}`);
        console.error(`❌ 访问麦克风失败: ${err.name} - ${err.message}`);
        
        // 提供详细错误信息
        switch (err.name) {
            case 'NotAllowedError':
                console.error('   原因: 用户拒绝了权限或权限被系统阻止');
                break;
            case 'NotFoundError':
                console.error('   原因: 未找到可用的麦克风设备');
                break;
            case 'NotReadableError':
                console.error('   原因: 麦克风无法读取（可能被其他应用占用）');
                break;
            case 'OverconstrainedError':
                console.error('   原因: 麦克风不支持请求的配置');
                break;
            case 'SecurityError':
                console.error('   原因: 安全错误（可能不在安全上下文中）');
                break;
            default:
                console.error('   原因: 未知错误');
        }
    }
    
    console.log('=== 麦克风诊断结束 ===');
    return results;
}

// 在控制台中运行诊断
window.diagnoseMicrophone = diagnoseMicrophone;

// 自动运行诊断（如果页面加载时出错）
if (typeof window !== 'undefined') {
    console.log('麦克风诊断工具已加载。在控制台运行 diagnoseMicrophone() 进行诊断。');
}

