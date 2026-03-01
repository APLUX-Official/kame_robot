# MiniKame四足机器人

### 一、项目简介

#### 1.1 设计理念

MiniKame是一款基于Arduino Uno的8自由度（8-DOF）微型四足机器人。它的设计灵感来源于经典的蜘蛛机器人形态，但体型更加紧凑可爱，适合在桌面进行演示和实验。本项目旨在提供一个**入门级但可扩展**的四足机器人开源方案，让爱好者和学生们能够亲手搭建一个能走、能跳、能做俯卧撑的迷你宠物。

与许多复杂的四足机器人项目不同，MiniKame的设计哲学是**简洁而不简单**。它不依赖于昂贵的传感器和复杂的控制算法，而是通过精巧的数学模型——正弦振荡器，来模拟生物的中枢模式发生器（CPG），实现自然流畅的运动。这种设计让初学者也能理解四足机器人的核心原理，同时为进阶开发者提供了足够的扩展空间。

**（图片拍摄）**

*图1：组装完成的MiniKame四足机器人*

#### 1.2 应用场景

- **机器人爱好者入门项目**：学习舵机控制、步态生成原理，体验从零到一的搭建过程
- **高校课程设计/毕业设计**：可作为机电一体化、嵌入式系统、自动控制等课程的实践项目
- **ROS/人工智能前端平台**：可在此基础上增加传感器（超声波/摄像头）实现避障、巡线或目标跟踪
- **创客教育/STEAM教学**：作为展示项目，激发学生对机器人技术的兴趣
- **桌面宠物/展示品**：完成后的MiniKame本身就是一件充满科技感的桌面摆件

#### 1.3 项目特色

- **纯数学驱动的运动控制**：不依赖复杂的传感器反馈，通过正弦振荡器生成自然步态
- **参数化设计**：所有动作都由振幅、周期、相位、偏移四个参数定义，便于理解和调整
- **丰富的动作库**：内置行走、转弯、俯卧撑、舞蹈、太空步等多种动作
- **可扩展架构**：清晰的代码结构，方便添加新动作或集成外部传感器
- **完整的校准机制**：通过trim和reverse参数补偿机械装配误差

### 二、结构设计

#### 2.1 腿部关节分析

MiniKame采用典型的四足机器人腿部结构，每条腿由两个关节组成，共8个自由度：

| 关节名称 | 舵机编号 | 功能描述             | 运动范围 | 控制目标  |
| -------- | -------- | -------------------- | -------- | --------- |
| 左前大腿 | 0        | 控制左前腿的前后摆动 | 0-180°   | 前进/后退 |
| 右前大腿 | 1        | 控制右前腿的前后摆动 | 0-180°   | 前进/后退 |
| 左前小腿 | 2        | 控制左前腿的上下抬起 | 0-180°   | 抬腿/落地 |
| 右前小腿 | 3        | 控制右前腿的上下抬起 | 0-180°   | 抬腿/落地 |
| 左后大腿 | 4        | 控制左后腿的前后摆动 | 0-180°   | 前进/后退 |
| 右后大腿 | 5        | 控制右后腿的前后摆动 | 0-180°   | 前进/后退 |
| 左后小腿 | 6        | 控制左后腿的上下抬起 | 0-180°   | 抬腿/落地 |
| 右后小腿 | 7        | 控制右后腿的上下抬起 | 0-180°   | 抬腿/落地 |

**关节配置的对称性分析**：

**（图片拍摄）**

*图2：单腿关节配置示意图*

每条腿的关节配置遵循以下原则：

1. **大腿（髋关节）**：负责腿的前后摆动，产生前进/后退的动力
2. **小腿（膝关节）**：负责腿的上下抬起，控制脚离地的高度

这种设计模拟了哺乳动物的腿部结构，虽然简化了（真正的生物腿部有更多关节），但对于桌面级机器人已经足够产生丰富的运动。

**坐标系的统一**：
在代码中，我们统一规定：

- 大腿角度增加 → 腿向前摆动
- 小腿角度增加 → 腿向下放（身体降低）

但实际安装时，舵机可能安装方向不同，这时就需要通过`reverse[]`数组进行方向反转。

#### 2.2 整体运动分析

MiniKame的运动可以分解为三个层次：

**第一层：单腿运动**

- 大腿的正弦摆动产生前进动力
- 小腿的正弦抬起确保脚离地
- 大腿和小腿的相位关系决定了单腿的运动轨迹

**第二层：对角腿协同**

- 左前-右后为一组（对角线）
- 右前-左后为另一组（对角线）
- 两组交替运动，形成稳定的**对角小跑步态**

**第三层：整体平衡**

- 通过偏移量调整初始姿态
- 通过振幅调整步长
- 通过周期调整运动速度
- 通过相位调整协调关系

**运动学的数学描述**：

对于任意一条腿，脚端的运动轨迹可以表示为：

```
x(t) = A_x * sin(ωt + φ_x) + O_x  (前后位置)
z(t) = A_z * sin(ωt + φ_z) + O_z  (上下位置)
```

其中：

- `x(t)`：脚的前后位置
- `z(t)`：脚的高度
- `A_x`：前后摆动振幅
- `A_z`：上下抬起振幅
- `ω = 2π/T`：角频率
- `φ_x`：前后运动相位
- `φ_z`：上下运动相位
- `O_x`：前后偏移
- `O_z`：上下偏移

当`φ_z - φ_x = 90°`时，脚的运动轨迹是一个椭圆，这正是行走所需的"抬腿-前摆-落腿-后蹬"循环。

#### 2.3 整体装配图解

**装配步骤概览**：

<video src=".\博客素材\解除爆炸视图.avi"></video>

*图3：MiniKame装配爆炸图*

**第一步：舵机初始化**

在安装前，需要将所有舵机设置为90度（中立位置）：

```
// 舵机归零测试程序
#include <Servo.h>

Servo testServo;

void setup() {
    testServo.attach(9);  // 假设舵机接在D9
    testServo.write(90);  // 设置到90度
}

void loop() {
    // 保持不动
}
```

**为什么要先归零再安装？**
如果舵机没有归零就安装机械结构，可能导致安装完成后腿的位置不对称，甚至损坏舵机齿轮。

**第二步：身体框架组装**

**（图片拍摄）**

*图4：身体框架组装完成*

身体框架由上下两块3D打印板通过铜柱连接，中间放置Arduino开发板和电池。舵机安装在身体两侧，通过U型支架连接腿部件。

**第三步：腿部组装**

**（图片拍摄）**

*图5：腿部组装示意图*

