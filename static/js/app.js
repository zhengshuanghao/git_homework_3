// 全局变量
let map = null;
let markers = [];
let currentUser = null;
let socket = null;
// 防止重复提交生成旅行计划
let isGeneratingPlan = false;
// isRecording 现在由 audio-recorder.js 管理

// 检查登录状态
function checkLoginStatus() {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        // 未登录，跳转到首页
        window.location.href = '/';
        return;
    }
    
    try {
        currentUser = JSON.parse(userStr);
        // 显示用户信息
        const userEmailEl = document.getElementById('userEmail');
        if (userEmailEl && currentUser.email) {
            userEmailEl.textContent = currentUser.email;
        }
    } catch (error) {
        console.error('解析用户信息失败:', error);
        localStorage.removeItem('user');
        window.location.href = '/';
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('user');
    currentUser = null;
    window.location.href = '/';
}

// 初始化
document.addEventListener('DOMContentLoaded', async function() {
    // 检查登录状态
    checkLoginStatus();
    
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
    
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // API设置、偏好设置和费用记录
    document.getElementById('settingsBtn').addEventListener('click', openSettingsModal);
    document.getElementById('preferencesBtn').addEventListener('click', openPreferencesModal);
    document.getElementById('expensesBtn').addEventListener('click', openExpensesModal);
    
    // 表单提交
    document.getElementById('settingsForm').addEventListener('submit', saveSettings);
    document.getElementById('preferencesForm').addEventListener('submit', savePreferences);
    document.getElementById('addExpenseForm').addEventListener('submit', addExpense);
    
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
    // 优先使用 voice 区域的日期/天数（如果存在），否则回退到文本区域的控件
    const departureDateVoiceEl = document.getElementById('departureDateVoice');
    const tripDaysVoiceEl = document.getElementById('tripDaysVoice');
    const departureDateTextEl = document.getElementById('departureDate');
    const tripDaysTextEl = document.getElementById('tripDays');

    let departureDate = '';
    let tripDays = null;

    if (departureDateVoiceEl && departureDateVoiceEl.value) {
        departureDate = departureDateVoiceEl.value;
    } else if (departureDateTextEl && departureDateTextEl.value) {
        departureDate = departureDateTextEl.value;
    }

    if (tripDaysVoiceEl && tripDaysVoiceEl.value) {
        tripDays = parseInt(tripDaysVoiceEl.value, 10);
    } else if (tripDaysTextEl && tripDaysTextEl.value) {
        tripDays = parseInt(tripDaysTextEl.value, 10);
    }
    if (!input) {
        alert('请输入旅行需求');
        return;
    }

    // 防止并发重复提交
    if (isGeneratingPlan) return;
    isGeneratingPlan = true;

    // 禁用生成按钮，显示按钮内 spinner，防止多次点击
    const genBtn = document.getElementById('generatePlanBtn');
    const genVoiceBtn = document.getElementById('generatePlanFromVoiceBtn');
    if (genBtn) {
        genBtn.disabled = true;
        const s = genBtn.querySelector('.btn-spinner');
        if (s) s.style.display = 'inline-block';
    }
    if (genVoiceBtn) {
        genVoiceBtn.disabled = true;
        const s2 = genVoiceBtn.querySelector('.btn-spinner');
        if (s2) s2.style.display = 'inline-block';
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
                user_id: currentUser?.id,
                departure_date: departureDate || null,
                trip_days: tripDays || null
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
    } finally {
        // 恢复按钮、spinner 和状态
        isGeneratingPlan = false;
        if (genBtn) {
            const s = genBtn.querySelector('.btn-spinner');
            if (s) s.style.display = 'none';
            genBtn.disabled = false;
        }
        if (genVoiceBtn) {
            const s2 = genVoiceBtn.querySelector('.btn-spinner');
            if (s2) s2.style.display = 'none';
            genVoiceBtn.disabled = false;
        }
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
    
    // Normalize destination and duration display (handle sentinel values from LLM)
    const dest = (plan.destination && plan.destination !== '未识别') ? plan.destination : '未知目的地';
    const durationRaw = plan.duration || '';
    const duration = (durationRaw && durationRaw !== '未指定') ? durationRaw : '';
    planTitle.textContent = duration ? `${dest} - ${duration}天` : `${dest}`;
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
    
    // 显示预算信息（如果为0或未指定则显示友好提示）
    const totalBudgetNum = Number(plan.total_budget || 0);
    const budgetDiv = document.createElement('div');
    budgetDiv.style.padding = '1rem';
    budgetDiv.style.background = '#f0f0f0';
    budgetDiv.style.borderRadius = '8px';
    budgetDiv.style.marginTop = '1rem';
    if (totalBudgetNum > 0) {
        budgetDiv.innerHTML = `<strong>总预算: ¥${totalBudgetNum}</strong>`;
    } else {
        budgetDiv.innerHTML = `<strong>总预算: 未指定</strong>`;
    }
    planContent.appendChild(budgetDiv);
    
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
                        <div class="plan-item">
                            <div class="plan-item-content" onclick="loadPlan(${plan.id})">
                                <div class="plan-item-title">${planData.destination || '未知目的地'}</div>
                                <div class="plan-item-meta">${plan.duration || ''}天 | ¥${plan.budget || 0}</div>
                            </div>
                            <button class="btn-delete-plan" onclick="event.stopPropagation(); deletePlan(${plan.id})" title="删除计划">🗑️</button>
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

// 已删除不需要的模态框和登录注册函数
// 这些功能现在在landing页面处理

// 加载提示
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// ==================== 模态框管理 ====================

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// ==================== 偏好设置功能 ====================

function openPreferencesModal() {
    const modal = document.getElementById('preferencesModal');
    modal.classList.add('active');
    loadUserPreferences();
}

function closePreferencesModal() {
    const modal = document.getElementById('preferencesModal');
    modal.classList.remove('active');
}

async function loadUserPreferences() {
    if (!currentUser || !currentUser.id) return;
    
    try {
        const response = await fetch(`/api/preferences?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (data.success && data.preferences) {
            const prefs = data.preferences;
            const form = document.getElementById('preferencesForm');
            
            // 填充复选框
            ['travel_style', 'accommodation_type', 'food_preference', 'transportation_preference', 'activity_preference'].forEach(field => {
                if (prefs[field] && Array.isArray(prefs[field])) {
                    prefs[field].forEach(value => {
                        const checkbox = form.querySelector(`input[name="${field}"][value="${value}"]`);
                        if (checkbox) checkbox.checked = true;
                    });
                }
            });
            
            // 填充单选框
            if (prefs.budget_level) {
                const radio = form.querySelector(`input[name="budget_level"][value="${prefs.budget_level}"]`);
                if (radio) radio.checked = true;
            }
            
            if (prefs.pace) {
                const radio = form.querySelector(`input[name="pace"][value="${prefs.pace}"]`);
                if (radio) radio.checked = true;
            }
            
            // 填充文本域
            if (prefs.special_requirements) {
                form.querySelector('textarea[name="special_requirements"]').value = prefs.special_requirements;
            }
        }
    } catch (error) {
        console.error('加载偏好设置失败:', error);
    }
}

async function savePreferences(e) {
    e.preventDefault();
    
    if (!currentUser || !currentUser.id) {
        alert('请先登录');
        return;
    }
    
    const form = e.target;
    const formData = new FormData(form);
    
    // 构建偏好数据
    const preferences = {
        travel_style: formData.getAll('travel_style'),
        accommodation_type: formData.getAll('accommodation_type'),
        food_preference: formData.getAll('food_preference'),
        transportation_preference: formData.getAll('transportation_preference'),
        activity_preference: formData.getAll('activity_preference'),
        budget_level: formData.get('budget_level') || '',
        pace: formData.get('pace') || '',
        special_requirements: formData.get('special_requirements') || ''
    };
    
    try {
        const response = await fetch('/api/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                preferences: preferences
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('偏好设置保存成功！');
            closePreferencesModal();
        } else {
            alert('保存失败：' + data.message);
        }
    } catch (error) {
        console.error('保存偏好设置失败:', error);
        alert('保存失败，请稍后重试');
    }
}

// ==================== 费用记录功能 ====================

async function openExpensesModal() {
    const modal = document.getElementById('expensesModal');
    modal.classList.add('active');
    await loadUserPlansForExpense(); // 加载旅行计划列表
    await loadExpenses();
    await loadExpenseSummary();
}

async function loadUserPlansForExpense() {
    if (!currentUser || !currentUser.id) return;
    
    try {
        const response = await fetch(`/api/travel/plans?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (data.success && data.plans) {
            const select = document.getElementById('expensePlanSelect');
            select.innerHTML = '<option value="">不关联具体计划</option>';
            
            data.plans.forEach(plan => {
                const option = document.createElement('option');
                option.value = plan.id;
                option.textContent = `${plan.destination || '未知目的地'} - ${plan.duration || ''}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载旅行计划列表失败:', error);
    }
}

function closeExpensesModal() {
    const modal = document.getElementById('expensesModal');
    modal.classList.remove('active');
}

async function loadExpenses() {
    if (!currentUser || !currentUser.id) return;
    
    try {
        const response = await fetch(`/api/expenses?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            displayExpenses(data.expenses);
        }
    } catch (error) {
        console.error('加载费用记录失败:', error);
    }
}

function displayExpenses(expenses) {
    const listEl = document.getElementById('expenseList');
    
    if (!expenses || expenses.length === 0) {
        listEl.innerHTML = '<p class="empty-message">暂无费用记录</p>';
        return;
    }
    
    listEl.innerHTML = expenses.map(exp => `
        <div class="expense-item">
            <div class="expense-info">
                <div class="expense-header">
                    <span class="expense-category">${exp.category || '其他'}</span>
                    <span class="expense-amount">¥${parseFloat(exp.amount).toFixed(2)}</span>
                </div>
                <div class="expense-description">${exp.description || '无描述'}</div>
                <div class="expense-date">${new Date(exp.date).toLocaleDateString('zh-CN')}</div>
            </div>
            <div class="expense-actions">
                <button class="btn-icon btn-delete" onclick="deleteExpense(${exp.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

async function loadExpenseSummary() {
    if (!currentUser || !currentUser.id) return;
    
    try {
        const response = await fetch(`/api/expenses/summary?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            const summary = data.summary;
            
            // 更新总计
            document.getElementById('totalExpense').textContent = `¥${summary.total.toFixed(2)}`;
            document.getElementById('expenseCount').textContent = summary.count;
            
            // 更新分类统计
            const categoryEl = document.getElementById('expenseByCategory');
            if (summary.by_category && Object.keys(summary.by_category).length > 0) {
                categoryEl.innerHTML = Object.entries(summary.by_category).map(([category, amount]) => `
                    <div class="category-item">
                        <div class="category-name">${category}</div>
                        <div class="category-amount">¥${amount.toFixed(2)}</div>
                    </div>
                `).join('');
            } else {
                categoryEl.innerHTML = '';
            }
        }
    } catch (error) {
        console.error('加载费用汇总失败:', error);
    }
}

async function addExpense(e) {
    e.preventDefault();
    
    if (!currentUser || !currentUser.id) {
        alert('请先登录');
        return;
    }
    
    const form = e.target;
    const formData = new FormData(form);
    
    const planId = formData.get('plan_id');
    
    const expense = {
        plan_id: planId ? parseInt(planId) : null,
        amount: parseFloat(formData.get('amount')),
        category: formData.get('category'),
        date: formData.get('date'),
        description: formData.get('description') || ''
    };
    
    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                expense: expense
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('费用记录添加成功！');
            form.reset();
            await loadExpenses();
            await loadExpenseSummary();
        } else {
            alert('添加失败：' + data.message);
        }
    } catch (error) {
        console.error('添加费用记录失败:', error);
        alert('添加失败，请稍后重试');
    }
}

async function deleteExpense(expenseId) {
    if (!confirm('确定要删除这条费用记录吗？')) return;
    
    if (!currentUser || !currentUser.id) {
        alert('请先登录');
        return;
    }
    
    try {
        const response = await fetch(`/api/expenses/${expenseId}?user_id=${currentUser.id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadExpenses();
            await loadExpenseSummary();
        } else {
            alert('删除失败：' + data.message);
        }
    } catch (error) {
        console.error('删除费用记录失败:', error);
        alert('删除失败，请稍后重试');
    }
}

// 删除旅行计划
async function deletePlan(planId) {
    if (!confirm('确定要删除这个旅行计划吗？相关的费用记录不会被删除。')) return;
    
    if (!currentUser || !currentUser.id) {
        alert('请先登录');
        return;
    }
    
    try {
        const response = await fetch(`/api/travel/plan/${planId}?user_id=${currentUser.id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('计划已删除');
            await loadUserPlans(); // 重新加载计划列表
        } else {
            alert('删除失败：' + data.message);
        }
    } catch (error) {
        console.error('删除计划失败:', error);
        alert('删除失败，请稍后重试');
    }
}

// ==================== API设置功能 ====================

async function openSettingsModal() {
    const modal = document.getElementById('settingsModal');
    modal.classList.add('active');
    await loadCurrentSettings();
}

function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    modal.classList.remove('active');
}

async function loadCurrentSettings() {
    try {
        const response = await fetch('/api/config/all');
        const data = await response.json();
        
        const form = document.getElementById('settingsForm');
        
        // 填充当前配置（只显示是否已配置，不显示实际值）
        if (data.speech_configured) {
            form.speech_app_id.placeholder = '已配置 ✓';
            form.speech_access_key.placeholder = '已配置 ✓';
            form.speech_secret_key.placeholder = '已配置 ✓';
            form.speech_model_id.placeholder = '已配置 ✓';
        }
        if (data.amap_configured) {
            form.amap_api_key.placeholder = '已配置 ✓';
            form.amap_api_secret.placeholder = '已配置 ✓';
        }
        if (data.deepseek_configured) {
            form.ark_api_key.placeholder = '已配置 ✓';
            form.deepseek_model.placeholder = '已配置 ✓';
        }
        if (data.supabase_configured) {
            form.supabase_url.placeholder = '已配置 ✓';
            form.supabase_key.placeholder = '已配置 ✓';
        }
        if (data.flask_configured) {
            form.flask_secret_key.placeholder = '已配置 ✓';
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

async function saveSettings(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // 构建配置对象（只包含非空值）
    const config = {};
    for (const [key, value] of formData.entries()) {
        if (value.trim()) {
            config[key] = value.trim();
        }
    }
    
    if (Object.keys(config).length === 0) {
        alert('请至少填写一项配置');
        return;
    }
    
    try {
        const response = await fetch('/api/config/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ 配置保存成功！\n\n' + (data.message || '配置已更新到 .env 文件'));
            closeSettingsModal();
            form.reset();
            
            // 重新加载配置状态
            await loadCurrentSettings();
        } else {
            alert('❌ 保存失败：' + (data.message || '未知错误'));
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('❌ 保存失败，请稍后重试');
    }
}

// 全局函数（供HTML调用）
window.loadPlan = loadPlan;
window.deletePlan = deletePlan;
window.closeModal = closeModal;
window.closeSettingsModal = closeSettingsModal;
window.closePreferencesModal = closePreferencesModal;
window.closeExpensesModal = closeExpensesModal;
window.deleteExpense = deleteExpense;

