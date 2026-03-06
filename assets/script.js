const socket = io();
const dot = document.getElementById('dot');
const stat = document.getElementById('stat');
const statusText = document.getElementById('status-text');

// === 连接状态 ===
socket.on('connect', () => { 
    dot.classList.add('online'); 
    stat.innerText = "ONLINE"; 
    stat.style.color = "#fff";
    statusText.innerText = "READY";
    statusText.className = "status-text ready";
});
socket.on('disconnect', () => { 
    dot.classList.remove('online'); 
    stat.innerText = "OFFLINE"; 
    stat.style.color = "#666";
    statusText.innerText = "DISCONNECTED";
    statusText.className = "status-text";
});

// === 状态反馈 ===
socket.on('status', (data) => {
    if (data.msg) {
        statusText.innerText = data.msg;
        statusText.className = data.busy ? "status-text busy" : "status-text ready";
    }
    // 忙碌时禁用所有动作按钮，就绪时恢复
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.disabled = !!data.busy;
        btn.style.opacity = data.busy ? '0.4' : '';
        btn.style.pointerEvents = data.busy ? 'none' : '';
    });
});

// === 发送动作指令 ===
function doAction(cmd) {
    if(event && event.cancelable) event.preventDefault();
    if(navigator.vibrate) navigator.vibrate(20);
    
    socket.emit('action', cmd);
    statusText.innerText = "⏳ " + cmd + "...";
    statusText.className = "status-text busy";
    
    // 给按钮添加按下动画
    if(event && event.target) {
        const btn = event.target.closest('.action-btn');
        if(btn) {
            btn.classList.add('pressed');
            setTimeout(() => btn.classList.remove('pressed'), 300);
        }
    }
}

// === 防抖工具 ===
function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// === 更新步数（防抖 300ms） ===
const _emitSteps = debounce((val) => socket.emit('steps', val), 300);
function updateSteps(val) {
    document.getElementById('steps-val').innerText = val;
    _emitSteps(val);
}

// === 更新周期（防抖 300ms） ===
const _emitPeriod = debounce((val) => socket.emit('period', val), 300);
function updatePeriod(val) {
    document.getElementById('period-val').innerText = val + "ms";
    _emitPeriod(val);
}

// === 禁止右键菜单 ===
document.oncontextmenu = (e) => e.preventDefault();