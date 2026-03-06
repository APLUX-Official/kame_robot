# Kame Robot — Web-Controlled Quadruped Robot

## 1. Overview

A MiniKame quadruped walking robot based on the Arduino UNO Q. The robot can be remotely controlled via a browser to perform a variety of preset actions such as walking, turning, and dancing, with real-time adjustment of step count and speed parameters.

**Core Highlights**:

- Pure browser control: Remote control via a web page on mobile/PC, no app installation required.
- 11 preset actions: Walking, left turn, right turn, dance, moonwalk, hello, push up, etc.
- Real-time parameter adjustment: Step count (1-20) and speed period (200-3000ms) adjustable in real time via sliders.
- Cyberpunk UI: Dark-style responsive interface, color-coded button categories, and vertical screen adaptation for mobile phones.
- Three-tier separation architecture: Web Frontend ↔ Python Middleware ↔ Arduino Firmware, with clear responsibilities for each tier.

## 2. File Structure

```
kame_robot/
├── sketch/
│   ├── sketch.ino       # Arduino Firmware (Bridge command scheduling)
│   ├── sketch.yaml      # Arduino dependency configuration
│   ├── minikame.cpp     # MiniKame motion library implementation (8-servo oscillator drive)
│   ├── minikame.h       # MiniKame class definition
│   ├── Octosnake.cpp    # Octosnake oscillator library implementation
│   └── Octosnake.h      # Octosnake oscillator class definition
├── python/
│   └── main.py          # Python Middleware (WebUI + Bridge command routing)
├── assets/
│   ├── index.html       # Control interface skeleton
│   ├── style.css        # Style sheet (Cyberpunk dark theme)
│   ├── script.js        # Interactive logic (Socket.IO communication)
│   └── socket.io.min.js # Local Socket.IO library (offline support)
├── app.yaml             # Arduino App configuration
└── README.md            # Project documentation
```

## 3. Hardware

### Hardware List

| Component       | Model                | Quantity | Description                                   |
| --------------- | -------------------- | -------- | --------------------------------------------- |
| Main Controller | Arduino UNO Q        | 1        | Based on STM32/Zephyr, built-in WiFi          |
| Servo           | SG90                 | 8        | 2 joints per leg (thigh + calf) for quadruped |
| Expansion Board | Customized           | 1        | Servo power supply and signal distribution    |
| Battery         | 7.4V Lithium Battery | 1        | Power supply for servos                       |

### Servo Pin Assignment

| Servo No. | Pin  | Position          |
| --------- | ---- | ----------------- |
| S0        | D4   | Front left thigh  |
| S1        | D5   | Front right thigh |
| S2        | D6   | Front left calf   |
| S3        | D7   | Front right calf  |
| S4        | D8   | Rear left thigh   |
| S5        | D9   | Rear right thigh  |
| S6        | D10  | Rear left calf    |
| S7        | D11  | Rear right calf   |

## 4. Software Architecture

```
┌──────────────────────────────────────────────┐
│             Web Frontend (Browser)           │
│  index.html + style.css + script.js          │
│  [Action Buttons] [Step Slider] [Speed Slider] [Status Panel] │
│              ↕ Socket.IO                     │
├──────────────────────────────────────────────┤
│            Python Middleware (Server)        │
│  main.py                                     │
│  [Action Name→ID Mapping] [Parameter Management] [Bridge Forwarding] │
│              ↕ RouterBridge                  │
├──────────────────────────────────────────────┤
│           Arduino Firmware (Low Level)       │
│  sketch.ino + minikame.cpp                   │
│  [Command Scheduling] [8-servo Oscillator Drive] [Trim Calibration] │
└──────────────────────────────────────────────┘
```

### 4.1 Frontend (Assets)

- Layout: Left parameter panel + middle action button area; automatically switches to a single-column layout for mobile vertical screens.
- Action buttons: Divided into three groups — Movement (Walk/Turn L/Turn R), Gesture (Dance/Moonwalk/Hello/Front Back/Push Up/Up Down), System (Init/Home).
- Parameter sliders: Step count (Amber, 1-20), Speed period (Cyan, 200-3000ms, smaller values mean faster speed).

