"""生成 docs/assets/strategy/p01-data-pipeline-flow.svg（data-pipeline-design.md 的全链路流程图）。

用法：python3 work/diagrams/gen_pipeline_flow.py
风格沿用 docs/assets/strategy/*.svg：文字与线条用 currentColor，轨道用色条区分。
"""

from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/assets/strategy/p01-data-pipeline-flow.svg"

W, H = 1120, 1196
FONT = "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif"
GRAY = "rgba(128,136,144,0.9)"
FILL = "rgba(128,136,144,0.10)"
FILL_NEW = "rgba(237,161,0,0.10)"
C = {"robot": "#2a78d6", "human": "#eb6834", "device": "#1baf7a", "sim": "#9aa3ad", "new": "#eda100"}

out: list[str] = []


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=11, anchor="start", bold=False, gray=False, rotate=None):
    fill = GRAY if gray else "currentColor"
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    out.append(
        f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{"bold" if bold else "normal"}" fill="{fill}"{tr}>{esc(s)}</text>'
    )


def rect(x, y, w, h, stripe=None, new=False, fill=None, dashed=False, sw=1):
    f = fill if fill is not None else (FILL_NEW if new else FILL)
    da = ' stroke-dasharray="5 4"' if dashed else ""
    out.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{f}" '
        f'stroke="currentColor" stroke-width="{sw}"{da}/>'
    )
    color = C["new"] if new and stripe is None else stripe
    if color:
        out.append(f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="2" fill="{color}"/>')


def tag(x, y, label):
    w = 10 + sum(10.2 if ord(ch) > 255 else 6.0 for ch in label)
    out.append(
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="15" rx="7.5" fill="none" '
        f'stroke="currentColor" stroke-width="0.8"/>'
    )
    text(x + w / 2, y + 11, label, size=9.5, anchor="middle")
    return x + w + 4


def line(points, dashed=False, arrow=True, sw=1.2):
    d = " ".join(f"{'M' if i == 0 else 'L'}{px},{py}" for i, (px, py) in enumerate(points))
    da = ' stroke-dasharray="5 4"' if dashed else ""
    mk = ' marker-end="url(#arr)"' if arrow else ""
    out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{sw}"{da}{mk}/>')


def chip(x, y, w, h, s, size=10.5):
    out.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{FILL}" '
        f'stroke="currentColor" stroke-width="0.8"/>'
    )
    text(x + w / 2, y + h / 2 + size * 0.36, s, size=size, anchor="middle")


def chain(x0, x1, y, h, labels, size=10.5, gap=22):
    """在 [x0, x1] 内排一行等宽 chip，chip 之间画箭头。"""
    n = len(labels)
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, s in enumerate(labels):
        cx = x0 + i * (w + gap)
        chip(round(cx), y, round(w), h, s, size)
        if i < n - 1:
            line([(round(cx + w + 2), y + h / 2), (round(cx + w + gap - 2), y + h / 2)], sw=1)


# ---------------- 画布区域 ----------------
LX0, LX1 = 20, 228  # 左：回流闭环
MX0, MX1 = 250, 890  # 中：主链路
RX = 906  # 右：合成回质检的回线
SX = 932  # 右：状态

# 标题
text(MX0, 30, "数据管线全链路流程", size=15, bold=True)
text(MX0 + 150, 30, "实线 = 数据流　虚线 = 回流 / 反馈　黄色条 = 本方案新增或补齐", size=10.5, gray=True)

# ---------------- 采集 ----------------
tracks = [
    ("robot 轨", "遥操作 · 车队回流（分档）", C["robot"]),
    ("human 轨", "第一视角 · 手机众包", C["human"]),
    ("device 轨", "UMI · 穿戴采集器", C["device"]),
    ("sim 轨", "仿真 · 生成 · 合成", C["sim"]),
]
TY, TH = 48, 56
tw = (MX1 - MX0 - 3 * 12) / 4
for i, (t1, t2, col) in enumerate(tracks):
    x = MX0 + i * (tw + 12)
    rect(round(x), TY, round(tw), TH, stripe=col)
    text(round(x + tw / 2), TY + 23, t1, size=12, anchor="middle", bold=True)
    text(round(x + tw / 2), TY + 41, t2, size=10.5, anchor="middle")
    line([(round(x + tw / 2), TY + TH), (round(x + tw / 2), 128)])
