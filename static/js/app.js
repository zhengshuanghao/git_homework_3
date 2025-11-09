// 全局变量
let map = null;
let markers = [];
let currentUser = null;
let socket = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// 初始化
document.addEventListener('DOMContentLoaded', async function() {
    initSocket();
    await initMap(); // 等待地图初始化完成
    initEventListeners();
    if (currentUser) {
        loadUserPlans();
    }
    
    // 添加诊断按钮（仅在开发环境）
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        addDiagnosticButton();
    }
});

// 添加诊断按钮
function addDiagnosticButton() {
    const diagnosticBtn = document.createElement('button');
    diagnosticBtn.textContent = '🔍 麦克风诊断';
    diagnosticBtn.style.cssText = 'position: fixed; bottom: 20px; right: 20px; padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; z-index: 10000; font-size: 14px;';
    diagnosticBtn.onclick = async function() {
        if (typeof diagnoseMicrophone === 'function') {
            const results = await diagnoseMicrophone();
            let message = '麦克风诊断结果:\n\n';
            
            if (results.browserSupport) message += '✅ 浏览器支持\n';
            else message += '❌ 浏览器不支持\n';
            
            if (results.secureContext) message += '✅ 安全上下文\n';
            else message += '❌ 不在安全上下文\n';
            
            if (results.devicesAvailable) message += '✅ 找到音频设备\n';
            else message += '❌ 未找到音频设备\n';
            
            if (results.streamAccessible) message += '✅ 可以访问麦克风\n';
            else message += '❌ 无法访问麦克风\n';
            
            if (results.errors.length > 0) {
                message += '\n错误信息:\n';
                results.errors.forEach(err => message += `- ${err}\n`);
            }
            
            alert(message);
            console.log('完整诊断结果:', results);
        } else {
            alert('诊断工具未加载。请刷新页面后重试。');
        }
    };
    document.body.appendChild(diagnosticBtn);
}

// 初始化Socket.IO
function initSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Socket connected');
    });
    
    socket.on('recognition_interim', (data) => {
        document.getElementById('recognitionResult').textContent = data.text;
    });
    
    socket.on('recording_result', (data) => {
        document.getElementById('recognitionResult').textContent = data.text;
        document.getElementById('travelInput').value = data.text;
        stopRecordingUI();
    });
    
    socket.on('error', (data) => {
        alert('错误: ' + data.message);
        stopRecordingUI();
    });
}

// 初始化地图
async function initMap() {
    return new Promise((resolve) => {
        // 先加载配置获取高德地图API Key
        fetch('/api/config')
            .then(res => res.json())
            .then(config => {
                if (config.amap_api_key) {
                    // 检查是否已加载高德地图API
                    if (window.AMap) {
                        createMap();
                        resolve();
                    } else {
                        // 动态加载高德地图API
                        const script = document.createElement('script');
                        script.src = `https://webapi.amap.com/maps?v=2.0&key=${config.amap_api_key}`;
                        script.onload = () => {
                            createMap();
                            resolve();
                        };
                        script.onerror = () => {
                            console.error('高德地图API加载失败，请检查API Key配置');
                            document.getElementById('mapContainer').innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">地图加载失败，请检查高德地图API Key配置</div>';
                            resolve();
                        };
                        document.head.appendChild(script);
                    }
                } else {
                    document.getElementById('mapContainer').innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">请先在设置中配置高德地图API Key</div>';
                    resolve();
                }
            })
            .catch(error => {
                console.error('加载配置失败:', error);
                document.getElementById('mapContainer').innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">无法加载地图配置</div>';
                resolve();
            });
    });
}

// 创建地图实例
function createMap() {
    if (window.AMap && !map) {
        try {
            map = new AMap.Map('mapContainer', {
                zoom: 10,
                center: [116.397428, 39.90923], // 北京
                viewMode: '3D'
            });
            console.log('地图初始化成功');
        } catch (error) {
            console.error('创建地图失败:', error);
            document.getElementById('mapContainer').innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">地图创建失败</div>';
        }
    }
}