每条腿由两个舵机（大腿和小腿）和两个3D打印的连杆组成。装配时需注意：

- 舵机安装方向需与代码中的`reverse[]`设置对应
- 连杆长度直接影响运动范围，需使用标准打印件
- 所有螺丝需拧紧但不要过紧，避免塑料件滑丝

**（图片拍摄）**

*图6：MiniKame完整装配图*

装配完成后的MiniKame尺寸约为：长150mm × 宽120mm × 高100mm，重量约300g（含电池）。

### 三、电控设计

#### 3.1 电源设计与实现分析

MiniKame的电源系统需要同时满足两个需求：

1. **舵机供电**：8个舵机同时工作时电流可达2-3A，需要稳定的5V电源
2. **主控供电**：Arduino需要5V或7-12V输入

**电源方案对比**：

| 方案               | 优点           | 缺点                 | 适用场景   |
| ------------------ | -------------- | -------------------- | ---------- |
| 2节18650锂电池串联 | 容量大，续航久 | 需降压至5V，体积大   | 长时间演示 |
| 4节AA镍氢电池      | 易于获取       | 电压下降快，电流不足 | 短期测试   |
| 航模2S锂电池       | 放电能力强     | 需降压稳压           | 高性能需求 |
| USB移动电源        | 方便，安全     | 5V可能不够稳定       | 室内演示   |

**推荐的电源方案**：

采用12V锂电池，通过降压模块（如MP2225）降压至5V供给舵机，同时直接供给Arduino的Vin引脚。

**关键考虑因素**：

1. **电流能力**：舵机启动瞬间电流很大，电源需能提供峰值3A以上
2. **稳压精度**：电压波动不应超过±0.3V，否则舵机可能工作异常
3. **滤波电容**：在舵机电源输入端并联一个大容量电容（1000μF以上），吸收瞬态电流

**代码中的电源管理**：

```
// 在初始化时延迟连接舵机，避免同时启动造成电流冲击
void MiniKame::init() {
    for (int i = 0; i < 8; i++) {
        oscillator[i].start();
        servo[i].attach(board_pins[i]);
        delay(50);  // 每个舵机间隔50ms连接
    }
    zero();
}
```

#### 3.2 电机驱动电路设计与实现分析

MiniKame使用标准舵机，不需要额外的电机驱动芯片，但需要了解舵机的控制原理：

**舵机控制原理**：

舵机内部包含直流电机、减速齿轮、位置反馈电位器和控制电路。控制信号是周期20ms的PWM波，脉宽1ms对应0°，1.5ms对应90°，2ms对应180°。

**脉宽与角度的转换**：

```
// 角度到脉宽的转换函数
int MiniKame::angToUsec(float value) {
    // MIN_PULSE_WIDTH = 544μs (0°)
    // MAX_PULSE_WIDTH = 2400μs (180°)
    return value / 180 * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH) + MIN_PULSE_WIDTH;
}
```

**为什么使用`writeMicroseconds()`而不是`write()`？**

- `write(angle)`：库内部将角度转换为脉宽，但不同舵机可能有差异
- `writeMicroseconds(us)`：直接控制脉宽，精度更高，可适配不同舵机

### 四、从生物灵感到机器人实现

在自然界中，四足动物的行走是一种看似简单实则极其复杂的运动。当我们观察一只猫悠闲地漫步，或者一只狗轻快地小跑时，它们四条腿的协调运动显得如此自然流畅。这种运动的背后，是生物脊髓中一种称为**中枢模式发生器（Central Pattern Generator, CPG）**的神经回路在起作用。CPG能够产生节律性的信号，控制肌肉的收缩和舒张，即使在没有大脑有意识干预的情况下，也能维持基本的行走运动。

MiniKame四足机器人的设计理念，正是受到了这种生物机制的启发。我们不需要为每一个细微的动作编写复杂的指令序列，而是通过数学模型模拟CPG的工作原理，让机器人能够自主产生节律性的运动。这种自上而下的设计思路，使得代码简洁而优雅，同时也为后续的扩展和优化留下了充足的空间。

### 五、正弦振荡器——数字世界的CPG

#### 5.1 什么是正弦振荡器？

在数学和物理学中，振荡器是指能够产生周期性信号的系统。单摆的摆动、弹簧的振动、交流电的变化，这些都是自然界中常见的振荡现象。而在MiniKame的代码中，我们使用正弦函数来模拟这种振荡。

让我们深入剖析`Octosnake.cpp`中的`Oscillator`类，这是整个机器人运动的数学基础。

#### 5.2 Oscillator类的成员变量解析

首先看`Octosnake.h`中定义的私有成员变量：

```cpp
private:
    int _period;          // 周期：完成一次完整振荡所需的时间（毫秒）
    int _amplitude;       // 振幅：摆动幅度的大小（角度）
    int _phase;           // 相位：在周期中的起始位置（度）
    int _offset;          // 偏移：运动中心点相对于0度的位置（角度）
    float _output;        // 输出：当前计算得到的舵机目标角度
    bool _stop;           // 停止标志：true表示振荡器暂停输出
    unsigned long _ref_time; // 参考时间：振荡器启动的时刻（毫秒）
    float _delta_time;    // 时间差：当前时间相对于参考时间的偏移（毫秒）
```

这些变量共同定义了一个完整的正弦振荡器。每一个变量都有其特定的物理意义和数学作用。

#### 5.3 构造函数：振荡器的初始化

```cpp
Oscillator::Oscillator(){
    _period = 2000;       // 默认周期2000毫秒（2秒完成一次完整摆动）
    _amplitude = 50;      // 默认振幅50度（摆动范围±50度）
    _phase = 0;           // 默认相位0度（从正弦波的零点开始）
    _offset = 0;          // 默认偏移0度（围绕0度摆动）
    _stop = true;         // 初始状态为停止
    _ref_time = millis(); // 记录当前时间作为参考点
    _delta_time = 0;      // 初始时间差为0
}
```

构造函数设置了振荡器的默认参数。值得注意的是，虽然设置了默认值，但在实际使用中，这些参数会被具体的步态函数覆盖。`_stop`初始为`true`意味着振荡器创建后不会自动开始运行，需要调用`start()`方法激活。

#### 5.4 refresh()：核心计算函数

```cpp
float Oscillator::refresh(){
    if (!_stop){
        // 计算当前时间距离参考时间的差值，并对周期取模
        // 这样保证了_delta_time始终在0到_period-1之间
        _delta_time = (millis() - _ref_time) % _period;
        
        // 正弦波计算公式：
        // output = amplitude * sin(2π * time/period + phase) + offset
        _output =   (float)_amplitude * 
                    sin(time_to_radians(_delta_time) + 
                        degrees_to_radians(_phase)) + 
                    _offset;
    }
    return _output;
}
```