text(SX, TY + 24, "采集（MCAP，多流单文件）", size=10.5, gray=True)
text(SX, TY + 40, "配比由缩放消融裁决", size=10.5, gray=True)

# ---------------- ① 入湖 ----------------
IY, IH = 128, 52
rect(MX0, IY, MX1 - MX0, IH)
text(MX0 + 18, IY + 21, "① 入湖 ingest", size=12, bold=True)
tag(MX0 + 112, IY + 9, "M1")
text(MX0 + 18, IY + 40, "校验 · 跨流对时（ns）· AV1 + yuv420p 转码 · 幂等入湖 · 绑定采集规则快照哈希（collection_rule / quality_rule）", size=10.5)
line([((MX0 + MX1) / 2, IY + IH), ((MX0 + MX1) / 2, 204)])
text(SX, IY + 30, "raw → ingested", size=11, bold=True)

# ---------------- ② 质检 ----------------
QY, QH = 204, 122
rect(MX0, QY, MX1 - MX0, QH)
text(MX0 + 18, QY + 20, "② 质检：规则 → 语义 → 报告", size=12, bold=True)
qc = [
    ("规则段", "M1", ["完整 · 解码 · 时间戳 · 同步", "模糊 / 曝光 / 黑屏冻结 · L1 / L2"]),
    ("语义段", "M2", ["VLM 联系图粗筛 → 候选段细检", "遮挡 · 交互 · 步骤覆盖 / 顺序"]),
    ("报告段", "M2", ["合并 · 判定 · 严格校验", "quality_report · summary"]),
]
qx0, qx1, qy, qh = MX0 + 12, MX1 - 12, QY + 32, 62
qw = (qx1 - qx0 - 2 * 44) / 3
for i, (name, m, lines_) in enumerate(qc):
    x = round(qx0 + i * (qw + 44))
    out.append(f'<rect x="{x}" y="{qy}" width="{round(qw)}" height="{qh}" rx="4" fill="{FILL}" stroke="currentColor" stroke-width="0.8"/>')
    text(x + 10, qy + 17, name, size=11.5, bold=True)
    tag(x + 56, qy + 5, m)
    text(x + 10, qy + 36, lines_[0], size=10.5)
    text(x + 10, qy + 53, lines_[1], size=10.5)
    if i < 2:
        line([(x + round(qw) + 4, qy + qh / 2), (x + round(qw) + 40, qy + qh / 2)])
text(MX0 + 18, QY + QH - 10, "不过 → 标记 reject_* / flag，不删除（raw 永存）；坏样本在规则段拦截，不调用 VLM", size=10.5, gray=True)
line([((MX0 + MX1) / 2, QY + QH), ((MX0 + MX1) / 2, 348)])
text(SX, QY + 58, "→ gated / scored", size=11, bold=True)

# ---------------- ③ 打标 ----------------
AY, AH = 348, 150
rect(MX0, AY, MX1 - MX0, AH)
text(MX0 + 18, AY + 20, "③ 打标：先定边界，再写描述", size=12, bold=True)
tag(MX0 + 216, AY + 8, "M2")
text(MX0 + 18, AY + 51, "边界", size=11, bold=True)
chain(MX0 + 58, MX1 - 14, AY + 34, 28, ["信号候选", "VLM 粗分", "局部精修", "确定性后处理"])
text(MX0 + 18, AY + 93, "描述", size=11, bold=True)
chain(MX0 + 58, MX1 - 14, AY + 76, 28, ["槽位化描述", "交叉质检", "风险分级", "人工只改错"])
text(MX0 + 18, AY + 128, "伪动作：human 轨伪标签工厂 · device / robot 轨真值后处理", size=10.5)
text(MX0 + 18, AY + 143, "规范 vN ⇄ 待裁决队列 → 回写规范、离线重映射；按用途出标注档案（动作专家 / 规划器 / 预训练）", size=10.5, gray=True)
line([((MX0 + MX1) / 2, AY + AH), ((MX0 + MX1) / 2, 522)])
text(SX, AY + 78, "→ segmented / labeled", size=11, bold=True)

