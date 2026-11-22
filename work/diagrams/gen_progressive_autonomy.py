"""生成 docs/assets/strategy/p03-progressive-autonomy.svg（data-pipeline-design.md §9.4 的渐进式自主图）。

用法：python3 work/diagrams/gen_progressive_autonomy.py
风格沿用 gen_pipeline_flow.py：文字与线条用 currentColor，轨道用色条区分，黄色 = 本方案新增（提议）。
"""

from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/assets/strategy/p03-progressive-autonomy.svg"

W, H = 1124, 846
FONT = "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif"
GRAY = "rgba(128,136,144,0.9)"
FILL = "rgba(128,136,144,0.10)"
FILL_NEW = "rgba(237,161,0,0.10)"
C = {"robot": "#2a78d6", "new": "#eda100"}

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


def rect(x, y, w, h, stripe=None, new=False, dashed=False, sw=1):
    f = FILL_NEW if new else FILL
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


def chip(x, y, w, h, s, size=10.5, sub=None):
    out.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{FILL}" '
        f'stroke="currentColor" stroke-width="0.8"/>'
    )
    if sub is None:
        text(x + w / 2, y + h / 2 + size * 0.36, s, size=size, anchor="middle")
    else:
        text(x + w / 2, y + h / 2 - 3, s, size=size, anchor="middle", bold=True)
        text(x + w / 2, y + h / 2 + 13, sub, size=9.5, anchor="middle", gray=True)


def chain(x0, x1, y, h, labels, size=10.5, gap=22):
    n = len(labels)
    w = (x1 - x0 - gap * (n - 1)) / n
    xs = []
    for i, lab in enumerate(labels):
        cx = x0 + i * (w + gap)
        s, sub = lab if isinstance(lab, tuple) else (lab, None)
        chip(round(cx), y, round(w), h, s, size, sub)
        xs.append((round(cx), round(cx + w)))
        if i < n - 1:
            line([(round(cx + w + 2), y + h / 2), (round(cx + w + gap - 2), y + h / 2)], sw=1)
    return xs


X0, X1 = 20, 1090
MID = (X0 + X1) / 2
RX = 1104  # 右：定档回到档位的回线

# 标题
text(X0, 30, "渐进式自主：档位、晋降档与数据回流", size=15, bold=True)
text(X0 + 262, 30, "实线 = 数据流 / 晋档　虚线 = 降档 / 回流　黄色 = 本方案新增（提议）", size=10.5, gray=True)

# ---------------- A. 三档 ----------------
AY, AH = 50, 186
CW, GAP = 300, 85
tiers = [
    ("T0 全遥操", "人做，机器记", "M1", False, [
        ("控制", "操作员全程（D4 遥操作站 / 远程）"),
        ("人的角色", "示教"),
        ("产出", "演示 episode（动作真值）"),
        ("训练用途", "对齐集 · BC 后训练"),
        ("上传", "全量"),
    ]),
    ("T1 共享自主", "机器做，人随时接", "M3", True, [
        ("控制", "策略执行，人实时监看"),
        ("人的角色", "OOD 二级 / 主动接管（by 本地或远程）"),
        ("产出", "干预段（接管前 30 s / 后 60 s）"),
        ("训练用途", "DAgger · RECAP · 残差 RL"),
        ("上传", "干预段 100%，回坞优先"),
    ]),
    ("T2 全自主", "机器做，人抽检", "M3", True, [
        ("控制", "策略独立运行"),
        ("人的角色", "抽检 · 远程待命"),
        ("产出", "自主 rollout + 成败 + OOD 事件"),
        ("训练用途", "车队 RL · 成败条件化 · 负样本"),
        ("上传", "失败 / OOD 优先，成功抽样 20%"),
    ]),
]
for i, (name, sub, m, new, rows) in enumerate(tiers):
    x = X0 + i * (CW + GAP)
    rect(x, AY, CW, AH, stripe=C["robot"], new=new)
    text(x + 18, AY + 24, name, size=13, bold=True)
    nx = x + 18 + 13.5 * len(name.replace(" ", "")) - (6 if name[1].isdigit() else 0)
    tag(round(nx), AY + 12, m)
    text(x + 18, AY + 43, sub, size=10.5, gray=True)
    for j, (k, v) in enumerate(rows):
        yy = AY + 72 + j * 25
        text(x + 18, yy, k, size=10.5, gray=True)
        text(x + 82, yy, v, size=10.5)
    if i < 2:
        ax0, ax1 = x + CW + 4, x + CW + GAP - 4
        line([(ax0, AY + 74), (ax1, AY + 74)])
        text((ax0 + ax1) / 2, AY + 66, "晋档", size=10, anchor="middle", gray=True)
        line([(ax1, AY + 112), (ax0, AY + 112)], dashed=True)
        text((ax0 + ax1) / 2, AY + 130, "降档", size=10, anchor="middle", gray=True)

# ---------------- C. 单次运行 ----------------
CY_, CH = 262, 96
line([(MID, AY + AH), (MID, CY_)])
text(MID + 8, AY + AH + 17, "每档运行都全程录制（D5 车队回流录制器）", size=10, gray=True)
rect(X0, CY_, X1 - X0, CH)
text(X0 + 18, CY_ + 20, "单次运行（T1 / T2 部署；T0 全量录制直接入湖）", size=12, bold=True)
tag(X0 + 330, CY_ + 8, "M3")
chain(X0 + 18, X1 - 14, CY_ + 32, 30, [
    "策略执行（PolicyServer）",
    "OOD 探针 10 Hz 越阈",
    "处置：放慢 / 接管 / estop",
    "固化 [−30 s, +60 s] 窗口",
    "回坞按优先级上传",
])
text(X0 + 18, CY_ + 84, "所有 OOD 事件与接管对齐到 episode 时间轴（/event/ood、/event/intervention）；家庭部署机上脱敏后帧才出机", size=10.5, gray=True)

