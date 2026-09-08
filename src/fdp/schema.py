"""Episode schema：分层采样率、版本化、可空模态。

设计对标 Helix 02 的三层消费（见 docs/architecture.md §2/§3）：
- 视觉流 ~10-30 Hz（S2/VLM 消费）
- 状态/动作流 100-200 Hz（S1/动作专家消费）
- 所有模态可空（mask）：老数据在新传感器套件下仍可用，人类视频轨无动作真值。

四条 ingest 轨共用同一 schema，以 `track` 区分。采集方式是组合而非单选
（Figure 双轨 + Generalist 手持夹爪的共同结论），配比由下游消融裁决。
"""

from enum import StrEnum

from pydantic import BaseModel, Field

SCHEMA_VERSION = "0.1"


class Track(StrEnum):
    """数据来源轨道。"""

    ROBOT = "robot"  # 遥操作/车队真机：全模态 + 动作真值
    HUMAN = "human"  # 第一视角人类视频：无动作标签（后续重定向伪标签）
    DEVICE = "device"  # 手持采集设备（UMI/Data Hands 式）：SLAM 位姿 + 开合编码，硬件动作真值
    SIM = "sim"  # 仿真 rollout（Isaac Lab / MimicGen 等）


class VideoStream(BaseModel):
    """一路相机流（头部/腕部/掌心等）。"""

    name: str
    fps: float
    width: int
    height: int
    encoding: str = "h264"  # 机上采集 h264 硬编；入湖转 AV1 yuv420p


class SignalStream(BaseModel):
    """一路低维高频信号（关节状态、动作、触觉、力觉等）。"""

    name: str
    rate_hz: float
    dim: int
    dtype: str = "float32"
    # 映射到统一状态-动作槽位向量的区段（如 "ee_pose"/"gripper"/"joint_pos"），
    # None = 不进槽位向量（原始传感器流）。见 docs/training-pipeline.md §1.2-3
    slot: str | None = None


class EpisodeMeta(BaseModel):
    """一条 episode 的元数据。原始数据本体存 MCAP，训练态导出为 LeRobotDataset v3。"""

    schema_version: str = SCHEMA_VERSION
    episode_id: str
    track: Track
    robot_model: str | None = None  # human 轨为 None
    operator_id: str | None = None  # 采集员/Creator 标识（质量归因、消融切分用）
    started_at_ns: int
    duration_ns: int
    videos: list[VideoStream] = Field(default_factory=list)
    signals: list[SignalStream] = Field(default_factory=list)
    # 分层语言标注：任务级 + 子任务级（对齐 Index 的 hierarchical caption）
    task_instruction: str | None = None
    subtask_instructions: list[str] = Field(default_factory=list)
    # 策展状态
    quality_flags: list[str] = Field(default_factory=list)  # L1/L2/L3 QC 产出
    curated: bool = False
    # RL 闭环素材（robot/device 轨；奖励分类器直接消费，docs/training-pipeline.md §2 Stage D）
    success: bool | None = None  # None = 未标注/不适用
    intervention_ts_ns: list[int] = Field(default_factory=list)  # 遥操作接管时刻