### 4.2 Middleware (Python)

- Command mapping: Maps frontend action names (e.g., 'walk') to integer IDs (e.g., 1), and sends them to Arduino via `Bridge.call("action", id)`.
- Parameter forwarding: Step count and speed period changes are forwarded in real time, and the Arduino side uses `constrain()` for safety limits.

### 4.3 Low Level (Arduino)

- Command scheduling: Detects `pending_cmd` in `loop()`, and performs auto homing (`home()`) after executing the corresponding action.
- Motion library: The MiniKame library is based on the Octosnake oscillator, and 8 servos achieve smooth gaits through sine wave functions.
- Trim calibration: The `trim[]` array in `minikame.cpp` is used to compensate for servo zero-position deviation.

## 5. Actions

| Button       | Action Name | ID   | Description               |
| ------------ | ----------- | ---- | ------------------------- |
| 🚶 Walk       | walk        | 1    | Quadruped walking         |
| ↩️ Turn L     | turnL       | 3    | In-place left turn        |
| ↪️ Turn R     | turnR       | 4    | In-place right turn       |
| 💃 Dance      | dance       | 6    | Dance movement            |
| 🌙 Moonwalk   | moonwalk    | 5    | Moonwalk                  |
| 👋 Hello      | hello       | 9    | Greeting (leg waving)     |
| 🔄 Front Back | frontBack   | 11   | Forward and backward sway |
| 💪 Push Up    | pushUp      | 8    | Push up                   |
| ↕️ Up Down    | upDown      | 7    | Up and down heave         |
| 🔧 Init       | init        | 13   | Re-initialize servos      |
| 🏠 Home       | home        | 12   | Homing (standing posture) |

All actions (except Init/Home) will perform auto homing after execution.

## 6. User Guide

### Quick Start

1. Upload the code in the `sketch/` directory to the Arduino UNO Q.

2. Run it in the Arduino App Lab, or execute the following command via SSH:

   ```
   arduino-app-cli app start kame_robot
   ```

3. Access `http://<Robot IP>:7000` via a browser to enter the control console.

### Interface Operation

- Step Slider (Amber): Controls the repeat count of each action (1-20 steps).
- Speed Slider (Cyan): Controls the action period (200ms = fastest, 3000ms = slowest).
- Action Buttons: Execute immediately when clicked; the status panel displays "⏳ Action Name..." during execution.
- Init Button: Re-initializes all servos (for calibration or recovering from abnormal status).
- Home Button: Immediately returns to the default standing posture.

## 7. Trim Calibration

If the robot is skewed when standing, adjust the `trim[]` array in `minikame.cpp`:

```cpp
trim[0] = -5;   // Front left thigh (positive value = clockwise offset)
trim[1] = -5;   // Front right thigh
trim[2] = -20;  // Front left calf
trim[3] = 10;   // Front right calf
trim[4] = -3;   // Rear left thigh
trim[5] = -3;   // Rear right thigh
trim[6] = -15;  // Rear left calf
trim[7] = -13;  // Rear right calf
```

**Adjustment Method**: Send the Home command to make the robot stand → Observe which leg is skewed → Modify the corresponding trim value → Re-upload the firmware.

## 8. FAQ

**Q**: What to do if the servos jitter?
**A**: Check if the battery power is sufficient. SG90 servos will jitter at low voltage. It is recommended to use a 7.4V lithium battery for independent power supply.

**Q**: Abnormal robot posture after action execution?
**A**: Click the Home button to return to the standing posture. If the abnormality persists, click Init to re-initialize the servos.

**Q**: Abnormal interface arrangement on mobile vertical screens?
**A**: Ensure the latest `style.css` is referenced, which contains `@media` responsive queries.

**Q**: Is it usable without an internet connection?
**A**: Yes. The local `socket.io.min.js` file is included in `assets/`, enabling control within the local area network without an internet connection.

**Q**: How to modify the default values of action parameters?
**A**: Modify `cmd_steps` (default 5) and `cmd_period` (default 800ms) in `sketch.ino`, or modify `current_steps` and `current_period` in `main.py`.
