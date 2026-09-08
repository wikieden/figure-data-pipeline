# recorder 规范：机上落盘 · flush/fsync · 带宽与存储预算 · 断电恢复

> 2026-09-08。M1 交付物 `fdp record` 的行为规范，覆盖 robot 轨遥操作站、自研头戴设备固件（P1）与 device 轨设备的共同要求；P0 手机/GoPro 走各自原生录制，只需满足 §5 的输出要求。同步语义见 architecture §8。

## 1. 写入模型

- 单进程 MCAP writer，多生产者线程/进程经有界队列投递消息；队列满时**丢低优先级流**（预览/健康）先于丢高优先级流（动作/视频关键帧），丢弃计数进 `/meta/health`。
- 每 chunk 4 MB 或 1 s 先到即 flush；每 5 s 或每个关键帧组 fsync 一次；`/meta/episode` 与 `/meta/calibration` 在文件头写入并在每个 part 重复。
- 文件分段：2 GB 或 10 分钟切换 part，切换时旧文件写尾部索引并关闭；episode 结束写最终 `/meta/episode`（含 `duration_ns`）。
- 时钟：单调时钟采样，进程启动时记录单调→UTC 偏移；robot 轨主控为 PTP 主，遥操作端 NTP 到主控。

## 2. 带宽预算验算（机上）

| 配置 | 视频 | 信号 | 合计写入 |
|---|---|---|---|
| robot 轨：3 路 1080p30 h264 硬编 @ 8 Mbps + 200 Hz 状态/动作 + 触觉 | 24 Mbps | ~1 Mbps | ~3.2 MB/s ≈ 11.5 GB/h |
| 自研头戴 P1：1440p60 h265 @ 20 Mbps + 2 路灰度 SLAM 60 fps @ 4 Mbps + 双 IMU | 28 Mbps | <0.5 Mbps | ~3.6 MB/s ≈ 13 GB/h |
| UMI（GoPro 原生） | 60–100 Mbps（GoPro 码率） | 遥测内嵌 | 27–45 GB/h（P0 接受，入湖转 AV1） |

写入介质要求：持续 ≥20 MB/s（留 5× 余量），eMMC/UFS/NVMe 均满足；SD 卡需 V30 以上。

## 3. 存储预算（机上）

- 一个班次 4 小时 × 13 GB/h ≈ 52 GB；设备存储 256 GB = 4–5 个班次不回传也不丢（index-replica-plan §1 表）。
- 环形缓冲：已确认上传（服务端哈希回执）的 part 才可被覆盖；未上传数据占满时**停止录制并提示**，不覆盖。
- 磁盘满降级：剩余 <10% 时关闭预览流写入并降主视频码率一档；<5% 停录。

## 4. 断电与崩溃恢复

- 断电后 MCAP 可读性：已 fsync 的 chunk 全部可恢复；未 fsync 的最多丢 5 s；缺失尾部索引由 ingest 线性扫描恢复（ingest-spec §2）。
- 恢复测试（M1 验收必做）：录制中随机断电 20 次，要求 100% 文件可被 ingest 恢复、丢失时长 ≤5 s、无静默数据错位（用已知同步事件验证对齐仍在预算内）。
- 崩溃后重启：recorder 发现未关闭的 part 文件 → 写恢复标记、新开 part 续录同一 episode（`/meta/segment` 记录续接），不新开 episode。

## 5. 非自研录制端（P0）的输出要求

- GoPro/手机：视频 + 遥测（IMU、GPS 剥离）+ 录制起止的 UTC 时间；App 负责写 `/meta/episode` 等价的 sidecar JSON（`episode_id`、`session_id`、`device_id`、`consent_ref`、`region`、任务模板 id、口令时间戳）。
- 同步事件：多设备同录会话开始与结束各做一次 LED 闪烁 + 拍手（architecture §8.3）。
- ingest 拆流转 MCAP（ingest-spec §3），P0 不要求机上 MCAP。

## 6. 中间件裁决（governance U-01）

M1 recorder 实现前两周做对比原型：dora-rs 节点 vs 自写采集循环，各跑 §4 的断电测试与 architecture §8.4 的同步残差测量，嵌入式（RK3588 级）CPU 占用 <30%。三项都过者取实现更简单的一方；只有一方过则取该方。裁决结果回写本节并关闭 U-01。

## 7. 交付与测试

- 单测：队列丢弃优先级、part 切换、`/meta/episode` 头尾一致。
- 集成：合成三路流录 10 分钟，ingest 全通过，同步残差在预算内。
- 硬件在环：§4 断电测试 20 次。
