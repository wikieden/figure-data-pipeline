from fdp.schema import EpisodeMeta, Track


def test_episode_meta_minimal():
    ep = EpisodeMeta(episode_id="ep_0001", track=Track.HUMAN, started_at_ns=0, duration_ns=1)
    assert ep.robot_model is None
    assert not ep.curated


def test_track_values():
    assert {t.value for t in Track} == {"robot", "human", "device", "sim"}


def test_rl_and_slot_fields_default():
    from fdp.schema import EpisodeMeta, SignalStream, Track

    ep = EpisodeMeta(episode_id="ep_0002", track=Track.DEVICE, started_at_ns=0, duration_ns=1)
    assert ep.success is None
    assert ep.intervention_ts_ns == []
    s = SignalStream(name="ee_pose", rate_hz=60, dim=9, slot="ee_pose")
    assert s.slot == "ee_pose"
