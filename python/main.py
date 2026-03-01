# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
# SPDX-License-Identifier: MPL-2.0

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

# === 回调函数 ===
def on_action(sid, cmd):
    action_id = ACTION_MAP.get(cmd, 0)
    if action_id > 0:
        print(f"🎮 Action: {cmd} (id={action_id}, steps={current_steps}, period={current_period})", flush=True)
        Bridge.call("action", action_id)
        ui.send_message("status", {"msg": f"执行: {cmd}", "busy": True})
    else:
        print(f"⚠️ Unknown action: {cmd}", flush=True)

def on_steps(sid, value):
    global current_steps
    try:
        current_steps = max(1, min(20, int(value)))
        Bridge.call("steps", current_steps)
        print(f"⚙️ Steps: {current_steps}", flush=True)
    except:
        pass

def on_period(sid, value):
    global current_period
    try:
        current_period = max(200, min(5000, int(value)))
        Bridge.call("period", current_period)
        print(f"⚙️ Period: {current_period}ms", flush=True)
    except:
        pass

# === 注册事件 ===
ui.on_message('action', on_action)
ui.on_message('steps', on_steps)
ui.on_message('period', on_period)

print("🤖 Kame Robot Web Controller Ready", flush=True)
App.run()