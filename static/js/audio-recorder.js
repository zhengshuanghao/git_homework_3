/**
 * 音频录制模块 - 用于语音识别
 * 录制音频并转换为 PCM 格式发送给服务器
 */

// 全局变量
let audioStream = null;
let audioContextRecorder = null;
let audioSource = null;
let audioProcessor = null;
let isRecording = false;

/**
 * 开始流式录音（直接生成 PCM）
 * @param {Socket} socket - Socket.IO 连接
 * @returns {Promise<MediaStream>}
 */
async function startStreamingRecording(socket) {
    try {
        // 获取麦克风流
        audioStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 16000,  // 语音识别要求 16kHz
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            } 
        });
        
        // 创建音频上下文
        audioContextRecorder = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000  // 直接使用 16kHz
        });
        
        // 创建音频源
        audioSource = audioContextRecorder.createMediaStreamSource(audioStream);
        
        // 使用 ScriptProcessorNode 获取原始音频数据
        // 缓冲区大小：4096 samples (约 256ms @ 16kHz)
        audioProcessor = audioContextRecorder.createScriptProcessor(4096, 1, 1);
        
        audioProcessor.onaudioprocess = (event) => {
            if (!isRecording) return;
            
            // 获取 Float32 音频数据
            const inputData = event.inputBuffer.getChannelData(0);
            
            // 转换为 Int16 PCM
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                // Float32 (-1.0 ~ 1.0) -> Int16 (-32768 ~ 32767)
                const s = Math.max(-1, Math.min(1, inputData[i]));
                pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            
            // 转换为 Base64
            const bytes = new Uint8Array(pcmData.buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            const base64Audio = btoa(binary);
            
            // 发送给服务器
            socket.emit('audio_data', base64Audio);
            // console.log('[录音] 发送PCM音频:', pcmData.length, 'samples');
        };
        
        // 连接音频节点
        audioSource.connect(audioProcessor);
        audioProcessor.connect(audioContextRecorder.destination);
        
        isRecording = true;
        console.log('[录音] 流式录音已启动 (PCM 16kHz)');
        return audioStream;
        
    } catch (error) {
        console.error('[录音] 启动失败:', error);
        throw error;
    }
}

/**
 * 停止录音
 */
function stopStreamingRecording() {
    isRecording = false;
    
    // 断开音频节点
    if (audioProcessor) {
        audioProcessor.disconnect();
        audioProcessor = null;
    }
    
    if (audioSource) {
        audioSource.disconnect();
        audioSource = null;
    }
    
    // 关闭音频上下文
    if (audioContextRecorder) {
        audioContextRecorder.close();
        audioContextRecorder = null;
    }
    
    // 停止麦克风流
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }
    
    console.log('[录音] 已停止');
}

// 导出函数
window.AudioRecorder = {
    startStreamingRecording,
    stopStreamingRecording,
    get isRecording() { return isRecording; }
};