# ---------------- D. 进入数据管线 ----------------
DY, DH = 384, 112
line([(MID, CY_ + CH), (MID, DY)])
rect(X0, DY, X1 - X0, DH)
text(X0 + 18, DY + 20, "进入数据管线（编号与图 P1 对应）", size=12, bold=True)
xs = chain(X0 + 18, X1 - 14, DY + 32, 44, [
    ("① 入湖", "source=fleet · 档位 · 策略版本"),
    ("②③ 质检 · 打标", "干预段切分 · 接管 / 恢复标记"),
    ("⑦ 配方", "conditioning 加 档位 / 成败"),
    ("⑧ 训练 · 评测", "DAgger / RECAP · 统计判定"),
    ("定档", "晋档 / 保持 / 降档 · 写 lineage"),
])
text(X0 + 18, DY + 98, "降档同时触发 ⑨ 回流闭环：失败归类 → 挖掘反查 → 采集配额 / 阈值消融 / 规范待裁决", size=10.5, gray=True)

# 定档 → 新档位生效（右侧回线回到 T2 列）
line([(X1, DY + 54), (RX, DY + 54), (RX, AY + 93), (X1 + 2, AY + 93)], dashed=True)
text(RX + 12, (DY + 54 + AY + 93) / 2, "新 checkpoint + 档位决定 → 部署", size=10.5, anchor="middle", gray=True, rotate=-90)

# ---------------- B. 晋降档门 ----------------
BY, BH = 522, 136
line([(MID, DY + DH), (MID, BY)])
text(MID + 8, DY + DH + 17, "定档依据", size=10, gray=True)
BW = (X1 - X0 - 14) / 2
rect(X0, BY, round(BW), BH, new=True)
text(X0 + 18, BY + 22, "晋档门（每档一道，按 任务簇 × 站点 判）", size=12, bold=True)
for j, s in enumerate([
    "1. ⑧ 评测统计判定通过（序贯检验 / Wilson 下界；档线待定）",
    "2. 干预率（每 1,000 任务）连续 N 周低于档线",
    "3. 部署检查单：延迟预算 · 安全过滤器 · OOD 阈值来自当前 dataset_version",
    "4. 新 checkpoint 先在 T1 复核，不直接继承上一版的档位",
]):
    text(X0 + 18, BY + 48 + j * 22, s, size=10.5)

bx = round(X0 + BW + 14)
rect(bx, BY, round(X1 - bx), BH, new=True)
text(bx + 18, BY + 22, "降档与临时接管", size=12, bold=True)
for j, s in enumerate([
    "临时接管（不降档）：OOD 二级 → 请求人工接管；三级 → estop",
    "降一档：接管率周环比 >30% 或任务簇成功率跌破阈值",
    "降档同时开 Stage D 后训练 run，并写一条 ⑨ loop 记录",
    "新任务 / 新站点 / 新本体：一律从 T0 起",
]):
    text(bx + 18, BY + 48 + j * 22, s, size=10.5)

# ---------------- E. 约束 ----------------
EY = 696
text(X0, EY - 8, "约束（贯穿全部档位）", size=12, bold=True)
cons = [
    ("对外口径", ["干预率是内部 KPI，不对外宣称", "对外宣称附可复现日志（R-03）"]),
    ("安全", ["ISO 10218 / TS 15066 / 13482 基线", "安全过滤器 · 心跳丢失 200 ms 停机"]),
    ("隐私", ["家庭部署机上脱敏 · 禁入区", "远程接管在场披露"]),
    ("lineage", ["policy_version · deployment_id", "每次定档写决策记录"]),
]
ew = (X1 - X0 - 3 * 12) / 4
for i, (t, ls) in enumerate(cons):
    x = round(X0 + i * (ew + 12))
    rect(x, EY, round(ew), 70)
    text(x + 14, EY + 21, t, size=11.5, bold=True)
    text(x + 14, EY + 41, ls[0], size=10)
    text(x + 14, EY + 57, ls[1], size=10)

# ---------------- 图例 ----------------
LY = 790
out.append(f'<rect x="{X0}" y="{LY}" width="10" height="10" rx="2" fill="{C["robot"]}"/>')
text(X0 + 15, LY + 9, "robot 轨", size=10.5)
out.append(f'<rect x="{X0 + 80}" y="{LY}" width="10" height="10" rx="2" fill="{C["new"]}"/>')
text(X0 + 95, LY + 9, "新增（提议）", size=10.5)
tag(X0 + 190, LY - 3, "M3")
text(X0 + 222, LY + 9, "里程碑（M1 采集与格式 · M3 训练与闭环）", size=10.5)
text(X0, LY + 32, "详见 data-pipeline-design.md §9.4。三档划分沿用 1X 三档自主（官方）；档线、N 与门槛为提议，待 governance U-52 裁决。", size=10.5, gray=True)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
    f'aria-label="渐进式自主：T0 全遥操、T1 共享自主、T2 全自主三档，各档产出经单次运行录制进入数据管线，训练评测后按晋降档门定档并回到部署" '
    f'font-family="{FONT}" style="max-width:100%;height:auto">'
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>'
    + "".join(out)
    + "</svg>\n"
)
OUT.write_text(svg, encoding="utf-8")
print(OUT)
