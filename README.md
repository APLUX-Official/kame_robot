<!--
 * @Author: WALT
 * @Date: 2026-02-25
-->
# 🤖 Kame Robot — Web 控制四足机器人

## 1. 项目概述 (Overview)
基于 **Arduino UNO Q** 的 MiniKame 四足步行机器人。通过浏览器即可远程控制机器人执行行走、转弯、跳舞等多种预设动作，支持实时调节步数与速度参数。

**核心亮点**：
* **纯浏览器控制**：手机/电脑打开网页即可遥控，无需安装 App。
* **11 种预设动作**：行走、左转、右转、舞蹈、太空步、打招呼、俯卧撑等。
* **实时参数调节**：步数（1-20）和速度周期（200-3000ms）通过滑块实时调节。
* **赛博朋克 UI**：暗色风格响应式界面，按钮分类色彩编码，手机竖屏自适应。
* **三层分离架构**：Web 前端 ↔ Python 中台 ↔ Arduino 固件，各层职责清晰。

---

## 2. 项目目录结构 (File Structure)

```text
kame_robot/
├── sketch/
│   ├── sketch.ino       # Arduino 固件 (Bridge命令调度)
│   ├── sketch.yaml      # Arduino 依赖配置
│   ├── minikame.cpp     # MiniKame 运动库实现 (8舵机振荡器驱动)
│   ├── minikame.h       # MiniKame 类定义
│   ├── Octosnake.cpp    # Octosnake 振荡器库实现
│   └── Octosnake.h      # Octosnake 振荡器类定义
├── python/
│   └── main.py          # Python 中台 (WebUI + Bridge 指令路由)
├── assets/
│   ├── index.html       # 控制界面骨架
│   ├── style.css        # 样式表 (赛博朋克暗色主题)
│   ├── script.js        # 交互逻辑 (Socket.IO 通信)
│   └── socket.io.min.js # 本地 Socket.IO 库 (离线支持)
├── app.yaml             # Arduino App 配置
└── README.md            # 项目文档
```

---

## 3. 硬件架构 (Hardware)

### 硬件清单

| 组件 | 型号 | 数量 | 说明 |
|------|------|------|------|
| 主控 | Arduino UNO Q | 1 | 基于 STM32/Zephyr，内置 WiFi |
| 舵机 | SG90 | 8 | 四足×2关节（大腿+小腿） |
| 拓展板 | 自定义 | 1 | 舵机供电与信号分配 |
| 电池 | 7.4V 锂电池 | 1 | 舵机供电 |

### 舵机引脚分配

| 舵机编号 | 引脚 | 位置 |
|----------|------|------|
| S0 | D4 | 前左大腿 |
| S1 | D5 | 前右大腿 |
| S2 | D6 | 前左小腿 |
| S3 | D7 | 前右小腿 |
| S4 | D8 | 后左大腿 |
| S5 | D9 | 后右大腿 |
| S6 | D10 | 后左小腿 |
| S7 | D11 | 后右小腿 |

---

## 4. 软件架构 (Software Architecture)

```text
┌──────────────────────────────────────────────┐
│             Web 前端（浏览器）                 │
│  index.html + style.css + script.js          │
│  [动作按钮] [步数滑块] [速度滑块] [状态面板]    │
│              ↕ Socket.IO                     │
├──────────────────────────────────────────────┤
│            Python 中台（服务器）               │
│  main.py                                     │
│  [动作名→ID映射] [参数管理] [Bridge转发]       │
│              ↕ RouterBridge                  │
├──────────────────────────────────────────────┤
│           Arduino 固件（底层）                 │
│  sketch.ino + minikame.cpp                   │
│  [命令调度] [8舵机振荡器驱动] [Trim校准]        │
└──────────────────────────────────────────────┘
```

### 4.1 前端 (Assets)
- **布局**：左侧参数面板 + 中间动作按钮区，手机竖屏自动切换为单列布局。
- **动作按钮**：分三组——移动（Walk/Turn L/Turn R）、动作（Dance/Moonwalk/Hello/Front Back/Push Up/Up Down）、系统（Init/Home）。
- **参数滑块**：步数（琥珀色，1-20）、速度周期（青色，200-3000ms，值越小越快）。