**逐行详细解释**：

1. **`if (!_stop)`**：只有当振荡器处于启动状态时，才进行角度计算。这样可以避免不必要的计算开销。

2. **`(millis() - _ref_time) % _period`**：
   - `millis()`返回从程序启动到现在的毫秒数
   - 减去`_ref_time`得到从振荡器启动到现在经过的时间
   - 对`_period`取模，确保时间值始终在一个周期范围内
   - 这个操作的数学意义是：无论运行多久，我们只关心当前时刻在一个周期内的位置

3. **`time_to_radians(_delta_time)`**：将时间值转换为弧度
   - 公式：`弧度 = 时间/周期 × 2π`
   - 这相当于计算正弦函数的自变量中的`ωt`部分

4. **`degrees_to_radians(_phase)`**：将相位从度转换为弧度
   - 相位决定了波形在时间轴上的偏移
   - 例如，相位90度会使正弦波提前四分之一个周期

5. **正弦波计算**：
   - `sin(...)`计算正弦值，范围在[-1, 1]之间
   - 乘以`_amplitude`将范围扩展到[-amplitude, amplitude]
   - 加上`_offset`将整个波形上下平移

6. **返回值**：计算得到的角度值，将直接用于控制舵机

#### 5.5 辅助函数：单位转换

```cpp
float Oscillator::time_to_radians(double time){
    // 将时间转换为弧度：2π * (time/period)
    return time * 2 * PI / _period;
}

float Oscillator::degrees_to_radians(float degrees){
    // 角度转弧度的标准公式：2π * (degrees/360)
    return degrees * 2 * PI / 360;
}

float Oscillator::degrees_to_time(float degrees){
    // 将角度转换为时间偏移：period * (degrees/360)
    return degrees * _period / 360;
}
```

这三个函数实现了时间、角度、弧度之间的相互转换，是正弦波计算的基础工具。理解它们有助于掌握正弦振荡器的数学本质。

#### 5.6 参数设置函数

```cpp
void Oscillator::setPeriod(int period){
    _period = period;     // 设置周期，单位毫秒
}

void Oscillator::setAmplitude(int amplitude){
    _amplitude = amplitude; // 设置振幅，单位度
}

void Oscillator::setPhase(int phase){
    _phase = phase;       // 设置相位，单位度
}

void Oscillator::setOffset(int offset){
    _offset = offset;     // 设置偏移，单位度
}
```

这些setter函数看似简单，但它们是连接高层步态逻辑和底层振荡计算的桥梁。在后面的步态函数中，我们会看到如何为每个舵机设置不同的参数组合。

#### 5.7 时间管理函数

```cpp
void Oscillator::reset(){
    _ref_time = millis();  // 将参考时间重置为当前时间
}

void Oscillator::start(){
    reset();               // 重置时间基准
    _stop = false;         // 启动振荡器
}

void Oscillator::start(unsigned long ref_time){
    _ref_time = ref_time;  // 使用外部传入的时间作为基准
    _stop = false;
}

void Oscillator::stop(){
    _stop = true;          // 停止振荡器
}

void Oscillator::setTime(unsigned long ref){
    _ref_time = ref;       // 设置参考时间（不改变停止状态）
}
```

**这些时间管理函数的设计思想**：

- `reset()`让振荡器"忘记"过去，从现在重新开始
- `start()`的两个重载版本提供了灵活性：要么自动获取当前时间，要么使用外部传入的统一时间
- `setTime()`用于实现多个振荡器的同步，这是步态协调的关键

#### 5.8 状态查询函数

```cpp
float Oscillator::getOutput(){
    return _output;        // 返回最近一次计算的结果
}

unsigned long Oscillator::getTime(){
    return _ref_time;      // 返回参考时间
}

float Oscillator::getPhaseProgress(){
    // 计算当前在周期中的进度（0-360度）
    return ((float)_delta_time / _period) * 360;
}
```

`getPhaseProgress()`是一个特别有用的函数，它返回当前时刻在一个周期内的位置（以度为单位）。这个值在`omniWalk()`中被用于实现平滑的步态过渡。

### 六、正弦波的四个参数——运动的四大要素

通过上面的代码分析，我们已经了解了振荡器的四个核心参数。现在让我们深入探讨每个参数的物理意义和数学本质。

#### 6.1 振幅（Amplitude）—— 决定动作的幅度

**数学定义**：振幅是正弦波的最大偏离值，决定了波形在垂直方向上的伸缩程度。

**物理意义**：在机器人运动中，振幅决定了舵机摆动的最大角度。振幅越大，腿摆动的幅度越大，步长越长，抬腿越高。

**代码体现**：

```cpp
int x_amp = 15;  // 前后摆动振幅15度
int z_amp = 20;  // 上下抬腿振幅20度
```

**为什么行走时小腿振幅大于大腿振幅**？因为抬腿动作需要克服重力，为了确保脚能完全离地，需要较大的角度；而前后摆动主要克服摩擦力，所需角度相对较小。

#### 6.2 周期（Period）—— 决定动作的快慢

**数学定义**：周期是完成一次完整振荡所需的时间，决定了波形在时间轴上的压缩或拉伸。

**物理意义**：周期决定了机器人运动的节奏。周期越短，运动越快；周期越长，运动越慢。

**代码体现**：

```cpp
int period[] = {T, T, T / 2, T / 2, T, T, T / 2, T / 2};
```

**特别值得注意的是**：在`walk()`函数中，大腿的周期是T，小腿的周期是T/2。这意味着小腿的运动速度是大腿的两倍。这种设计模拟了生物行走的特点——抬腿动作需要快速完成，而前后摆动可以相对缓慢。

#### 6.3 相位（Phase）—— 决定动作的协同

**数学定义**：相位表示正弦波在时间轴上的偏移量，决定了波形起始点的位置。

**物理意义**：相位是步态生成中最关键、也最富有数学美的参数。相位描述的是多个振荡器之间的时间偏移关系。打个比方，如果我们把四个腿比作四个舞者，相位就是决定他们何时起跳、何时落地的编舞指令。

**代码体现**：

```cpp
int phase[] = {90, 90, 270, 90, 270, 270, 90, 270};
```

**相位的数学关系**：当两个频率相同的正弦波相位差为0°时，它们完全同步；相位差90°时，一个达到峰值时另一个正在过零点；相位差180°时，它们完全相反。

#### 6.4 偏移（Offset）—— 决定动作的中立位置

