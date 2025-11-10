// 全局变量
let map = null;
let markers = [];
let currentUser = null;
let socket = null;
// isRecording 现在由 audio-recorder.js 管理

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
    
    // 语音识别结果（统一处理临时和最终结果）
    socket.on('recognition_result', (data) => {
        const resultElement = document.getElementById('recognitionResult');
        const inputElement = document.getElementById('travelInput');
        const voiceBtn = document.getElementById('generatePlanFromVoiceBtn');
        
        const text = data.text;
        const isFinal = data.is_final;
        
        console.log(`[语音识别] ${isFinal ? '最终' : '临时'}结果:`, text);
        
        if (text && text.trim()) {
            // 显示识别结果
            if (resultElement) {
                if (isFinal) {
                    resultElement.textContent = '识别结果：' + text;
                    resultElement.style.color = '#2ecc71'; // 绿色表示成功
                    
                    // 最终结果时显示"生成旅行计划"按钮
                    if (voiceBtn) {
                        voiceBtn.style.display = 'block';
                    }
                } else {
                    resultElement.textContent = '识别中：' + text;
                    resultElement.style.color = '#3498db'; // 蓝色表示识别中
                }
            }
            
            // 填充到文本输入框（临时和最终都填充）
            if (inputElement) {
                inputElement.value = text;
            }
        }
    });
    
    socket.on('error', (data) => {
        alert('错误: ' + data.message);
        stopRecordingUI();
    });

    socket.on('recognition_text', (data) => {
        console.log('[豆包文本]', data.text);
        const resultElement = document.getElementById('recognitionResult');
        if (resultElement) {
            resultElement.textContent += data.text;
            resultElement.style.color = '#2ecc71'; // 绿色
        }
        
        // 也更新到输入框
        const inputElement = document.getElementById('travelInput');
        if (inputElement) {
            inputElement.value += data.text;
        }
    });

    socket.on('audio_output', (data) => {
        console.log('[豆包音频] 收到音频:', data.audio.length, '字节');
        // 播放豆包返回的语音
        if (window.DoubaoAudio) {
            window.DoubaoAudio.playPCMAudio(data.audio, data.sample_rate);
        }
    });
    
    socket.on('recording_stopped', (data) => {
        console.log('[豆包] 对话已停止:', data.message);
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
    document.getElementById('generatePlanFromVoiceBtn').addEventListener('click', generateTravelPlan);
    
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
        // 清空之前的结果
        const resultElement = document.getElementById('recognitionResult');
        if (resultElement) {
            resultElement.textContent = '';
            resultElement.style.color = '#666';
        }
        const voiceBtn = document.getElementById('generatePlanFromVoiceBtn');
        if (voiceBtn) {
            voiceBtn.style.display = 'none';
        }
        
        // 检查录音模块
        if (!window.AudioRecorder) {
            throw new Error('录音模块未加载');
        }
        
        // 通知服务器开始录音
        socket.emit('start_recording');
        
        // 等待服务器确认
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error('服务器响应超时')), 5000);
            
            socket.once('recording_started', (data) => {
                clearTimeout(timeout);
                console.log('[语音识别] 服务器已启动:', data.message);
                resolve();
            });
            
            socket.once('error', (data) => {
                clearTimeout(timeout);
                reject(new Error(data.message));
            });
        });
        
        // 启动流式录音
        await window.AudioRecorder.startStreamingRecording(socket);
        
        // UI更新（isRecording 状态由 AudioRecorder 管理）
        document.getElementById('recordBtn').classList.add('recording');
        document.getElementById('recordingStatus').style.display = 'flex';
        
        console.log('[语音识别] 录音已启动');
        
    } catch (error) {
        console.error('[语音识别] 录音失败:', error);
        
        // 显示更友好的错误提示
        const errorMsg = error.message || '无法启动语音识别';
        if (errorMsg.includes('404') || errorMsg.includes('rejected')) {
            alert('语音识别服务暂时不可用。请使用文字输入模式，或稍后重试。\n\n提示：您可以切换到"文字输入"模式直接输入旅行需求。');
        } else {
            alert(errorMsg);
        }
        
        stopRecordingUI();
        
        // 自动切换到文字输入模式
        switchInputMethod('text');
    }
}

// 停止录音
function stopRecording() {
    if (window.AudioRecorder && window.AudioRecorder.isRecording) {
        try {
            // 停止流式录音
            window.AudioRecorder.stopStreamingRecording();
            
            // 通知服务器停止
            socket.emit('stop_recording');
            
            stopRecordingUI();
            
            console.log('[语音识别] 录音已停止');
            
            // 显示"生成旅行计划"按钮
            const voiceBtn = document.getElementById('generatePlanFromVoiceBtn');
            if (voiceBtn) {
                voiceBtn.style.display = 'block';
            }
            
        } catch (err) {
            console.error('[语音识别] 停止录音失败:', err);
        }
    }
}

// 停止录音UI
function stopRecordingUI() {
    document.getElementById('recordBtn').classList.remove('recording');
    document.getElementById('recordingStatus').style.display = 'none';
}

// 转换并发送音频数据（简化版：直接发送WebM让后端处理）
async function convertAndSendAudio(audioBlob) {
    try {
        // 直接发送 WebM 格式，让后端用 pydub/ffmpeg 转换
        // 这样更可靠，避免前端 AudioContext 兼容性问题
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64Audio = reader.result.split(',')[1];
            socket.emit('audio_data', base64Audio);
            console.log('✓ 发送音频数据:', audioBlob.size, '字节 (WebM格式)');
        };
        reader.onerror = (error) => {
            console.error('✗ 读取音频文件失败:', error);
        };
        reader.readAsDataURL(audioBlob);
    } catch (error) {
        console.error('✗ 音频发送失败:', error);
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

