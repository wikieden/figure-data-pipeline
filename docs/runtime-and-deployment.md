# 运行时与部署：推理栈 · 延迟预算 · OOD/reset · 回流 · 安全

> 2026-09-08。architecture §7 运行时层的展开。本仓库范围止于"策略部署产生的数据如何回流"，推理框架本身用 LeRobot 的 PolicyServer/RobotClient 异步栈，不自研。

## 1. 部署栈

- 策略服务：LeRobot `PolicyServer`（GPU 工作站或机上 Orin 级）+ `RobotClient`（机器人主控），异步动作块（chunk）执行，实测吞吐 ×2（architecture §7）。
- 观测预处理与训练严格同源：同一份相机语义映射（data-format-contract §2.2）、同一归一化统计文件（按 dataset_version 固定）、同一分辨率阶梯——**train/serve skew 的三大来源全部由 export 产物驱动，不在运行时手写**。
- 版本：`policy_version` = checkpoint 哈希 + dataset_version + mixture 哈希；`deployment_id` = 机器人 + 场地 + 日期。两者写进回流 episode。

## 2. 延迟预算

| 环节 | 预算 |
|---|---|
| 相机曝光 → 观测就绪 | ≤30 ms |
| 推理（S1 等价层，动作块 H=50 @ 50–100 Hz） | ≤80 ms（每块） |
| 传输（服务端 → 主控） | ≤10 ms（有线）/ ≤30 ms（无线） |
| 执行器闭环 | 5–10 ms |
| 端到端（观测 → 首个动作） | **≤150 ms**；超预算连续 1 s 触发降级（放慢动作块重采样，Figure "Sport Mode" 的反向） |

每次部署记录延迟直方图进 `/meta/health`，进 eval 报告。

## 3. OOD 检测与 reset

- OOD 信号（任一触发即记事件 `/event/ood`）：动作块内一致性差（连续块首尾动作跳变 > 阈值）、观测 embedding 到训练分布的距离（训练集 embedding 的 k-NN 距离分位数）、任务进度停滞（子任务判据 N 秒无进展）、力/触觉超限。
- 处置分级：一级放慢 + 重规划；二级停止并请求人工接管（遥操作站或远程）；三级 estop。
- 自动 reset：任务模板定义可安全 reset 的初始位形与前向/后向控制器（HIL-SERL 的 SERL 模式）；不可自动 reset 的任务由人复位并记事件。
- 所有 OOD 事件与接管一起对齐到 episode 时间轴，是 RL 闭环的负样本来源。

## 4. 回流策略

- 全量记录自主运行（`source="fleet"`），回坞批量上传；带宽有限时优先上传含接管/OOD/失败的 episode，成功 episode 抽样 20%。
- 回流数据用途见 robot-track-teleop §6；隐私约束见 compliance §1/§3（家庭部署机上脱敏）。
- 回流触发再训练：接管率周环比上升 >30% 或某任务簇成功率跌破阈值 → 开 RECAP 式后训练 run（training-pipeline Stage D）。

## 5. 安全

- 机器人安全标准对齐：ISO 10218/ISO/TS 15066（协作）为基线，人形/移动场景补充 ISO 13482；速度/力限制在主控硬编码，策略输出经安全过滤器（关节限位、速度、工作空间边界）后才执行。
- 紧急停止：物理 estop + 遥操作站软 estop + 策略服务心跳丢失 200 ms 自动停机。
- 部署前检查单：延迟预算实测、安全过滤器测试、OOD 阈值来自当前 dataset_version、回流 recorder 正常。

## 6. 交付

- M3：PolicyServer/RobotClient 接入、`/event/ood` schema、回流 ingest 适配（`--source fleet`）、延迟直方图进 health。