**数学定义**：偏移是整个波形在垂直方向上的平移量，决定了正弦波的中心线位置。

**物理意义**：偏移决定了舵机在静止时的位置。在`home()`函数中，我们看到不同的腿有不同的偏移量，这是因为机器人的身体需要保持水平，而腿的安装角度天然存在差异。

**代码体现**：

```cpp
int offset[] = {
    90 + ap - front_x,  // 左前大腿：前伸更多
    90 - ap + front_x,  // 右前大腿：前伸更多
    90 - hi,            // 左前小腿
    90 + hi,            // 右前小腿
    // ...
};
```

**偏移的设计考量**：偏移量通常围绕90度（舵机的中立位置）进行微调，通过加减不同的值来实现特定的姿态。

### 七、MiniKame类的整体架构

#### 7.1 类的成员变量

```cpp
class MiniKame{
private:
    Oscillator oscillator[8];  // 8个振荡器，对应8个舵机
    Servo servo[8];            // 8个舵机对象
    int board_pins[8];         // 舵机对应的引脚号
    int trim[8];               // 校准值，补偿机械误差
    bool reverse[8];           // 方向反转标志
    unsigned long _init_time;  // 初始化时间
    unsigned long _final_time; // 结束时间
    unsigned long _partial_time; // 中间时间点
    float _increment[8];       // 增量数组，用于平滑移动
    float _servo_position[8];  // 当前舵机位置
    // ...
};
```

**每个成员变量的作用**：

- `oscillator[8]`：这是运动生成的核心，每个振荡器独立计算一个舵机的目标角度
- `servo[8]`：Arduino的Servo对象，负责生成实际的PWM信号
- `board_pins[8]`：定义每个舵机连接在哪个引脚上，与物理接线对应
- `trim[8]`：存储每个舵机的校准值，解决机械装配误差
- `reverse[8]`：解决舵机安装方向不一致的问题
- 各种时间变量：用于控制运动的时间和节奏
- `_increment[8]`：用于实现平滑插值
- `_servo_position[8]`：记录每个舵机的当前位置，用于增量计算

#### 7.2 init()：初始化函数深度解析

```cpp
void MiniKame::init() {
    // 1. 引脚映射配置
    board_pins[0] = D4; // 左前大腿
    board_pins[1] = D5; // 右前大腿
    board_pins[2] = D6; // 左前小腿
    board_pins[3] = D7; // 右前小腿
    board_pins[4] = D8; // 左后大腿
    board_pins[5] = D9; // 右后大腿
    board_pins[6] = D10; // 左后小腿
    board_pins[7] = D11; // 右后小腿
```

**引脚映射的设计原则**：

- 按照腿的物理位置分组：前腿使用D4-D7，后腿使用D8-D11
- 按照功能分组：偶数索引（0,2,4,6）为左侧腿，奇数索引（1,3,5,7）为右侧腿
- 这种映射使得在代码中可以通过索引的奇偶性快速判断是哪一侧的腿

```cpp
    // 2. 校准值配置（最终生效的值）
    trim[0] = -3;   // 左前大腿需要微调-3度
    trim[1] = 0;    // 右前大腿刚好合适
    trim[2] = 10;   // 左前小腿需要增加10度
    trim[3] = 5;    // 右前小腿需要增加5度
    trim[4] = -1;   // 左后大腿需要微调-1度
    trim[5] = 0;    // 右后大腿刚好合适
    trim[6] = 10;   // 左后小腿需要增加10度
    trim[7] = -5;   // 右后小腿需要微调-5度
```

**校准值的获取方法**：
这些值不是凭空得来的，而是通过反复调试得到的。调试过程通常是：

1. 将所有舵机设置为90度
2. 观察机器人是否站平
3. 如果某条腿悬空，说明该腿偏短，需要增加小腿的trim值
4. 如果某条腿过度受压，说明该腿偏长，需要减小trim值
5. 反复调整直到四条腿均匀受力

```cpp
    // 3. 方向设置
    for (int i = 0; i < 8; i++) reverse[i] = false;
    // 这里全部设为false，但在实际使用中可能需要根据安装方向调整
```

**方向设置的重要性**：
舵机的安装方向会影响角度增加对应的运动方向。如果舵机装反了，90度可能对应腿向后而不是向前。通过`reverse`标志，我们可以统一坐标系：无论舵机如何安装，我们都让"增加角度"对应"向前/向上"的运动。

```cpp
    // 4. 振荡器和舵机初始化
    for (int i = 0; i < 8; i++) {
        oscillator[i].start();        // 启动振荡器
        servo[i].attach(board_pins[i]); // 将舵机对象绑定到引脚
    }
    
    // 5. 将所有舵机归零
    zero();
}
```

**初始化顺序的逻辑**：
先启动振荡器，再绑定舵机，最后归零。这个顺序确保了在设置舵机位置时，振荡器已经准备好提供计算值。

### 八、舵机控制与校准机制

#### 8.1 setServo()：舵机控制的最终执行

```cpp
void MiniKame::setServo(int id, float target) {
    if (!reverse[id])
        // 正常方向：直接使用target + trim
        servo[id].writeMicroseconds(angToUsec(target + trim[id]));
    else
        // 反向：使用180 - (target + trim)实现方向反转
        servo[id].writeMicroseconds(angToUsec(180 - (target + trim[id])));
    
    // 记录当前舵机位置，供后续使用
    _servo_position[id] = target;
}
```

**这个函数的精巧之处在于**：

1. **校准值叠加**：在输出前加上`trim[id]`，补偿机械误差
2. **方向处理**：通过`180 - angle`实现方向反转
   - 数学原理：如果原方向是顺时针增加，反向后就是逆时针增加
   - 例如：原角度90度（向前）变成90度（因为180-90=90，保持不变）
   - 原角度120度（更向前）变成60度（更向后）
3. **角度转脉宽**：调用`angToUsec()`将角度转换为舵机需要的脉宽信号

#### 8.2 angToUsec()：角度到脉宽的转换

```cpp
int MiniKame::angToUsec(float value) {
    // 线性映射：0° -> MIN_PULSE_WIDTH (544μs)
    //          180° -> MAX_PULSE_WIDTH (2400μs)
    return value / 180 * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH) + MIN_PULSE_WIDTH;
}
```

**这个映射的数学原理**：

- 舵机通过脉宽信号控制角度，通常脉宽在500μs到2500μs之间对应0°到180°
- 这是一个线性关系：角度和脉宽成正比
- 公式可以写为：`脉宽 = 最小脉宽 + 角度 × (脉宽范围/180)`

