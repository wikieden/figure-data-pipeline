# 具身档案（docs/robot-track-teleop.md §1）：关节顺序、限位、相机映射、槽位映射，是 export 与训练的共同输入。
# 相机项（2026-11-18 起要求）：新版档案的 cameras.<name> 需含 mount（相对腕法兰/头部基座的外参、安装件零件号、视场、标定 ref），作为采集器与遥操支架的共同基准（docs/capture-devices-design.md §1.2）；v1 不回填。
# 改动 = 新版本文件（`_v2.yaml`），不覆盖旧文件；文件哈希随 episode 的 calibration_ref / lineage 记录。
