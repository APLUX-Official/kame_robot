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

// === 更新步数 ===
function updateSteps(val) {
    document.getElementById('steps-val').innerText = val;
    socket.emit('steps', val);
}

// === 更新周期 ===
function updatePeriod(val) {
    document.getElementById('period-val').innerText = val + "ms";
    socket.emit('period', val);
}

// === 禁止右键菜单 ===
document.oncontextmenu = (e) => e.preventDefault();