**为什么使用微秒而不是直接写角度**？
Servo库提供了`write()`函数可以直接写角度，但`writeMicroseconds()`提供了更精细的控制。直接控制脉宽可以避免库内部的转换误差，也能更好地适配不同品牌的舵机。

#### 8.3 moveServos()：平滑移动的实现

```cpp
void MiniKame::moveServos(int time, float target[8]) {
    if (time > 10) {
        // 计算每10毫秒的增量
        // 总移动距离除以时间段数（time/10）
        for (int i = 0; i < 8; i++)
            _increment[i] = (target[i] - _servo_position[i]) / (time / 10.0);
        
        _final_time =  millis() + time;
        
        // 循环直到到达目标时间
        while (millis() < _final_time) {
            _partial_time = millis() + 10;
            
            // 每10ms增加一次
            for (int i = 0; i < 8; i++) 
                setServo(i, _servo_position[i] + _increment[i]);
            
            // 精确等待10ms
            while (millis() < _partial_time); // 忙等待
        }
    }
    else {
        // 时间很短，直接跳转到目标位置
        for (int i = 0; i < 8; i++) setServo(i, target[i]);
    }
    
    // 更新记录的位置
    for (int i = 0; i < 8; i++) _servo_position[i] = target[i];
}
```

**这个算法的设计思想**：

1. **分段线性插值**：将总移动时间分割成10ms的小段，每段移动一小步
2. **时间精度**：使用忙等待确保每段间隔精确为10ms
3. **边界处理**：时间太短时直接跳转，避免计算误差
4. **状态更新**：移动完成后更新记录的位置

**为什么需要平滑移动**？
如果直接从当前位置跳转到目标位置，会产生剧烈的冲击，不仅影响机器人稳定性，还可能损坏舵机齿轮。通过平滑移动，我们让运动变得柔和自然。

### 九、步态执行的统一接口：execute()函数

#### 9.1 execute()的整体架构

```cpp
void MiniKame::execute(float steps, int period[8], int amplitude[8], 
                       int offset[8], int phase[8]) {
    
    // 第一步：配置8个振荡器
    for (int i = 0; i < 8; i++) {
        oscillator[i].setPeriod(period[i]);
        oscillator[i].setAmplitude(amplitude[i]);
        oscillator[i].setPhase(phase[i]);
        oscillator[i].setOffset(offset[i]);
    }

    // 第二步：同步所有振荡器的起始时间
    unsigned long global_time = millis();
    for (int i = 0; i < 8; i++) 
        oscillator[i].setTime(global_time);

    // 第三步：执行指定步数
    _final_time = millis() + period[0] * steps;
    while (millis() < _final_time) {
        for (int i = 0; i < 8; i++) {
            setServo(i, oscillator[i].refresh());
        }
        yield();  // 喂看门狗，防止阻塞
    }
}
```

#### 9.2 execute()的逐行深度解析

**第一步：参数配置**

```cpp
for (int i = 0; i < 8; i++) {
    oscillator[i].setPeriod(period[i]);
    oscillator[i].setAmplitude(amplitude[i]);
    oscillator[i].setPhase(phase[i]);
    oscillator[i].setOffset(offset[i]);
}
```

这一步将传入的步态参数数组分别设置给8个振荡器。每个振荡器获得自己独立的参数，形成了所谓的"控制矩阵"。

**第二步：时间同步**

```cpp
unsigned long global_time = millis();
for (int i = 0; i < 8; i++) 
    oscillator[i].setTime(global_time);
```

**这是整个步态协调中最关键的一步**。所有振荡器使用同一个`global_time`作为参考时间，确保了它们的相位关系从一开始就是正确的。如果没有这一步，每个振荡器可能因为启动时间不同而导致相位错乱。

**第三步：实时计算与输出**

```cpp
_final_time = millis() + period[0] * steps;
while (millis() < _final_time) {
    for (int i = 0; i < 8; i++) {
        setServo(i, oscillator[i].refresh());
    }
    yield();
}
```

- `period[0] * steps`计算总执行时间（假设所有振荡器周期相同）
- 循环不断刷新每个振荡器的输出，并设置舵机
- `yield()`允许后台任务运行，防止看门狗超时

### 十、站立姿态的实现

#### 10.1 home()：标准站立姿态

```cpp
void MiniKame::home() {
    int ap = 20;   // 前后偏移量（anteroposterior）
    int hi = 25;   // 上下偏移量（height）
    
    int position[] = {
        90 + ap,    // 左前大腿：前摆20度
        90 - ap,    // 右前大腿：后摆20度
        90 - hi,    // 左前小腿：抬起25度
        90 + hi,    // 右前小腿：放下25度
        90 - ap,    // 左后大腿：后摆20度
        90 + ap,    // 右后大腿：前摆20度
        90 + hi,    // 左后小腿：放下25度
        90 - hi     // 右后小腿：抬起25度
    };
    
    for (int i = 0; i < 8; i++) setServo(i, position[i]);
}
```

**站立姿态的力学分析**：

1. **前后腿的对称设计**：
   - 前腿：左前向前（110°），右前向后（70°）
   - 后腿：左后向后（70°），右后向前（110°）
   - 这种对称使得机器人的重心位于身体中心

2. **小腿的对角补偿**：
   - 左前小腿抬起（65°），右前小腿放下（115°）
   - 左后小腿放下（115°），右后小腿抬起（65°）
   - 这种对角线的补偿确保了机身保持水平

3. **为什么这样设计**？
   如果所有腿的小腿都在同一高度，机身会向前或向后倾斜。通过对角线的高低搭配，我们让机身保持水平，同时为后续行走做好准备。

#### 10.2 zero()：归零姿态

```cpp
void MiniKame::zero() {
    for (int i = 0; i < 8; i++) setServo(i, 90);
}
```

**zero()的用途**：

- 初始调试时验证所有舵机是否正常工作
- 作为所有运动的基准点
- 在更换舵机或重新装配后重新校零

### 十一、行走步态深度解析

#### 11.1 walk()函数的整体结构

