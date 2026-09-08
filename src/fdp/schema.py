"""Episode schema：分层采样率、版本化、可空模态。

设计对标 Helix 02 的三层消费（见 docs/architecture.md §2/§3）：
- 视觉流 ~10-30 Hz（S2/VLM 消费）
- 状态/动作流 100-200 Hz（S1/动作专家消费）；device 轨按传感器原生频率（≥50 Hz）入湖
- 所有模态可空（mask）：老数据在新传感器套件下仍可用，人类视频轨无动作真值。

四条 ingest 轨共用同一 schema，以 `track` 区分。采集方式是组合而非单选，配比由下游消融裁决。
字段级契约与写入者见 docs/data-format-contract.md §3；改字段先改那里。
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = "0.2"
SUPPORTED_VERSIONS = ("0.1", "0.2")


class Track(StrEnum):
    """数据来源轨道。"""

    ROBOT = "robot"  # 遥操作/车队真机：全模态 + 动作真值
    HUMAN = "human"  # 第一视角人类视频：无动作标签（后续重定向伪标签）
    DEVICE = "device"  # 手持/穿戴采集设备（UMI/Data Hands 式）：SLAM 位姿 + 开合编码，硬件动作真值
    SIM = "sim"  # 仿真 rollout / 增殖 / 神经轨迹 / 动捕重定向（source 子字段区分）


class EpisodeState(StrEnum):
    """策展状态机（docs/curation-pipeline.md §0）。"""

    RAW = "raw"
    INGESTED = "ingested"
    GATED = "gated"
    SCORED = "scored"
    SEGMENTED = "segmented"
    LABELED = "labeled"
    TRAINING_READY = "training_ready"
    REJECTED = "rejected"


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
    # 映射到统一状态-动作槽位向量的区段（如 "ee_pose_left"/"gripper_left"/"joint_pos"），
    # None = 不进槽位向量（原始传感器流）。见 docs/data-format-contract.md §2.3
    slot: str | None = None


class ClockDomain(BaseModel):
    """一个物理设备的时钟域及其对 UTC 的偏移/漂移估计（docs/architecture.md §8.3）。"""

    name: str
    offset_to_utc_ns: int
    drift_ppm: float = 0.0


class Subtask(BaseModel):
    """子任务区间与指令；区间为 None 表示只有指令没有时间边界（0.1 迁移数据）。"""

    instruction: str
    start_ns: int | None = None
    end_ns: int | None = None


class EpisodeMeta(BaseModel):
    """一条 episode 的元数据。原始数据本体存 MCAP，训练态导出为 LeRobotDataset v3。"""

    schema_version: str = SCHEMA_VERSION
    episode_id: str
    track: Track
    session_id: str | None = None
    source: str | None = None  # sim 子来源 / robot 轨回流 "fleet"
    robot_model: str | None = None  # human 轨为 None
    operator_id: str | None = None  # 采集员/Creator 标识（质量归因、消融切分用）
    device_id: str | None = None
    calibration_ref: str | None = None
    firmware_version: str | None = None
    started_at_ns: int
    duration_ns: int
    clock_domains: list[ClockDomain] = Field(default_factory=list)
    videos: list[VideoStream] = Field(default_factory=list)
    signals: list[SignalStream] = Field(default_factory=list)
    # 场景与多样性标签（再平衡、held-out 组切分）
    scene_id: str | None = None
    environment_tags: list[str] = Field(default_factory=list)
    object_tags: list[str] = Field(default_factory=list)
    # 分层语言标注：任务级 + 子任务级（对齐 Index 的 hierarchical caption）
    task_instruction: str | None = None
    # 0.1 遗留字段；0.2 起以 subtasks 为准
    subtask_instructions: list[str] = Field(default_factory=list)
    subtasks: list[Subtask] = Field(default_factory=list)
    # 策展状态；quality_flags 是 L1/L2/L3 QC 产出，标记不删除
    state: EpisodeState = EpisodeState.RAW
    quality_flags: list[str] = Field(default_factory=list)
    quality_score: float | None = None
    curated: bool = False
    split: str | None = None
    split_version: str | None = None
    # RL 闭环素材（robot/device/sim 轨；奖励分类器直接消费，docs/training-pipeline.md §2 Stage D）
    success: bool | None = None  # None = 未标注/不适用
    intervention_ts_ns: list[int] = Field(default_factory=list)  # 遥操作接管时刻
    # 存储与来源审计
    storage_uri: str | None = None
    content_hash: str | None = None
    size_bytes: int | None = None
    consent_ref: str | None = None
    region: str | None = None
    # 运行时回流与派生关系
    policy_version: str | None = None
    deployment_id: str | None = None
    parent_episode_id: str | None = None


def migrate(raw: dict[str, Any]) -> EpisodeMeta:
    """把任一受支持版本的元数据字典升级为当前 schema（读侧迁移，不回写原文件）。"""
    data = dict(raw)
    version = str(data.get("schema_version", "0.1"))
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(
            f"unsupported schema_version {version!r}; supported: {SUPPORTED_VERSIONS}"
        )
    if version == "0.1":
        if not data.get("subtasks") and data.get("subtask_instructions"):
            data["subtasks"] = [
                {"instruction": s} for s in data["subtask_instructions"]
            ]
        if "state" not in data:
            data["state"] = (
                EpisodeState.TRAINING_READY
                if data.get("curated")
                else EpisodeState.INGESTED
            )
        data["schema_version"] = SCHEMA_VERSION
    return EpisodeMeta.model_validate(data)
