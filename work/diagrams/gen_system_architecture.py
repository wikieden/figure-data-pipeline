"""生成 docs/assets/strategy/p02-data-system-architecture.svg（data-system-plan.md 的子系统架构图）。

用法：python3 work/diagrams/gen_system_architecture.py
风格与 gen_pipeline_flow.py 一致：文字与线条用 currentColor，黄色条 = 本规划新增。
"""

from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/assets/strategy/p02-data-system-architecture.svg"

W, H = 1100, 790
FONT = "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif"
GRAY = "rgba(128,136,144,0.9)"
FILL = "rgba(128,136,144,0.10)"
FILL_NEW = "rgba(237,161,0,0.10)"
NEW = "#eda100"
BLUE = "#2a78d6"

out: list[str] = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=11, anchor="start", bold=False, gray=False):
    fill = GRAY if gray else "currentColor"
    out.append(
        f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{"bold" if bold else "normal"}" fill="{fill}">{esc(s)}</text>'
    )


def box(x, y, w, h, new=False, stripe=None, dashed=False):
    f = FILL_NEW if new else FILL
    da = ' stroke-dasharray="5 4"' if dashed else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{f}" stroke="currentColor" stroke-width="1"{da}/>')
    col = NEW if new else stripe
    if col:
        out.append(f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="2" fill="{col}"/>')


def chip(x, y, w, h, s, new=False, size=10.5):
    f = FILL_NEW if new else FILL
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{f}" stroke="currentColor" stroke-width="0.8"/>')
    text(x + w / 2, y + h / 2 + size * 0.36, s, size=size, anchor="middle")


def chips_row(x0, x1, y, h, items, gap=10, size=10.5):
    n = len(items)
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, it in enumerate(items):
        label, new = (it, False) if isinstance(it, str) else it
        chip(round(x0 + i * (w + gap)), y, round(w), h, label, new=new, size=size)


def line(points, dashed=False, arrow=True, both=False, sw=1.2):
    d = " ".join(f"{'M' if i == 0 else 'L'}{px},{py}" for i, (px, py) in enumerate(points))
    da = ' stroke-dasharray="5 4"' if dashed else ""
    mk = ' marker-end="url(#arr)"' if arrow else ""
    ms = ' marker-start="url(#arr)"' if both else ""
    out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{sw}"{da}{mk}{ms}/>')


L0, L1 = 20, 186   # 左：治理 / 观测
M0, M1 = 212, 820  # 中：主流
R0, R1 = 846, 1080  # 右：任务下发 / 工作台

text(M0, 30, "数据系统：9 个子系统与接口", size=15, bold=True)
text(M0 + 210, 30, "实线 = 数据流　虚线 = 回流 / 控制　黄色 = 本规划新增或成形", size=10.5, gray=True)

# SS1 采集端
y = 48
box(M0, y, M1 - M0, 66, stripe=BLUE)
text(M0 + 16, y + 20, "SS1 采集端", size=12, bold=True)
chips_row(M0 + 16, M1 - 12, y + 30, 26, ["recorder（MCAP）", "Creator App", "遥操作站", "车队录制器", "坞站同步"])
line([((M0 + M1) / 2, y + 66), ((M0 + M1) / 2, 138)])
text((M0 + M1) / 2 + 8, y + 84, "上传（分片、断点续传）", size=10, gray=True)

# SS2 任务与规则下发（右上）
box(R0, 48, R1 - R0, 108, new=True)
text(R0 + 16, 68, "SS2 采集任务与规则下发", size=12, bold=True)
text(R0 + 16, 88, "任务库 · 规则仓 · 配额服务", size=10.5)
text(R0 + 16, 106, "collection_rule / quality_rule", size=10.5)
text(R0 + 16, 124, "下发后不可改，只发新版", size=10, gray=True)
text(R0 + 16, 142, "产出 DP7 采集任务包", size=10, gray=True)
line([(R0, 81), (M1 + 2, 81)])

# SS3 接入
y = 138
box(M0, y, M1 - M0, 56)
text(M0 + 16, y + 22, "SS3 接入", size=12, bold=True)
text(M0 + 92, y + 22, "分片上传网关 · 校验 · 跨流对时 · AV1 转码 · 幂等入湖 · 绑定规则快照哈希", size=10.5)
text(M0 + 92, y + 42, "发出 episode.ingested 等状态事件；运行时回流与外部数据集同走此入口", size=10, gray=True)

# SS4 存储（左） / SS5 处理（右）
y4 = 220
S4X1 = 400
box(M0, y4, S4X1 - M0, 214)
text(M0 + 16, y4 + 20, "SS4 存储", size=12, bold=True)
for i, s in enumerate(["对象存储 raw / curated / training", "冷热分层：raw 30 天转冷存", "PostgreSQL：元数据 + lineage", "向量库：pgvector → Milvus", "中间产物缓存（90 天）", "审计日志（写一次）"]):
    chip(M0 + 14, y4 + 32 + i * 28, S4X1 - M0 - 28, 22, s, size=10)
line([(M0 + 60, 194), (M0 + 60, y4)])
text(M0 + 68, 210, "写 raw", size=9.5, gray=True)

S5X0 = 420
box(S5X0, y4, M1 - S5X0, 214)
text(S5X0 + 16, y4 + 20, "SS5 处理", size=12, bold=True)
text(S5X0 + 90, y4 + 20, "DAG 编排 · CPU 池 · GPU 池（阶段幂等、可重放）", size=10, gray=True)
chips_row(S5X0 + 14, M1 - 12, y4 + 32, 24, ["质检", "打标", "伪标签", "去重再平衡"], gap=8)
chips_row(S5X0 + 14, M1 - 12, y4 + 62, 24, [("挖掘建索引", True), ("合成", True), ("闭环编排", True)], gap=8)
chip(S5X0 + 14, y4 + 98, round((M1 - 12 - S5X0 - 14 - 10) / 2), 46, "", new=True)
text(S5X0 + 24, y4 + 117, "模型网关（新）", size=11, bold=True)
text(S5X0 + 24, y4 + 135, "路由 · 降级 · 记账 · 分级检查", size=10)
gx = S5X0 + 14 + round((M1 - 12 - S5X0 - 14 - 10) / 2) + 10
chip(gx, y4 + 98, M1 - 12 - gx, 46, "", new=True)
text(gx + 10, y4 + 117, "模型与配置注册（新）", size=11, bold=True)
text(gx + 10, y4 + 135, "版本 · 哈希 · license · 审批", size=10)
text(S5X0 + 16, y4 + 166, "本地 VLM / 外部 API / 云托管均为网关后端；", size=10, gray=True)
text(S5X0 + 16, y4 + 182, "L3 数据只走本地后端", size=10, gray=True)
text(S5X0 + 16, y4 + 202, "产出 DP4 质检报告 · DP5 标注资产", size=10, gray=True)
line([(S4X1 + 2, y4 + 100), (S5X0 - 2, y4 + 100)], both=True)
line([(S5X0 + 200, 194), (S5X0 + 200, y4)])
text(S5X0 + 208, 210, "状态事件", size=9.5, gray=True)

# SS5 → SS2 配额（虚线）
line([(M1, y4 + 74), (R0 + 110, y4 + 74), (R0 + 110, 158)], dashed=True)
text(R0 + 118, 196, "配额：稀缺簇 /", size=10, gray=True)
text(R0 + 118, 210, "闭环缺数据", size=10, gray=True)

# SS7 工作台（右）
y7 = 300
box(R0, y7, R1 - R0, 248, new=True)
text(R0 + 16, y7 + 20, "SS7 人工作业台", size=12, bold=True)
text(R0 + 16, y7 + 38, "一个工作台、多个队列；与 SS5 双向", size=10, gray=True)
for i, q in enumerate(["标注改错", "规范裁决", "L2 尾部复核", "欺诈灰区", "金标准标注", "采集运营", "闭环复核"]):
    chip(R0 + 14, y7 + 48 + i * 26, R1 - R0 - 28, 22, q, size=10)
line([(R0 - 2, y7 + 40), (M1 + 2, y7 + 40)], both=True)

# SS6 数据服务
y6 = 460
box(M0, y6, M1 - M0, 86, new=True)
text(M0 + 16, y6 + 20, "SS6 数据服务", size=12, bold=True)
text(M0 + 112, y6 + 20, "CLI 与 API 同源；默认排除 held-out 与 reject_*；结果受 RBAC 过滤", size=10, gray=True)
svc = [("目录", "fdp catalog"), ("检索", "fdp curate --query"), ("数据集", "fdp export"), ("报告", "fdp report")]
sw_ = (M1 - 12 - M0 - 16 - 3 * 10) / 4
for i, (a, b) in enumerate(svc):
    x = round(M0 + 16 + i * (sw_ + 10))
    chip(x, y6 + 32, round(sw_), 42, "", new=(a != "数据集"))
    text(x + sw_ / 2, y6 + 50, a, size=11, anchor="middle", bold=True)
    text(x + sw_ / 2, y6 + 66, b, size=9.5, anchor="middle", gray=True)
line([((M0 + S4X1) / 2, y4 + 214), ((M0 + S4X1) / 2, y6)])
line([((S5X0 + M1) / 2, y4 + 214), ((S5X0 + M1) / 2, y6)])

# 消费端
yc = 580
cons = [("训练 fdp-policy", "读 DP1 manifest · DP2"), ("评测 eval-CI", "DP3 评测集 · DP6 反查"), ("运行时", "干预 / 失败事件"), ("对外交付", "供应商 DP4 · PL3 客户 DP1")]
cw = (M1 - M0 - 3 * 12) / 4
for i, (a, b) in enumerate(cons):
    x = round(M0 + i * (cw + 12))
    box(x, yc, round(cw), 52)
    text(x + cw / 2, yc + 22, a, size=11, anchor="middle", bold=True)
    text(x + cw / 2, yc + 40, b, size=10, anchor="middle")
    line([(round(x + cw / 2), y6 + 86), (round(x + cw / 2), yc)])
# 回流：评测 / 运行时 → 接入（左侧虚线）
x_eval = round(M0 + 1 * (cw + 12) + cw / 2)
x_rt = round(M0 + 2 * (cw + 12) + cw / 2)
line([(x_rt, yc + 52), (x_rt, yc + 70), (199, yc + 70), (199, 166), (M0 - 2, 166)], dashed=True)
line([(x_eval, yc + 52), (x_eval, yc + 70)], dashed=True, arrow=False)
text(M0 + 8, yc + 86, "消费端在系统外，本规划只定义接口；评测报告 · 车队干预 / 失败 → 回流入湖 → SS5 闭环编排", size=10, gray=True)

# 左侧：治理 / 观测
box(L0, 48, L1 - L0, 312)
text(L0 + 14, 68, "SS8 治理", size=12, bold=True)
text(L0 + 14, 84, "横跨全部子系统", size=10, gray=True)
for i, s in enumerate(["lineage（含新表）", "RBAC / SSO", "审计日志", "删除传导", "license 台账", "数据分级 L1–L3", "配额与预算"]):
    chip(L0 + 12, 96 + i * 36, L1 - L0 - 24, 28, s, size=10)
box(L0, 380, L1 - L0, 252)
text(L0 + 14, 400, "SS9 观测", size=12, bold=True)
text(L0 + 14, 416, "横跨全部子系统", size=10, gray=True)
for i, s in enumerate(["漏斗看板", "SLO 与告警", "成本记账", "loop 看板", "DP8 运营看板"]):
    chip(L0 + 12, 428 + i * 38, L1 - L0 - 24, 30, s, size=10)

# 底部：数据产品
yp = 700
text(L0, yp - 8, "数据产品（DP）", size=12, bold=True)
dps = ["DP1 训练数据集", "DP2 演示库", "DP3 评测集", "DP4 质检报告", "DP5 标注资产", "DP6 检索服务", "DP7 采集任务包", "DP8 运营看板"]
dw = (1080 - L0 - 7 * 8) / 8
for i, s in enumerate(dps):
    chip(round(L0 + i * (dw + 8)), yp, round(dw), 26, s, size=10)
text(L0, yp + 50, "详见 data-system-plan.md §2–§4；数据产品各有唯一 owner、版本规则与服务水平。SS6 的 catalog / report 子命令与工作台选型待 governance U-50 / U-51。", size=10, gray=True)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
    f'aria-label="数据系统 9 个子系统：采集端、任务与规则下发、接入、存储、处理、数据服务、人工作业台、治理、观测，以及消费端与 8 类数据产品" '
    f'font-family="{FONT}" style="max-width:100%;height:auto">'
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>'
    + "".join(out)
    + "</svg>\n"
)
OUT.write_text(svg, encoding="utf-8")
print(OUT)
