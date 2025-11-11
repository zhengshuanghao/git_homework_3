// 模态框管理
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// 登录按钮
document.getElementById('loginBtn').addEventListener('click', () => {
    openModal('loginModal');
});

// 注册按钮
document.getElementById('registerBtn').addEventListener('click', () => {
    openModal('registerModal');
});

// 开始按钮
document.getElementById('getStartedBtn').addEventListener('click', () => {
    openModal('registerModal');
});

// CTA按钮
document.getElementById('ctaBtn').addEventListener('click', () => {
    openModal('registerModal');
});

// 切换到注册
document.getElementById('switchToRegister').addEventListener('click', (e) => {
    e.preventDefault();
    closeModal('loginModal');
    openModal('registerModal');
});

// 切换到登录
document.getElementById('switchToLogin').addEventListener('click', (e) => {
    e.preventDefault();
    closeModal('registerModal');
    openModal('loginModal');
});

// 点击模态框外部关闭
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// 登录表单提交
document.getElementById('loginForm').addEventListener('submit', async (e) => {
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
            // 保存用户信息到localStorage
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // 显示成功消息
            alert('登录成功！');
            
            // 跳转到主应用页面
            window.location.href = '/app';
        } else {
            alert('登录失败：' + data.message);
        }
    } catch (error) {
        console.error('登录错误:', error);
        alert('登录失败，请稍后重试');
    }
});

// 注册表单提交
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const name = document.getElementById('registerName').value;
    
    // 验证密码长度
    if (password.length < 6) {
        alert('密码至少需要6位字符');
        return;
    }
    
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
            // 保存用户信息到localStorage
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // 显示成功消息
            alert('注册成功！');
            
            // 跳转到主应用页面
            window.location.href = '/app';
        } else {
            alert('注册失败：' + data.message);
        }
    } catch (error) {
        console.error('注册错误:', error);
        alert('注册失败，请稍后重试');
    }
});

// 检查是否已登录
window.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('user');
    if (user) {
        // 如果已登录，直接跳转到主应用
        window.location.href = '/app';
    }
});