```cpp
void MiniKame::walk(float steps, int T = 5000) {
    // 1. 参数定义
    int x_amp = 15;      // 前后摆动振幅
    int z_amp = 20;      // 上下抬腿振幅
    int ap = 20;         // 前后偏移量
    int hi = 30;         // 上下偏移量
    int front_x = 12;    // 前腿额外前伸量
    
    // 2. 周期数组
    int period[] = {T, T, T / 2, T / 2, T, T, T / 2, T / 2};
    
    // 3. 振幅数组
    int amplitude[] = {x_amp, x_amp, z_amp, z_amp, 
                       x_amp, x_amp, z_amp, z_amp};
    
    // 4. 偏移数组
    int offset[] = {
        90 + ap - front_x,  // 左前大腿
        90 - ap + front_x,  // 右前大腿
        90 - hi,            // 左前小腿
        90 + hi,            // 右前小腿
        90 - ap - front_x,  // 左后大腿
        90 + ap + front_x,  // 右后大腿
        90 + hi,            // 左后小腿
        90 - hi             // 右后小腿
    };
    
    // 5. 相位数组
    int phase[] = {90, 90, 270, 90, 270, 270, 90, 270};
    
    // 6. 特殊的执行逻辑（不是直接调用execute）
    // ...（后面详细分析）
}
```

#### 11.2 walk()的参数解析

**周期数组的设计**：

```cpp
int period[] = {T, T, T / 2, T / 2, T, T, T / 2, T / 2};
```

- 索引0,1,4,5（大腿）：周期为T
- 索引2,3,6,7（小腿）：周期为T/2

**这个设计的生物力学意义**：
在生物行走中，腿的抬起和放下动作（由小腿控制）通常比前后摆动（由大腿控制）更快。通过让小腿周期减半，我们模拟了这种生物特性——小腿在更短的时间内完成抬起-放下的动作。

**偏移数组的详细计算**：

让我们逐个分析每个偏移值：

| 索引 | 公式              | 计算值       | 物理意义         |
| ---- | ----------------- | ------------ | ---------------- |
| 0    | 90 + ap - front_x | 90+20-12=98  | 左前大腿略微前伸 |
| 1    | 90 - ap + front_x | 90-20+12=82  | 右前大腿略微后摆 |
| 2    | 90 - hi           | 90-30=60     | 左前小腿抬起     |
| 3    | 90 + hi           | 90+30=120    | 右前小腿放下     |
| 4    | 90 - ap - front_x | 90-20-12=58  | 左后大腿后摆     |
| 5    | 90 + ap + front_x | 90+20+12=122 | 右后大腿前伸     |
| 6    | 90 + hi           | 90+30=120    | 左后小腿放下     |
| 7    | 90 - hi           | 90-30=60     | 右后小腿抬起     |

**相位数组的数学关系**：

```cpp
int phase[] = {90, 90, 270, 90, 270, 270, 90, 270};
```

如果我们按腿分组重新排列：

| 腿   | 大腿相位 | 小腿相位 | 相位差 |
| ---- | -------- | -------- | ------ |
| 左前 | 90°      | 270°     | 180°   |
| 右前 | 90°      | 90°      | 0°     |
| 左后 | 270°     | 90°      | 180°   |
| 右后 | 270°     | 270°     | 0°     |

**相位差的物理意义**：

- 相位差180°意味着两个运动完全相反：当大腿向前摆时，小腿抬起；当大腿向后摆时，小腿放下。这正是行走所需的"抬腿-前摆-落腿-后蹬"循环。
- 相位差0°意味着两个运动同步：当大腿向前时小腿也向前（实际上是放下），这会导致腿拖地。但在右前和右后腿上，这个"异常"正是为了配合对角步态。

#### 11.3 walk()的特殊执行逻辑

```cpp
// 设置每个振荡器的初始参数
for (int i = 0; i < 8; i++) {
    oscillator[i].reset();
    oscillator[i].setPeriod(period[i]);
    oscillator[i].setAmplitude(amplitude[i]);
    oscillator[i].setPhase(phase[i]);
    oscillator[i].setOffset(offset[i]);
}

_final_time = millis() + period[0] * steps;
_init_time = millis();
bool side;

while (millis() < _final_time) {
    // 每半个周期切换一次side
    side = (int)((millis() - _init_time) / (period[0] / 2)) % 2;
    
    // 大腿始终运动
    setServo(0, oscillator[0].refresh());
    setServo(1, oscillator[1].refresh());
    setServo(4, oscillator[4].refresh());
    setServo(5, oscillator[5].refresh());

    // 小腿交替运动
    if (side == 0) {
        // 前半周期：右前小腿和左后小腿运动
        setServo(3, oscillator[3].refresh());
        setServo(6, oscillator[6].refresh());
    }
    else {
        // 后半周期：左前小腿和右后小腿运动
        setServo(2, oscillator[2].refresh());
        setServo(7, oscillator[7].refresh());
    }
    delay(1);
}
```

**这个执行逻辑的精妙之处**：

1. **side的计算**：

   ```cpp
   side = (int)((millis() - _init_time) / (period[0] / 2)) % 2;
   ```

   - `(millis() - _init_time)`：从开始到现在的时间
   - 除以半个周期，得到已经过去的半周期个数
   - 对2取模，得到0或1，交替切换

2. **为什么小腿要交替**：

   - 小腿2和7是一组（左前和右后）
   - 小腿3和6是一组（右前和左后）
   - 这两组正好是对角线关系
   - 交替运动实现了标准的**对角小跑步态**：左前-右后同时抬起，右前-左后同时抬起

3. **大腿持续运动的理由**：

   - 大腿提供持续的前进动力
   - 无论小腿是否在运动，大腿都在按正弦规律摆动
   - 这样保证了运动的连续性

### 十二、转弯步态的实现

#### 12.1 turnL()：左转的代码实现

```cpp
void MiniKame::turnL(float steps, int T = 600) {
    int x_amp = 15;
    int z_amp = 15;
    int ap = 15;
    int hi = 23;
    
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {x_amp, x_amp, z_amp, z_amp, 
                       x_amp, x_amp, z_amp, z_amp};
    int offset[] = {90 + ap, 90 - ap, 90 - hi, 90 + hi, 
                    90 - ap, 90 + ap, 90 + hi, 90 - hi};
    int phase[] = {180, 0, 90, 90, 0, 180, 90, 90};
    
    execute(steps, period, amplitude, offset, phase);
}
```

#### 12.2 转弯步态的相位分析

**左转相位矩阵**：

| 舵机 | 相位 | 所属腿   | 物理意义       |
| ---- | ---- | -------- | -------------- |
| 0    | 180° | 左前大腿 | 与右前相位相反 |
| 1    | 0°   | 右前大腿 | 与左前相位相反 |
| 2    | 90°  | 左前小腿 | 保持90°        |
| 3    | 90°  | 右前小腿 | 保持90°        |
| 4    | 0°   | 左后大腿 | 与右后相位相反 |
| 5    | 180° | 右后大腿 | 与左后相位相反 |
| 6    | 90°  | 左后小腿 | 保持90°        |
| 7    | 90°  | 右后小腿 | 保持90°        |

**转弯的力学原理**：