# ---------------- ④ 去重再平衡 ----------------
DY, DH = 522, 44
rect(MX0, DY, MX1 - MX0, DH)
text(MX0 + 18, DY + 27, "④ 去重 · 再平衡", size=12, bold=True)
tag(MX0 + 122, DY + 15, "M2")
text(MX0 + 162, DY + 27, "近重复保留最优 · 语义重复降权 · 四轴聚类（任务 / 物体 / 环境 / 操作者）· 稀缺簇 → 补数需求", size=10.5)

# ---------------- ⑤ 挖掘 / ⑥ 合成 ----------------
RY, RH = 590, 122
M5X1 = 650
S6X0 = 674
rect(MX0, RY, M5X1 - MX0, RH, new=True)
text(MX0 + 18, RY + 21, "⑤ 挖掘（新）", size=12, bold=True)
nx = tag(MX0 + 108, RY + 9, "检索底座 M2")
tag(nx, RY + 9, "闭环 M3")
text(MX0 + 18, RY + 46, "结构化过滤 → embedding 召回 → rerank 精排", size=10.5)
text(MX0 + 18, RY + 66, "查询 = 版本化配置，结果快照进 manifest", size=10.5)
text(MX0 + 18, RY + 86, "用途：演示库 · 难例长尾 · 技能盘点 · 失败反查", size=10.5)
text(MX0 + 18, RY + 106, "验收：成对难查询（方向 / 左右手 / 成败）", size=10.5, gray=True)
line([((MX0 + M5X1) / 2, DY + DH), ((MX0 + M5X1) / 2, RY)])
text((MX0 + M5X1) / 2 + 8, DY + DH + 16, "策展池 · 稀缺簇", size=10, gray=True)

rect(S6X0, RY, MX1 - S6X0, RH, new=True)
text(S6X0 + 18, RY + 21, "⑥ 合成", size=12, bold=True)
tag(S6X0 + 66, RY + 9, "M3")
text(S6X0 + 18, RY + 46, "sim 增殖 · 具身转换", size=10.5)
text(S6X0 + 18, RY + 66, "人类视频 → 机器人演示（新）", size=10.5)
text(S6X0 + 18, RY + 86, "世界模型生成（准入后）", size=10.5)
text(S6X0 + 18, RY + 106, "派生 episode，带 parent id", size=10.5, gray=True)
line([(M5X1 + 2, RY + 50), (S6X0 - 2, RY + 50)])
text((M5X1 + S6X0) / 2, RY + 40, "缺口", size=9.5, anchor="middle", gray=True)

# 合成产物回到质检（右侧回线）
line([(MX1, RY + 70), (RX, RY + 70), (RX, QY + 92), (MX1 + 2, QY + 92)], dashed=True)
text(RX + 12, (RY + 70 + QY + 92) / 2 + 30, "合成产物回 ② 质检（合成专属 QC）", size=10.5, anchor="middle", gray=True, rotate=-90)

# ---------------- ⑦ 数据集构建 ----------------
EY, EH = 736, 66
line([((MX0 + M5X1) / 2, RY + RH), ((MX0 + M5X1) / 2, EY)])
text((MX0 + M5X1) / 2 + 8, RY + RH + 16, "策展池 + 查询快照", size=10, gray=True)
rect(MX0, EY, MX1 - MX0, EH)
text(MX0 + 18, EY + 20, "⑦ 数据集构建 export", size=12, bold=True)
tag(MX0 + 156, EY + 8, "M1–M2")
chain(MX0 + 18, MX1 - 14, EY + 30, 26, ["可训练性检查", "配方 + 查询快照 + 标注档案", "冻结 manifest", "LeRobot v3 · 演示库切片"], gap=20)
line([((MX0 + MX1) / 2, EY + EH), ((MX0 + MX1) / 2, 826)])
text(SX, EY + 38, "→ training_ready", size=11, bold=True)