### 4.2 中台 (Python)
- **指令映射**：将前端动作名（如 `'walk'`）映射为整数 ID（如 `1`），通过 `Bridge.call("action", id)` 发送给 Arduino。
- **参数转发**：步数和速度周期变更实时转发，Arduino 端用 `constrain()` 做安全限位。

### 4.3 底层 (Arduino)
- **命令调度**：`loop()` 中检测 `pending_cmd`，执行对应动作后自动归位（`home()`）。
- **运动库**：MiniKame 库基于 Octosnake 振荡器，8 个舵机通过正弦波函数实现平滑步态。
- **Trim 校准**：`minikame.cpp` 中的 `trim[]` 数组用于补偿舵机零位偏差。

---

## 5. 动作列表 (Actions)

| 按钮 | 动作名 | ID | 说明 |
|------|--------|----|------|
| 🚶 Walk | `walk` | 1 | 四足行走 |
| ↩️ Turn L | `turnL` | 3 | 原地左转 |
| ↪️ Turn R | `turnR` | 4 | 原地右转 |
| 💃 Dance | `dance` | 6 | 舞蹈动作 |
| 🌙 Moonwalk | `moonwalk` | 5 | 太空步 |
| 👋 Hello | `hello` | 9 | 打招呼（挥腿） |
| 🔄 Front Back | `frontBack` | 11 | 前后摇摆 |
| 💪 Push Up | `pushUp` | 8 | 俯卧撑 |
| ↕️ Up Down | `upDown` | 7 | 上下起伏 |
| 🔧 Init | `init` | 13 | 重新初始化舵机 |
| 🏠 Home | `home` | 12 | 归位（站立姿态） |

> 所有动作（Init/Home 除外）执行完成后会自动归位。

---

## 6. 操作说明 (User Guide)

### 快速启动
1. 将 `sketch/` 目录下的代码上传至 Arduino UNO Q。
2. 在 Arduino App Lab 中运行，或通过 SSH 执行：
   ```bash
   arduino-app-cli app start kame_robot
   ```
3. 浏览器访问 `http://<机器人IP>:7000` 进入控制台。

### 界面操作
- **步数滑块 (Amber)**：控制每个动作的重复次数（1-20 步）。
- **速度滑块 (Cyan)**：控制动作周期（200ms=最快，3000ms=最慢）。
- **动作按钮**：点击即执行，执行期间状态面板显示"⏳ 动作名..."。
- **Init 按钮**：重新初始化所有舵机（用于校准或恢复异常状态）。
- **Home 按钮**：立刻归位到默认站立姿态。

---

## 7. 舵机校准 (Trim Calibration)

如果机器人站立时姿态歪斜，需要调整 `minikame.cpp` 中的 `trim[]` 数组：

```cpp
trim[0] = -5;   // 前左大腿 (正值=顺时针偏移)
trim[1] = -5;   // 前右大腿
trim[2] = -20;  // 前左小腿
trim[3] = 10;   // 前右小腿
trim[4] = -3;   // 后左大腿
trim[5] = -3;   // 后右大腿
trim[6] = -15;  // 后左小腿
trim[7] = -13;  // 后右小腿
```

调整方法：发送 Home 指令让机器人站立 → 观察哪条腿偏斜 → 修改对应 trim 值 → 重新上传固件。

---

## 8. 常见问题 (FAQ)

**Q: 舵机抖动怎么办？**  
A: 检查电池电量是否充足。SG90 在低电压下会抖动。建议使用 7.4V 锂电池独立供电。

**Q: 动作执行后机器人姿态异常？**  
A: 点击 Home 按钮归位。如果持续异常，点击 Init 重新初始化舵机。

**Q: 手机竖屏界面排列异常？**  
A: 确保引用了最新的 `style.css`，其中包含 `@media` 响应式查询。

**Q: 没有网络能用吗？**  
A: 可以。`assets/` 中已包含 `socket.io.min.js` 本地文件，局域网内即可控制，无需互联网。

**Q: 如何修改动作参数的默认值？**  
A: 修改 `sketch.ino` 中的 `cmd_steps`（默认 5）和 `cmd_period`（默认 800ms），或在 `main.py` 中修改 `current_steps` 和 `current_period`。

---

文档生成时间: 2026-02-25




