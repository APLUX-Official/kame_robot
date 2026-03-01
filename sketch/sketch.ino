/*
 * @Author: WALT
 * @Date: 2026-02-24 23:11:55
 */
#include "Arduino_RouterBridge.h"
#include <Servo.h>
#include "minikame.h"

MiniKame robot;

// === 命令队列 ===
volatile int pending_cmd = 0;   // 0=无命令
volatile int cmd_steps = 5;     // 默认步数
volatile int cmd_period = 800;  // 默认周期(ms)

void setup() {
    Serial.begin(9600);
    pinMode(LED_BUILTIN, OUTPUT);

    robot.init();
    delay(1000);
    robot.home();
    delay(1000);

    Bridge.begin();
    Bridge.provide("action",  set_action);
    Bridge.provide("steps",   set_steps);
    Bridge.provide("period",  set_period);

    Serial.println("🤖 Kame Robot Ready!");
}

void loop() {
    Bridge.update();

    if (pending_cmd != 0) {
        int cmd = pending_cmd;
        pending_cmd = 0;

        digitalWrite(LED_BUILTIN, LOW); // LED ON = 执行中

        switch (cmd) {
            case 1:  robot.walk(cmd_steps, cmd_period);      break;
            case 3:  robot.turnL(cmd_steps, cmd_period);     break;
            case 4:  robot.turnR(cmd_steps, cmd_period);     break;
            case 5:  robot.moonwalkL(cmd_steps, cmd_period); break;
            case 6:  robot.dance(cmd_steps, cmd_period);     break;
            case 7:  robot.upDown(cmd_steps, cmd_period);    break;
            case 8:  robot.pushUp(cmd_steps, cmd_period);    break;
            case 9:  robot.hello();                          break;
            case 11: robot.frontBack(cmd_steps, cmd_period); break;
            case 12: robot.home();                           break;
            case 13: robot.init();                           break;
        }

        // 动作完成后归位（home 和 init 内部已归位）
        if (cmd != 12 && cmd != 13) {
            robot.home();
        }

        digitalWrite(LED_BUILTIN, HIGH); // LED OFF = 空闲
    }

    delay(10);
}

// === Bridge 回调 ===
void set_action(int action) { pending_cmd = action; }
void set_steps(int steps)   { cmd_steps  = constrain(steps, 1, 20); }
void set_period(int period)  { cmd_period = constrain(period, 200, 5000); }