# ---------------- ⑧ 训练评测 ----------------
TY8, TH8 = 826, 48
rect(MX0, TY8, MX1 - MX0, TH8)
text(MX0 + 18, TY8 + 29, "⑧ 训练 · 评测", size=12, bold=True)
tag(MX0 + 108, TY8 + 17, "M3")
text(MX0 + 148, TY8 + 29, "fdp-policy 配方消融 · eval-protocol 统计判定 · held-out 入湖即固定，合成数据不进评测集", size=10.5)

# ---------------- ⑩ 渐进式自主 ----------------
Y10, H10 = 898, 118
RX10 = 1098  # 右：档位产出回入湖的回线
line([((MX0 + MX1) / 2, TY8 + TH8), ((MX0 + MX1) / 2, Y10)])
text((MX0 + MX1) / 2 + 8, TY8 + TH8 + 16, "checkpoint + 统计判定", size=10, gray=True)
rect(MX0, Y10, MX1 - MX0, H10, new=True)
text(MX0 + 18, Y10 + 20, "⑩ 渐进式自主（新）", size=12, bold=True)
tag(MX0 + 152, Y10 + 8, "M3")
text(MX0 + 196, Y10 + 20, "按 任务簇 × 站点 定档；新任务 / 新站点 / 新本体从 T0 起", size=10.5, gray=True)
tiers = ["T0 全遥操 · 演示", "T1 共享 · 干预段", "T2 全自主 · rollout"]
tx0, tx1, ty, th, tgap = MX0 + 18, MX1 - 14, Y10 + 32, 30, 74
tcw = (tx1 - tx0 - tgap * 2) / 3
for i, s_ in enumerate(tiers):
    cx = round(tx0 + i * (tcw + tgap))
    chip(cx, ty, round(tcw), th, s_, size=11)
    out.append(f'<rect x="{cx}" y="{ty}" width="4" height="{th}" rx="1.5" fill="{C["robot"]}"/>')
    if i < 2:
        ax0, ax1 = cx + round(tcw) + 4, cx + round(tcw) + tgap - 4
        line([(ax0, ty + 9), (ax1, ty + 9)])
        text((ax0 + ax1) / 2, ty + 4, "晋档", size=9.5, anchor="middle", gray=True)
        line([(ax1, ty + 22), (ax0, ty + 22)], dashed=True)
        text((ax0 + ax1) / 2, ty + 38, "降档", size=9.5, anchor="middle", gray=True)
text(MX0 + 18, Y10 + 88, "晋档：⑧ 统计判定通过 + 干预率连续 N 周低于档线 + 部署检查单　降档：接管率周环比 >30% 或成功率跌破阈值", size=10.5)
text(MX0 + 18, Y10 + 107, "episode 带 autonomy_tier / by / policy_version；干预段固化 [−30 s, +60 s] 优先上传；干预率为内部 KPI，不对外", size=10.5, gray=True)
# 各档产出经 robot 轨回 ① 入湖（右侧回线）
line([(MX1, Y10 + 24), (RX10, Y10 + 24), (RX10, IY + 44), (MX1 + 2, IY + 44)], dashed=True)
text(RX10 + 12, (Y10 + IY) / 2 + 40, "各档产出（演示 / 干预段 / rollout）经 robot 轨回 ① 入湖", size=10.5, anchor="middle", gray=True, rotate=-90)
text(SX, Y10 + 52, "→ autonomy_tier 定档", size=11, bold=True)

# ---------------- ⑨ 回流闭环（左列） ----------------
rect(LX0, TY, LX1 - LX0, TY8 + TH8 - TY, new=True, dashed=True)
text(LX0 + 16, TY + 20, "⑨ 回流闭环（新 · M3）", size=12, bold=True)

BX0, BX1 = 44, 216
SPINE = 31


def lbox(y, h, l1, l2, gray2=False):
    out.append(f'<rect x="{BX0}" y="{y}" width="{BX1 - BX0}" height="{h}" rx="4" fill="{FILL}" stroke="currentColor" stroke-width="0.8"/>')
    text(BX0 + 8, y + 17, l1, size=10.5, bold=True)
    if l2:
        text(BX0 + 8, y + 34, l2, size=10, gray=gray2)


