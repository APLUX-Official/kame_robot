# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
# SPDX-License-Identifier: MPL-2.0

import threading
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()

# === 动作映射表 ===
ACTION_MAP = {
    'walk':      1,
    'turnL':     3,
    'turnR':     4,
    'moonwalk':  5,
    'dance':     6,
    'upDown':    7,
    'pushUp':    8,
    'hello':     9,
    'frontBack': 11,
    'home':      12,
    'init':      13,
}

# === 默认参数 ===
current_steps = 5
current_period = 800

# === 忙碌状态管理 ===
_busy = False
_busy_lock = threading.Lock()

# === 回调函数 ===
def on_action(sid, cmd):
    global _busy
    action_id = ACTION_MAP.get(cmd, 0)
    if action_id == 0:
        print(f"⚠️ Unknown action: {cmd}", flush=True)
        return

    # 如果上一个动作还在执行，直接拒绝
    with _busy_lock:
        if _busy:
            print(f"⏳ Busy, skip: {cmd}", flush=True)
            ui.send_message("status", {"msg": "动作执行中，请等待…", "busy": True})
            return
        _busy = True

    steps = current_steps
    period = current_period
    print(f"🎮 Action: {cmd} (id={action_id}, steps={steps}, period={period})", flush=True)
    ui.send_message("status", {"msg": f"执行: {cmd}", "busy": True})

    # 在后台线程执行 Bridge.call，不阻塞 WebUI 回调
    def _run():
        global _busy
        try:
            # 执行动作前同步最新的 steps/period 到 Arduino
            Bridge.call("steps", steps)
            Bridge.call("period", period)
            max_wait = steps * period / 1000 + 10
            Bridge.call("action", action_id, timeout=max_wait)
        except Exception as e:
            print(f"❌ Action error: {e}", flush=True)
        finally:
            with _busy_lock:
                _busy = False
            ui.send_message("status", {"msg": "就绪", "busy": False})

    threading.Thread(target=_run, daemon=True).start()

def on_steps(sid, value):
    global current_steps
    try:
        current_steps = max(1, min(5, int(value)))
        print(f"⚙️ Steps: {current_steps}", flush=True)
    except Exception:
        pass

def on_period(sid, value):
    global current_period
    try:
        current_period = max(800, min(2000, int(value)))
        print(f"⚙️ Period: {current_period}ms", flush=True)
    except Exception:
        pass

# === 注册事件 ===
ui.on_message('action', on_action)
ui.on_message('steps', on_steps)
ui.on_message('period', on_period)

print("🤖 Kame Robot Web Controller Ready", flush=True)
App.run()