1. **左右侧相位相反**：
   - 左侧腿向前时（相位0°附近），右侧腿向后（相位180°附近）
   - 这产生了使机器人旋转的力矩

2. **前后腿的关系**：
   - 左前(180°)和左后(0°)相位差180°
   - 这意味着前腿向前时后腿向后，进一步加强了旋转效果

3. **小腿相位保持一致**：
   - 所有小腿相位都是90°左右
   - 这确保了在旋转过程中腿仍然能够抬起和放下

#### 12.3 turnR()：右转的实现

```cpp
void MiniKame::turnR(float steps, int T = 600) {
    // ... 相同参数 ...
    int phase[] = {0, 180, 90, 90, 180, 0, 90, 90};
    // 与左转相比，左右腿相位互换
    execute(steps, period, amplitude, offset, phase);
}
```

**左转和右转的对称性**：

- 左转：左侧腿相位180°，右侧0°
- 右转：左侧腿相位0°，右侧180°
- 这种对称设计使得代码简洁且易于理解

### 十三、特殊动作步态

#### 13.1 dance()：舞蹈模式

```cpp
void MiniKame::dance(float steps, int T = 600) {
    int x_amp = 0;        // 大腿不摆动
    int z_amp = 40;       // 小腿大幅度摆动
    int ap = 30;          // 较大偏移
    int hi = 20;
    
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {x_amp, x_amp, z_amp, z_amp, 
                       x_amp, x_amp, z_amp, z_amp};
    int offset[] = {90 + ap, 90 - ap, 90 - hi, 90 + hi, 
                    90 - ap, 90 + ap, 90 + hi, 90 - hi};
    int phase[] = {0, 0, 0, 270, 0, 0, 90, 180};
    
    execute(steps, period, amplitude, offset, phase);
}
```

**舞蹈步态的"混乱"之美**：

1. **大腿不摆动**：`x_amp = 0`意味着大腿保持固定位置，只有小腿运动
2. **小腿大幅度摆动**：`z_amp = 40`比行走时的20度大了一倍
3. **相位乱序**：`0,0,0,270,0,0,90,180`没有规律性
4. **偏移增大**：`ap = 30`让身体姿态更加夸张

**舞蹈效果的来源**：
当相位不再遵循对角步态的规律，四条腿各自为政时，机器人就会呈现出扭动、摇摆的效果。这告诉我们：**规律产生秩序，秩序产生功能；打破规律产生变化，变化产生趣味**。

#### 13.2 pushUp()：俯卧撑

```cpp
void MiniKame::pushUp(float steps, int T = 600) {
    int z_amp = 30;       // 小腿振幅30度
    int x_amp = 60;       // 后腿后伸60度
    int hi = 20;
    
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {0, 0, z_amp, z_amp, 0, 0, 0, 0};
    // 只有前腿小腿（索引2,3）有振幅
    
    int offset[] = {
        90, 90,           // 前腿大腿固定
        90 - hi, 90 + hi, // 前腿小腿上下运动
        90 - x_amp,       // 左后大腿后伸
        90 + x_amp,       // 右后大腿后伸
        90 + hi, 90 - hi  // 后腿小腿固定
    };
    
    int phase[] = {0, 0, 0, 180, 0, 0, 0, 170};
    
    execute(steps, period, amplitude, offset, phase);
}
```

**俯卧撑的运动学分析**：

1. **选择性激活**：只有舵机2和3（前腿小腿）在运动，其他舵机保持固定
2. **后腿后伸**：舵机4设为30度（90-60），舵机5设为150度（90+60），使身体前倾
3. **前腿小腿运动**：在30度范围内上下摆动
4. **相位关系**：两个前腿小腿相位差180°（0°和180°），交替抬起和放下

**这模拟了俯卧撑的动作**：

- 身体前倾，重心前移
- 前腿交替弯曲和伸直
- 后腿固定，作为支点

#### 13.3 moonwalkL()：太空步

```cpp
void MiniKame::moonwalkL(float steps, int T = 5000) {
    int z_amp = 45;       // 小腿大幅摆动
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {0, 0, z_amp, z_amp, 0, 0, z_amp, z_amp};
    // 只有小腿运动，大腿固定
    
    int offset[] = {90, 90, 90, 90, 90, 90, 90, 90};
    // 所有偏移都在90度
    
    int phase[] = {0, 0, 0, 120, 0, 0, 180, 290};
    // 小腿相位错开
    
    execute(steps, period, amplitude, offset, phase);
}
```

**太空步的效果原理**：

- 大腿固定，只有小腿运动
- 小腿的相位错开（0°, 120°, 180°, 290°）
- 这会产生波浪般的运动，视觉上像在滑动

#### 13.4 frontBack()：前后移动

```cpp
void MiniKame::frontBack(float steps, int T = 600) {
    int x_amp = 30;       // 大幅度前后摆动
    int z_amp = 25;       // 中幅度上下抬腿
    int ap = 20;
    int hi = 30;
    
    int phase[] = {0, 180, 270, 90, 0, 180, 90, 270};
    // 相位配置使得前后运动更加明显
}
```

**前后移动的特点**：

- 较大的前后振幅（30度）产生大步幅
- 相位设计让所有腿协同向前或向后

#### 13.5 upDown()：上下蹲起

```cpp
void MiniKame::upDown(float steps, int T = 5000) {
    int x_amp = 0;        // 大腿不摆动
    int z_amp = 25;       // 小腿统一运动
    
    int phase[] = {0, 0, 90, 270, 180, 180, 270, 90};
    // 所有小腿同步运动，但前后腿相位相反
}
```

**上下蹲起的原理**：

- 只有小腿运动，大腿固定
- 前后腿相位相反：前腿抬起时后腿放下
- 这样机身会整体上下移动

### 十四、高级步态：omniWalk()

#### 14.1 omniWalk()的整体结构

```cpp
void MiniKame::omniWalk(float steps, int T, bool side, float turn_factor) {
    int x_amp = 15;
    int z_amp = 15;
    int ap = 15;
    int hi = 23;
    int front_x = 6 * (1 - pow(turn_factor, 2));
    
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {x_amp, x_amp, z_amp, z_amp, 
                       x_amp, x_amp, z_amp, z_amp};
    
    int offset[] = {
        90 + ap - front_x,
        90 - ap + front_x,
        90 - hi,
        90 + hi,
        90 - ap - front_x,
        90 + ap + front_x,
        90 + hi,
        90 - hi
    };

    int phase[8];
    if (side) {  // 右转
        int phase1[] =  {0,   0,   90,  90,  180, 180, 90,  90};
        int phase2R[] = {0,   180, 90,  90,  180, 0,   90,  90};
        for (int i = 0; i < 8; i++)
            phase[i] = phase1[i] * (1 - turn_factor) + phase2R[i] * turn_factor;
    }
    else {  // 左转
        int phase1[] =  {0,   0,   90,  90,  180, 180, 90,  90};
        int phase2L[] = {180, 0,   90,  90,  0,   180, 90,  90};
        for (int i = 0; i < 8; i++)
            phase[i] = phase1[i] * (1 - turn_factor) + phase2L[i] * turn_factor 
                      + oscillator[i].getPhaseProgress();
    }
    
    execute(steps, period, amplitude, offset, phase);
}
```

