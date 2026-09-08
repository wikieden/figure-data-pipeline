import json
from pathlib import Path

import pytest

from fdp.schema import (
    SCHEMA_VERSION,
    EpisodeMeta,
    EpisodeState,
    SignalStream,
    Subtask,
    Track,
    migrate,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_episode_meta_minimal():
    ep = EpisodeMeta(
        episode_id="ep_0001", track=Track.HUMAN, started_at_ns=0, duration_ns=1
    )
    assert ep.robot_model is None
    assert not ep.curated
    assert ep.state is EpisodeState.RAW
    assert ep.schema_version == SCHEMA_VERSION


def test_track_values():
    assert {t.value for t in Track} == {"robot", "human", "device", "sim"}


def test_rl_and_slot_fields_default():
    ep = EpisodeMeta(
        episode_id="ep_0002", track=Track.DEVICE, started_at_ns=0, duration_ns=1
    )
    assert ep.success is None
    assert ep.intervention_ts_ns == []
    s = SignalStream(name="ee_pose", rate_hz=60, dim=9, slot="ee_pose_right")
    assert s.slot == "ee_pose_right"


def test_migrate_v0_1_fixture():
    raw = json.loads((FIXTURES / "episode_v0_1.json").read_text())
    ep = migrate(raw)
    assert ep.schema_version == SCHEMA_VERSION
    assert ep.track is Track.DEVICE
    assert [s.instruction for s in ep.subtasks] == raw["subtask_instructions"]
    assert all(s.start_ns is None for s in ep.subtasks)
    assert ep.state is EpisodeState.TRAINING_READY  # curated=True 推断
    assert ep.signals[0].rate_hz == 60.0  # device 轨原生频率原样保留
    assert ep.quality_flags == ["flag:slam_lost_short"]


def test_migrate_current_version_roundtrip():
    ep = EpisodeMeta(
        episode_id="ep_0003",
        track=Track.ROBOT,
        session_id="s1",
        robot_model="fdp-h1",
        started_at_ns=0,
        duration_ns=10,
        subtasks=[Subtask(instruction="reach", start_ns=0, end_ns=5)],
        state=EpisodeState.GATED,
        content_hash="blake3:abc",
    )
    again = migrate(json.loads(ep.model_dump_json()))
    assert again == ep


def test_migrate_rejects_unknown_version():
    with pytest.raises(ValueError):
        migrate({"schema_version": "9.9", "episode_id": "x", "track": "sim"})


def test_unknown_keys_are_ignored_for_forward_compat():
    ep = migrate(
        {
            "schema_version": "0.2",
            "episode_id": "ep_future",
            "track": "sim",
            "started_at_ns": 0,
            "duration_ns": 1,
            "some_future_field": 42,
        }
    )
    assert ep.episode_id == "ep_future"