// 初始化事件监听
function initEventListeners() {
    // 输入方式切换
    document.getElementById('textInputBtn').addEventListener('click', () => {
        switchInputMethod('text');
    });
    document.getElementById('voiceInputBtn').addEventListener('click', () => {
        switchInputMethod('voice');
    });
    
    // 生成计划
    document.getElementById('generatePlanBtn').addEventListener('click', generateTravelPlan);
    
    // 语音录制
    document.getElementById('recordBtn').addEventListener('click', startRecording);
    document.getElementById('stopRecordBtn').addEventListener('click', stopRecording);
    
    // 设置
    document.getElementById('settingsBtn').addEventListener('click', () => {
        openModal('settingsModal');
        loadSettings();
    });
    
    // 登录注册
    document.getElementById('loginBtn').addEventListener('click', () => openModal('loginModal'));
    document.getElementById('registerBtn').addEventListener('click', () => openModal('registerModal'));
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // 表单提交
    document.getElementById('settingsForm').addEventListener('submit', saveSettings);
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // 关闭计划详情
    document.getElementById('closePlanBtn').addEventListener('click', () => {
        document.getElementById('planDetails').style.display = 'none';
    });
}

// 切换输入方式
function switchInputMethod(method) {
    const textBtn = document.getElementById('textInputBtn');
    const voiceBtn = document.getElementById('voiceInputBtn');
    const textArea = document.getElementById('textInputArea');
    const voiceArea = document.getElementById('voiceInputArea');
    
    if (method === 'text') {
        textBtn.classList.add('active');
        voiceBtn.classList.remove('active');
        textArea.style.display = 'block';
        voiceArea.style.display = 'none';
    } else {
        textBtn.classList.remove('active');
        voiceBtn.classList.add('active');
        textArea.style.display = 'none';
        voiceArea.style.display = 'block';
    }
}

// 开始录音
async function startRecording() {
    try {
        // 检查浏览器是否支持 getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('您的浏览器不支持麦克风访问功能。请使用 Chrome、Firefox 或 Edge 等现代浏览器。');
        }
        
        // 检查是否在安全上下文中（HTTPS 或 localhost）
        const isSecureContext = window.isSecureContext || location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
        if (!isSecureContext) {
            throw new Error('麦克风访问需要安全连接（HTTPS）。请使用 https:// 访问，或在 localhost 上运行。');
        }
        
        // 首先尝试获取所有可用的音频设备
        let audioInputs = [];
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            audioInputs = devices.filter(device => device.kind === 'audioinput');
            console.log('可用的音频输入设备:', audioInputs.length);
            if (audioInputs.length === 0) {
                throw new Error('未找到音频输入设备。请检查麦克风是否已连接并启用。');
            }
        } catch (err) {
            console.warn('枚举设备失败，继续尝试:', err);
        }
        
        // 请求麦克风权限（先尝试简单配置）
        let stream;
        let lastError;
        
        // 尝试策略1: 使用完整配置
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
        } catch (err) {
            lastError = err;
            console.warn('完整配置失败，尝试简化配置:', err.name);
            
            // 尝试策略2: 使用基本配置
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true
                    } 
                });
            } catch (err2) {
                lastError = err2;
                console.warn('基本配置失败，尝试最简配置:', err2.name);
                
                // 尝试策略3: 使用最简配置
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: true
                    });
                } catch (err3) {
                    lastError = err3;
                    // 所有尝试都失败，提供详细错误信息
                    let errorMsg = '无法访问麦克风。\n\n';
                    
                    if (err3.name === 'NotAllowedError' || err3.name === 'PermissionDeniedError') {
                        errorMsg += '❌ 麦克风权限被拒绝\n\n';
                        errorMsg += '解决方法：\n';
                        errorMsg += '1. 点击地址栏左侧的锁图标或信息图标\n';
                        errorMsg += '2. 找到"麦克风"权限，设置为"允许"\n';
                        errorMsg += '3. 刷新页面后重试\n';
                        errorMsg += '4. 如果仍然不行，检查系统设置中的麦克风权限';
                    } else if (err3.name === 'NotFoundError' || err3.name === 'DevicesNotFoundError') {
                        errorMsg += '❌ 未找到麦克风设备\n\n';
                        errorMsg += '解决方法：\n';
                        errorMsg += '1. 检查麦克风是否已正确连接\n';
                        errorMsg += '2. 检查系统设置中的麦克风是否已启用\n';
                        errorMsg += '3. 尝试拔插麦克风设备\n';
                        errorMsg += '4. 重启浏览器';
                    } else if (err3.name === 'NotReadableError' || err3.name === 'TrackStartError') {
                        errorMsg += '❌ 无法读取麦克风\n\n';
                        errorMsg += '可能的原因：\n';
                        errorMsg += '1. 麦克风被其他应用占用（Zoom、Teams、Skype等）\n';
                        errorMsg += '2. 浏览器其他标签页正在使用麦克风\n';
                        errorMsg += '3. 系统权限问题\n';
                        errorMsg += '4. 麦克风驱动程序问题\n\n';
                        errorMsg += '解决方法：\n';
                        errorMsg += '1. 关闭所有其他使用麦克风的应用\n';
                        errorMsg += '2. 关闭浏览器中其他可能使用麦克风的标签页\n';
                        errorMsg += '3. 检查 Windows 设置 → 隐私 → 麦克风\n';
                        errorMsg += '4. 重启浏览器\n';
                        errorMsg += '5. 如果问题持续，尝试重启电脑';
                    } else if (err3.name === 'OverconstrainedError' || err3.name === 'ConstraintNotSatisfiedError') {
                        errorMsg += '❌ 麦克风不支持请求的配置\n\n';
                        errorMsg += '解决方法：\n';
                        errorMsg += '1. 尝试使用不同的麦克风设备\n';
                        errorMsg += '2. 更新麦克风驱动程序\n';
                        errorMsg += '3. 检查麦克风设置';
                    } else if (err3.name === 'SecurityError') {
                        errorMsg += '❌ 安全错误\n\n';
                        errorMsg += '解决方法：\n';
                        errorMsg += '1. 确保使用 http://localhost:8080 访问（不要使用 IP 地址）\n';
                        errorMsg += '2. 或者使用 https:// 协议\n';
                        errorMsg += '3. 检查浏览器安全设置';
                    } else {
                        errorMsg += `❌ 错误类型: ${err3.name}\n`;
                        errorMsg += `错误消息: ${err3.message}\n\n`;
                        errorMsg += '请检查：\n';
                        errorMsg += '1. 浏览器控制台是否有更多错误信息\n';
                        errorMsg += '2. 系统事件查看器中是否有相关错误\n';
                        errorMsg += '3. 麦克风设备是否正常工作';
                    }
                    
                    throw new Error(errorMsg);
                }
            }
        }
        
        // 检查流是否有效
        if (!stream || stream.getAudioTracks().length === 0) {
            throw new Error('无法获取有效的音频流。');
        }
        
        // 确定可用的 MIME 类型
        let mimeType = 'audio/webm';
        const supportedTypes = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/mp4'
        ];
        
        for (const type of supportedTypes) {
            if (MediaRecorder.isTypeSupported(type)) {
                mimeType = type;
                break;
            }
        }
        
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: mimeType
        });
        
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                audioChunks.push(event.data);
                // 将音频数据转换为PCM格式并发送
                convertAndSendAudio(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder 错误:', event.error);
            stopRecording();
            alert('录音过程中发生错误: ' + (event.error?.message || '未知错误'));
        };
        
        // 启动录音（每100ms收集一次数据）
        try {
            mediaRecorder.start(100);
            isRecording = true;
            
            // UI更新
            document.getElementById('recordBtn').classList.add('recording');
            document.getElementById('recordingStatus').style.display = 'flex';
            document.getElementById('recognitionResult').textContent = '';
            
            // 通知服务器开始录音
            socket.emit('start_recording');
            
            console.log('录音已开始，MIME类型:', mimeType);
        } catch (err) {
            stream.getTracks().forEach(track => track.stop());
            throw new Error('启动录音失败: ' + err.message);
        }
        
    } catch (error) {
        console.error('录音失败:', error);
        const errorMsg = error.message || '无法访问麦克风，请检查权限设置';
        alert(errorMsg);
        stopRecordingUI();
    }
}