#### 14.2 omniWalk()的创新之处

**1. 前伸量的动态调整**：

```cpp
int front_x = 6 * (1 - pow(turn_factor, 2));
```

- `turn_factor`为0时（直行），`front_x = 6`
- `turn_factor`为1时（急转弯），`front_x = 0`
- 转弯越急，前腿的前伸量越小，有利于转向

**2. 相位的线性插值**：

```cpp
phase[i] = phase1[i] * (1 - turn_factor) + phase2R[i] * turn_factor;
```

这是**线性插值**的经典应用。当`turn_factor`从0逐渐变化到1时，相位会从行走步态连续过渡到转弯步态。

**3. 当前相位的利用**：
在左转的代码中，加入了`oscillator[i].getPhaseProgress()`：

```cpp
+ oscillator[i].getPhaseProgress()
```

这确保了在切换过程中相位的连续性，避免了突变。

**4. omniWalk的设计理念**：

- **连续控制**：不再是离散的"行走"或"转弯"，而是可以连续调节转向程度
- **平滑过渡**：通过插值实现无缝切换
- **实时响应**：可以在运动过程中动态改变参数

### 十五、动作序列：hello()

#### 15.1 hello()的完整代码

```cpp
void MiniKame::hello() {
    // 第一步：坐下
    float sentado[] = {
        90 + 15,  // 左前大腿前伸
        90 - 15,  // 右前大腿后摆
        90 - 10,  // 左前小腿轻微抬起
        90 + 60,  // 右前小腿大幅放下（实际上是要抬起？）
        90 + 10,  // 左后大腿前伸
        90 - 10,  // 右后大腿后摆
        90 + 10,  // 左后小腿放下
        90 - 10   // 右后小腿抬起
    };
    moveServos(150, sentado);
    delay(300);

    // 第二步：挥手（执行4次振荡）
    int z_amp = 40;
    int x_amp = 60;
    int T = 550;
    int period[] = {T, T, T, T, T, T, T, T};
    int amplitude[] = {0, 50, 0, 50, 0, 0, 0, 0};
    int offset[] = {
        90 + 15,  // 左前大腿
        40,       // 右前大腿大幅前伸
        90 - 30,  // 左前小腿
        90,       // 右前小腿
        90 + 20,  // 左后大腿
        90 - 20,  // 右后大腿
        90 + 10,  // 左后小腿
        90 - 10   // 右后小腿
    };
    int phase[] = {0, 0, 0, 90, 0, 0, 0, 0};
    
    execute(4, period, amplitude, offset, phase);

    // 第三步：站起
    float goingUp[] = {
        90,       // 左前大腿回正
        70,       // 右前大腿后摆
        90,       // 左前小腿回正
        90,       // 右前小腿回正
        90 - 20,  // 左后大腿后摆
        90 + 20,  // 右后大腿前伸
        90 + 10,  // 左后小腿
        90 - 10   // 右后小腿
    };
    moveServos(500, goingUp);
    delay(200);
}
```

#### 15.2 hello()的动作分解

**第一步：坐下**

- `sentado`在西班牙语中是"坐下"的意思
- 关键变化：右前小腿设为150度（90+60），这是一个很大的角度
- 这会使右前腿大幅弯曲，身体重心降低
- 其他腿做相应调整保持平衡

**第二步：挥手**

- 只有舵机1（右前大腿）和舵机3（右前小腿）在运动
- 振幅50度，让右前腿大幅摆动
- 执行4次振荡，模拟挥手的动作
- 其他腿保持固定，维持坐姿

**第三步：站起**

- 恢复站立姿态
- 右前大腿回到70度（比标准姿态更后）
- 其他腿调整到最终位置

#### 15.3 hello()的设计思想

这个函数展示了**动作序列的编排**：

1. **准备动作**：坐下，引起注意
2. **主要动作**：挥手，传达信息
3. **收尾动作**：站起，恢复正常

通过多个基本动作的组合，我们创造了富有表现力的行为。这种设计思路可以扩展到更复杂的交互场景。

### 十六、校准与调试

#### 16.1 trim值的确定方法

校准是让理论模型适应物理现实的关键步骤。以下是详细的校准流程：

**步骤1：机械归零**

将所有舵机物理拆卸，分别设置到90度，然后安装腿部件。这样可以确保机械结构的基准是正确的。

**步骤2：初步校准**

```
// 校准测试程序
void MiniKame::calibrate() {
    zero();  // 所有舵机到90度
    delay(2000);  // 观察2秒
    
    // 然后逐一调整
    for (int i = 0; i < 8; i++) {
        // 只调整当前舵机
        setServo(i, 90 + test_offset);
        delay(1000);
    }
}
```

**步骤3：观察与记录**

将机器人放在水平面上，观察：

- 四条腿是否都接触地面？
- 机身是否水平？
- 是否有腿悬空或过度受压？

根据观察结果调整对应的trim值。

**步骤4：反复迭代**

通常需要3-5次迭代才能得到满意的校准结果。

#### 16.2 reverse方向的确定

reverse标志用于处理舵机安装方向不一致的问题。确定方法如下：

1. 将所有reverse设为false
2. 调用`home()`函数
3. 观察每条腿的运动方向：
   - 如果增加角度时腿向前/向上，则reverse应为false
   - 如果增加角度时腿向后/向下，则reverse应为true

#### 16.3 调试技巧

**使用串口监视器**：

```
void MiniKame::debugPrint() {
    Serial.println("=== 当前舵机状态 ===");
    for (int i = 0; i < 8; i++) {
        Serial.print("Servo ");
        Serial.print(i);
        Serial.print(": target=");
        Serial.print(_servo_position[i]);
        Serial.print(", output=");
        Serial.println(oscillator[i].getOutput());
    }
}
```

**单步执行**：

在关键位置添加`while(!Serial.available());`可以让程序暂停，等待用户按任意键继续，便于观察每个步骤的效果。

