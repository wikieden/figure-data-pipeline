# 第 5 章 时间、同步与标定

多流对齐是数据可用性的命门。一条 episode 可以画质完美、动作流畅，但只要视觉和动作差了 20 ms，学到的就是错位的因果。这一章讲本仓库的时间语义、同步手段、误差预算和标定纪律（[architecture.md](../architecture.md) §8）。ingest 校验和 curation 拒收判据都以本章为准。

## 5.1 两枚时间戳

每条 MCAP 消息带两枚原生时间戳：

- `log_time`：写入记录器的时刻；
- `publish_time`：传感器或驱动声明的**采样时刻**。

**训练与对齐只用 `publish_time`。** `log_time` 只用于诊断记录延迟。理由很简单：写入时刻受队列、磁盘、调度影响，和物理世界里"那一刻发生了什么"无关。

其余约定：

- 单位一律 ns，int64；episode 内用**单调时钟**（`CLOCK_MONOTONIC_RAW` 或等价物），另存一枚"单调→UTC"偏移（`started_at_ns`），跨设备、跨会话的比较只在 UTC 层做。
- **视频帧取曝光中点**，不取帧到达时刻。全局快门相机直接用；卷帘快门相机记录曝光起止，并在标定文件里声明行读出时间。无曝光信息的设备用 `pts − 0.5/fps` 近似并标 `flag:pts_approx`。
- 遥操作动作另记 `command_time`（发出时刻），用来量化闭环延迟。

## 5.2 四种同步手段

| 手段 | 适用 | 可达精度 | 备注 |
|---|---|---|---|
| 硬件触发（相机 GPIO 同步脉冲 + IMU 同步） | robot 轨多相机、自研头戴设备 | <0.1 ms | 需全局快门与触发线；自研设备的默认方案 |
| 同一 SoC 单时钟域软同步 | 手机、GoPro 单机 | 1–5 ms | 零额外硬件，视频与 IMU 同源即可 |
| PTP（IEEE 1588）/ 有线 NTP | 机器人本体多计算板 | PTP <0.1 ms、NTP 1–10 ms | robot 轨跨板必须 PTP |
| 事后相关对齐（IMU 角速度 vs 视觉旋转、LED/拍手标记） | GoPro + 外部 IMU、多设备同穿戴 | 1–3 ms | 零硬件；ingest 内建，产出对齐残差进 QC |

## 5.3 跨时钟域

每个物理设备是一个时钟域。episode 元数据记录所有参与的时钟域及其对 UTC 的偏移与漂移估计（`clock_domains[]`：`name, offset_to_utc_ns, drift_ppm`）。

- **多设备同录**（如头戴 + UMI 同戴）：会话开始与结束各做一次同步事件（LED 闪烁 + 拍手，双设备可见可闻），ingest 据此估计偏移和线性漂移；漂移 >1 ms/min 的会话标 `flag:clock_drift`。
- **没有同步事件**的多设备会话：用 IMU 角速度 vs 视觉旋转互相关估计偏移（窗口 30 s，搜索 ±500 ms）（[ingest-spec.md](../ingest-spec.md) §3）。
- **机器人本体**：主控为时间主，相机、触觉、遥操作端全部对齐到主控 PTP 时钟；遥操作端走 NTP 到主控，ingest 再用动作-状态互相关校一次。

## 5.4 同步误差预算

以动作专家 100–200 Hz 消费为约束，一个控制周期 5–10 ms：

| 流对 | 预算 | 依据 |
|---|---|---|
| 视觉 ↔ 动作/状态 | ≤5 ms（robot/device）；≤15 ms（human，仅供伪标签） | 一个 200 Hz 控制周期内；human 轨无动作真值，要求放宽 |
| IMU ↔ 视觉 | ≤2 ms | VIO 收敛条件 |
| 多相机彼此 | ≤1 ms（硬件触发）/ ≤10 ms（软同步，仅允许 human 轨） | 立体与多视角一致性 |
| 触觉 ↔ 动作 | ≤2 ms | 接触事件对齐 |

**超预算怎么办**：不删除。标 `flag:sync_budget_exceeded`，从 robot/device 轨训练分片排除，但可以留在 human 轨的消费路径。这是"清洗是标记不是删除"的第一个具体例子：同一条数据对一种用途不合格，对另一种用途仍有价值。

## 5.5 标定工序与漂移再估计

- **出厂标定**：相机内参 + 相机-IMU 外参 + 时间偏移（Kalibr 标准工序，棋盘或 AprilGrid）。标定文件随设备档案走（`device_id → calibration_ref`），每条 episode 引用标定版本。
- **在线再估计**：每次 ingest 用 VIO 残差与 IMU-视觉时间偏移估计值和出厂值比对；时间偏移 >1 ms 或外参旋转 >0.5° 的设备进"待重标"队列，其数据标 `flag:calib_stale`。
- **规模化纪律**：几十台以上设备时，标定一致性成为主要误差源（UMI 规模化的经验）。标定文件哈希进 lineage，任何重标产生新的标定版本，**不覆盖**。

human 轨众包设备没有出厂标定，内参从视频估计（GeoCalib / DroidCalib 类方法），写入元数据时注明来源为估计值（[data-format-contract.md](../data-format-contract.md) §3.1，契约 0.3 待入项）。

## 5.6 不重采样

ingest 阶段的对齐**只产生偏移与残差元数据，不改数据**。所有流保留原生时间戳。训练取帧时的规则（[curation-pipeline.md](../curation-pipeline.md) §5）：

- 信号流线性插值到查询时刻；
- 视觉流取最近帧，并记录取帧 Δt（`fdp.image_dt_ns.<camera>`），模型可选消费。

这样做的好处是对齐算法可以升级：bump `ingest_version` 后重算偏移，原始数据不动。

## 5.7 本章小结

- 只用 `publish_time`；视频取曝光中点；单调时钟 + UTC 偏移。
- 四种同步手段按场景选；robot 轨跨板必须 PTP，自研设备默认硬件触发。
- 误差预算以一个控制周期为界；超预算标记、按用途排除，不删除。
- 标定随数据走、只增版本不覆盖；在线再估计发现漂移就打标。
- 对齐产出元数据，不改数据；插值推迟到训练取帧。

**延伸阅读**：[architecture.md](../architecture.md) §8 · [ingest-spec.md](../ingest-spec.md) §3 · [capture-devices-design.md](../capture-devices-design.md) §6