// 停止录音
function stopRecording() {
    if (mediaRecorder && isRecording) {
        try {
            if (mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        } catch (err) {
            console.error('停止录音失败:', err);
        }
        isRecording = false;
        socket.emit('stop_recording');
        stopRecordingUI();
    }
}

// 停止录音UI
function stopRecordingUI() {
    document.getElementById('recordBtn').classList.remove('recording');
    document.getElementById('recordingStatus').style.display = 'none';
}

// 转换并发送音频数据
async function convertAndSendAudio(audioBlob) {
    try {
        // 使用AudioContext将音频转换为PCM格式
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000
        });
        
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        // 转换为单声道
        const channelData = audioBuffer.getChannelData(0);
        
        // 转换为16bit PCM
        const pcmData = new Int16Array(channelData.length);
        for (let i = 0; i < channelData.length; i++) {
            // 限制范围在-1到1之间，然后转换为16bit整数
            const s = Math.max(-1, Math.min(1, channelData[i]));
            pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        // 转换为Base64（分块处理避免内存问题）
        const pcmBytes = new Uint8Array(pcmData.buffer);
        let binaryString = '';
        const chunkSize = 8192;
        for (let i = 0; i < pcmBytes.length; i += chunkSize) {
            const chunk = pcmBytes.slice(i, i + chunkSize);
            binaryString += String.fromCharCode.apply(null, chunk);
        }
        const base64Audio = btoa(binaryString);
        
        // 发送PCM数据
        socket.emit('audio_data', base64Audio);
    } catch (error) {
        console.error('音频转换失败，使用原始格式:', error);
        // 如果转换失败，发送原始WebM数据（后端会尝试转换）
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64Audio = reader.result.split(',')[1];
            socket.emit('audio_data', base64Audio);
        };
        reader.readAsDataURL(audioBlob);
    }
}