# 自下而上的三步
lbox(TY8 + 2, 44, "触发", "评测失败 · 干预 / OOD · 降档")
lbox(778, 40, "失败归类", "失败模式词表")
lbox(730, 40, "调用 ⑤ 挖掘反查训练集", "诊断：缺数据 / 被过滤 / 标错")
line([(MX0, TY8 + 24), (BX1 + 2, TY8 + 24)])
line([(130, TY8 + 2), (130, 820)])
line([(130, 778), (130, 772)])

# 诊断出口（脊线 + 分支）
line([(BX0, 750), (SPINE, 750), (SPINE, 100)], arrow=False)
branches = [
    (80, "缺数据 → 采集配额", "带 collection_rule 下发", (MX0, 98)),
    (244, "被过滤 → 阈值消融", "走消融，不直接改阈值", (MX0, 266)),
    (404, "标错 → 规范待裁决", "回写规范 + 离线重映射", (MX0, 426)),
    (606, "缺数据 → 相似样本 / 合成种子", "", (MX0, 628)),
]
for y, l1, l2, (tx, ty) in branches:
    lbox(y, 44 if l2 else 40, l1, l2)
    line([(SPINE, y + 20), (BX0 - 2, y + 20)])
    line([(BX1, ty), (tx - 2, ty)], dashed=True)
text(BX0 + 8, 690, "每轮写 loop 记录；新数据集", size=10, gray=True)
text(BX0 + 8, 705, "版本再评测，不涨即回退", size=10, gray=True)

# ---------------- 横切能力 ----------------
CY = 1046
text(LX0, CY - 8, "横切能力（贯穿全部环节）", size=12, bold=True)
cross = [
    ("lineage", ["decisions · artifacts · qc_reports", "queries · loops · datasets"]),
    ("版本化配置", ["qc / annotation / queries", "synthesis / mixtures（改即新版本）"]),
    ("评测尺子", ["质检漏斗 · 边界两把尺子", "检索基准 · 合成消融 · 闭环前后"]),
    ("人在环", ["五个人工触点", "从零标 → 只改错 → 只看高风险"]),
    ("合规", ["脱敏 · 授权 · 模型 license", "闭源合成按 R-27 处理"]),
]
cw = (1080 - LX0 - 4 * 12) / 5
for i, (t, ls) in enumerate(cross):
    x = round(LX0 + i * (cw + 12))
    rect(x, CY, round(cw), 70)
    text(x + 14, CY + 21, t, size=11.5, bold=True)
    text(x + 14, CY + 41, ls[0], size=10)
    text(x + 14, CY + 57, ls[1], size=10)

# ---------------- 图例 ----------------
LY = 1150
lx = LX0
for name, col in [("robot", C["robot"]), ("human", C["human"]), ("device", C["device"]), ("sim", C["sim"]), ("新增 / 补齐", C["new"])]:
    out.append(f'<rect x="{lx}" y="{LY}" width="10" height="10" rx="2" fill="{col}"/>')
    text(lx + 15, LY + 9, name, size=10.5)
    lx += 30 + 7 * len(name) + (20 if not name.isascii() else 0)
tag(lx + 10, LY - 3, "M1")
text(lx + 38, LY + 9, "里程碑（M1 采集与格式 · M2 策展 · M3 训练与闭环）", size=10.5)
text(LX0, LY + 32, "详见 data-pipeline-design.md §1–§12（⑩ 见 §9.4）；新模块、CLI 与档位门槛为提议，待 governance U-47 / U-48 / U-52 裁决。", size=10.5, gray=True)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
    f'aria-label="数据管线全链路流程：采集四轨 → 入湖 → 质检 → 打标 → 去重再平衡 → 挖掘与合成 → 数据集构建 → 训练评测，下方为渐进式自主分档，左侧为回流闭环，底部为横切能力" '
    f'font-family="{FONT}" style="max-width:100%;height:auto">'
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>'
    + "".join(out)
    + "</svg>\n"
)
OUT.write_text(svg, encoding="utf-8")
print(OUT)