// 生成旅行计划
async function generateTravelPlan() {
    const input = document.getElementById('travelInput').value.trim();
    if (!input) {
        alert('请输入旅行需求');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/travel/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input: input,
                user_id: currentUser?.id
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            displayTravelPlan(data.plan);
            if (currentUser) {
                loadUserPlans();
            }
        } else {
            alert('生成计划失败: ' + data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('生成计划错误:', error);
        alert('生成计划时发生错误');
    }
}

// 显示旅行计划
function displayTravelPlan(plan) {
    // 清除旧标记
    clearMarkers();
    
    // 显示计划详情
    const planDetails = document.getElementById('planDetails');
    const planTitle = document.getElementById('planTitle');
    const planContent = document.getElementById('planContent');
    
    planTitle.textContent = `${plan.destination || '未知目的地'} - ${plan.duration || ''}天`;
    planContent.innerHTML = '';
    
    // 生成行程内容
    if (plan.itinerary && plan.itinerary.length > 0) {
        plan.itinerary.forEach(day => {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'itinerary-day';
            
            dayDiv.innerHTML = `
                <div class="day-header">第${day.day}天 - ${day.date || ''}</div>
                ${day.activities ? day.activities.map(activity => `
                    <div class="activity-item">
                        <div class="activity-time">${activity.time || ''}</div>
                        <div class="activity-name">${activity.name || ''}</div>
                        <div class="activity-description">${activity.description || ''}</div>
                        ${activity.location ? `<div>📍 ${activity.location.name || ''}</div>` : ''}
                        ${activity.cost ? `<div class="activity-cost">💰 ¥${activity.cost}</div>` : ''}
                    </div>
                `).join('') : ''}
                ${day.total_cost ? `<div style="text-align: right; margin-top: 0.5rem; font-weight: bold;">当日总费用: ¥${day.total_cost}</div>` : ''}
            `;
            
            planContent.appendChild(dayDiv);
            
            // 在地图上标记位置
            if (day.activities) {
                day.activities.forEach(activity => {
                    if (activity.location && activity.location.lng && activity.location.lat) {
                        addMarker(
                            activity.location.lng,
                            activity.location.lat,
                            activity.name || '',
                            activity.description || ''
                        );
                    }
                });
            }
        });
    }
    
    // 显示预算信息
    if (plan.total_budget) {
        const budgetDiv = document.createElement('div');
        budgetDiv.style.padding = '1rem';
        budgetDiv.style.background = '#f0f0f0';
        budgetDiv.style.borderRadius = '8px';
        budgetDiv.style.marginTop = '1rem';
        budgetDiv.innerHTML = `<strong>总预算: ¥${plan.total_budget}</strong>`;
        planContent.appendChild(budgetDiv);
    }
    
    // 显示提示
    if (plan.tips && plan.tips.length > 0) {
        const tipsDiv = document.createElement('div');
        tipsDiv.style.marginTop = '1rem';
        tipsDiv.innerHTML = `
            <h4>旅行建议</h4>
            <ul style="padding-left: 1.5rem;">
                ${plan.tips.map(tip => `<li>${tip}</li>`).join('')}
            </ul>
        `;
        planContent.appendChild(tipsDiv);
    }
    
    planDetails.style.display = 'block';
    
    // 调整地图视野
    if (markers.length > 0) {
        map.setFitView(markers);
    }
}

// 添加地图标记
function addMarker(lng, lat, title, content) {
    const marker = new AMap.Marker({
        position: [lng, lat],
        title: title
    });
    
    const infoWindow = new AMap.InfoWindow({
        content: `<div style="padding: 0.5rem;"><strong>${title}</strong><br>${content}</div>`
    });
    
    marker.on('click', () => {
        infoWindow.open(map, marker.getPosition());
    });
    
    markers.push(marker);
    map.add(marker);
}

// 清除标记
function clearMarkers() {
    markers.forEach(marker => {
        map.remove(marker);
    });
    markers = [];
}

// 加载用户计划
async function loadUserPlans() {
    if (!currentUser) {
        return;
    }
    
    try {
        const response = await fetch(`/api/travel/plans?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            const plansList = document.getElementById('plansList');
            if (data.plans.length === 0) {
                plansList.innerHTML = '<p class="empty-message">暂无旅行计划</p>';
            } else {
                plansList.innerHTML = data.plans.map(plan => {
                    const planData = typeof plan.plan_data === 'string' ? JSON.parse(plan.plan_data) : plan.plan_data;
                    return `
                        <div class="plan-item" onclick="loadPlan(${plan.id})">
                            <div class="plan-item-title">${planData.destination || '未知目的地'}</div>
                            <div class="plan-item-meta">${plan.duration || ''}天 | ¥${plan.budget || 0}</div>
                        </div>
                    `;
                }).join('');
            }
        }
    } catch (error) {
        console.error('加载计划失败:', error);
    }
}

// 加载计划
async function loadPlan(planId) {
    try {
        const response = await fetch(`/api/travel/plan/${planId}`);
        const data = await response.json();
        
        if (data.success) {
            const planData = typeof data.plan.plan_data === 'string' ? JSON.parse(data.plan.plan_data) : data.plan.plan_data;
            displayTravelPlan(planData);
        }
    } catch (error) {
        console.error('加载计划失败:', error);
    }
}

// 模态框
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// 加载设置
async function loadSettings() {
    try {
        // 从本地存储加载已保存的配置（如果存在）
        const savedConfig = localStorage.getItem('api_config');
        if (savedConfig) {
            const config = JSON.parse(savedConfig);
            document.getElementById('iflytekAppId').value = config.iflytek_app_id || '';
            document.getElementById('iflytekApiKey').value = config.iflytek_api_key || '';
            document.getElementById('iflytekApiSecret').value = config.iflytek_api_secret || '';
            document.getElementById('amapApiKey').value = config.amap_api_key || '';
            document.getElementById('deepseekApiKey').value = config.deepseek_api_key || '';
            document.getElementById('supabaseUrl').value = config.supabase_url || '';
            document.getElementById('supabaseKey').value = config.supabase_key || '';
        }
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// 保存设置
async function saveSettings(e) {
    e.preventDefault();
    
    const config = {
        iflytek_app_id: document.getElementById('iflytekAppId').value,
        iflytek_api_key: document.getElementById('iflytekApiKey').value,
        iflytek_api_secret: document.getElementById('iflytekApiSecret').value,
        amap_api_key: document.getElementById('amapApiKey').value,
        deepseek_api_key: document.getElementById('deepseekApiKey').value,
        supabase_url: document.getElementById('supabaseUrl').value,
        supabase_key: document.getElementById('supabaseKey').value
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        if (data.success) {
            // 保存到本地存储（用于前端显示）
            localStorage.setItem('api_config', JSON.stringify(config));
            alert('配置保存成功！\n注意：某些配置可能需要重启应用才能生效。');
            closeModal('settingsModal');
            // 重新加载配置
            location.reload();
        } else {
            alert('保存失败: ' + data.message);
        }
    } catch (error) {
        console.error('保存设置错误:', error);
        alert('保存设置时发生错误');
    }
}

// 登录
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/user/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (data.success) {
            currentUser = data.user;
            updateUserUI();
            closeModal('loginModal');
            loadUserPlans();
        } else {
            alert('登录失败: ' + data.message);
        }
    } catch (error) {
        console.error('登录错误:', error);
        alert('登录时发生错误');
    }
}

// 注册
async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const name = document.getElementById('registerName').value;
    
    try {
        const response = await fetch('/api/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, name })
        });
        
        const data = await response.json();
        if (data.success) {
            alert('注册成功，请登录');
            closeModal('registerModal');
            openModal('loginModal');
        } else {
            alert('注册失败: ' + data.message);
        }
    } catch (error) {
        console.error('注册错误:', error);
        alert('注册时发生错误');
    }
}

// 退出登录
function logout() {
    currentUser = null;
    updateUserUI();
    document.getElementById('plansList').innerHTML = '<p class="empty-message">暂无旅行计划</p>';
}

// 更新用户UI
function updateUserUI() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const userInfo = document.getElementById('userInfo');
    const userEmail = document.getElementById('userEmail');
    
    if (currentUser) {
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        userInfo.style.display = 'flex';
        userEmail.textContent = currentUser.email;
    } else {
        loginBtn.style.display = 'block';
        registerBtn.style.display = 'block';
        userInfo.style.display = 'none';
    }
}

// 加载提示
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 全局函数（供HTML调用）
window.loadPlan = loadPlan;
window.closeModal = closeModal;

