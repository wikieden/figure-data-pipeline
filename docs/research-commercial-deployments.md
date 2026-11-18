# 已调研厂商的商用落地案例：酒店洗衣房、餐厅厨房及其他（2026-10-09）

[F:bmw]: sources/figure/production-at-bmw.txt
[F:f03-bmw]: sources/figure/f-03-at-bmw.txt
[F:logistics]: sources/figure/helix-logistics.txt
[F:scaling-logistics]: sources/figure/scaling-helix-logistics.txt
[F:ramping]: sources/figure/ramping-figure-03-production.txt
[F:f03]: sources/figure/introducing-figure-03.txt
[D:dyna-1]: sources/dyna/dyna-1.txt
[D:dyna-2]: sources/dyna/dyna-2.txt
[D:owd]: sources/dyna/open-world-dexterity.txt
[D:product]: sources/dyna/scaling-customer-deployments.txt
[D:home]: sources/dyna/home.txt
[K:arr]: sources/skild/skild-crosses-100m-arr.txt
[K:series-c]: sources/skild/series-c.txt
[K:oem]: sources/skild/reindustrial-revolution.txt
[K:zebra]: sources/skild/skild-zebra.txt
[S:series-b]: sources/sunday/series-b.txt
[S:act-2]: sources/sunday/act-2-preview.txt
[G:funding]: sources/generalist/accelerating-the-next-phase-of-physical-ai.txt
[G:hands]: sources/generalist/towards-machines-with-a-thousand-hands.txt

> 范围：本仓库已调研的五家（Figure、Dyna、Skild、Sunday、Generalist），外加 [data-strategy-roadmap.md](data-strategy-roadmap.md) §1 顺带登记过的 Agility、1X、Apptronik。只用仓库内已归档的一手页面（[sources/MANIFEST.md](sources/MANIFEST.md)，抓取于 2026-09-14/16）和已有 research 文档里登记过的第三方条目，本次没有新抓取。来源属性：**官方** = 公司一手页面；**第三方** = 媒体或社交转述；**自报 ⚠️** = 公司自己给的业务数字、无独立核实。
>
> "落地"分三档：**规模部署**（多站点、付费、已在铺开）＞ **付费试点 / 单站生产**（有名有姓的客户、在真实产线或门店运行）＞ **演示 / 计划**（实验室或展会、或只说"将要"）。

## 0. 结论

| 场景 | 有案例的厂商 | 最强证据 | 档位 |
|---|---|---|---|
| **餐厅（前厅布草：叠餐巾）** | **Dyna** | 鼎泰丰在美门店网络铺开 Dyna 机器人，每机 18 h 班次 1,590 条合格餐巾 [D:product] | 规模部署（官方，数字自报 ⚠️） |
| **餐厅后厨 / 商用厨房** | **Skild**、Dyna | Skild 与三井物产在日本商用厨房试点 S1 [K:arr]；Dyna 首页列"餐饮：收餐盆→预刮、分拣、上碗架"180 件/h [D:home]，一手页面未给后厨客户名 | 试点（Skild，官方）；产品口径（Dyna，自报 ⚠️） |
| **洗衣房（毛巾/布草/衣物）** | **Dyna**；Figure、Sunday 只有演示 | Dyna 首页"烘干机到可交付"100 件/h、≥98% 可交付，覆盖手巾、浴巾、泳池巾、服装 [D:home]；客户 Monster Laundry（Sacramento）3 个月叠 20 万+ 条毛巾 | 单站生产（Monster Laundry 为第三方转述 ⚠️） |
| **酒店** | **Dyna**（只有一句） | "rollouts across hotels, logistics companies, and data centers (more on those soon)" [D:product]；无客户名、无数字 | 已宣布、未披露细节 |
| 汽车工厂 | Figure | BMW Spartanburg：F.02 11 个月、3 万台 X3 [F:bmw]；F.03 转排序工位 [F:f03-bmw] | 单站生产（官方） |
| 电子装配 | Skild | Foxconn 产线装 NVIDIA Blackwell [K:oem][K:arr] | 部署中（官方） |
| 仓储物流 | Skild、Figure、Agility | Skild 收购 Zebra（前 Fetch）[K:zebra]；Figure 物流包裹分拣 [F:logistics]；Agility 9 站点 | 见 §2 |
| 家庭 | Sunday、1X、Figure | Sunday Beta 2026 秋 [S:series-b]；1X NEO 以遥操作为主 | 演示 / Beta 计划 |

**一句话**：酒店洗衣房和餐厅这两个场景，五家里**只有 Dyna 有可指名的商用客户**（鼎泰丰、Monster Laundry），而且是叠餐巾/叠毛巾这类**台面布草活**，不是"洗→烘→叠"全流程；**Skild** 是唯一在商用后厨有指名试点的（三井物产，日本）。Figure 的叠衣、装洗碗机和 Sunday 的叠衣都是实验室或样板间演示，没有商用客户。Generalist 没有公开任何商用部署。

## 1. 酒店洗衣房 / 餐厅厨房：逐家

### 1.1 Dyna Robotics：唯一在两个场景都有付费客户的

| 时间 | 事件 | 来源 · 属性 |
|---|---|---|
| 2025-06-24 | DYNA-1 发布："battle-tested to upscale-restaurant standards"，24 h 连续叠 850+ 条餐巾，约人类 60% 速度，99.4% 成功率、零干预；并称"now folds napkins for paying customers"，按客户要求做了配料杯分装（cup-filling） | [D:dyna-1] · 官方，数字自报 ⚠️ |
| 2025-06-24 | 同页：在"unseen customer environment"开箱可叠，现场少量学习后在"a real restaurant site"连续叠 | [D:dyna-1] · 官方 |
| 2025-10 前后 | 官网有一篇 "Customer Testimonial: Monster Laundry"（open-world-dexterity 页的上一篇链接）；第三方转述：Sacramento 洗衣店 Monster Laundry，3 个月叠 20 万+ 条毛巾、10 个客户，单机每天运行 16 h | [D:owd] 仅有标题；数字见 [research-dyna-comparison.md](research-dyna-comparison.md) §1 · 第三方 ⚠️（客户证言页**未归档**） |
| 2026-04 | Red Bull Mirage（Coachella）活动 8 h 700+ 杯 | 同上 · 第三方 ⚠️ |
| 2026-08-15 | DYNA-2：同一后训练预算下，客户现场按客户验收标准、由非开发人员评分，DYNA-1 通过 46%、DYNA-2 通过 87%（内部评测两者都接近 100%） | [D:dyna-2] · 官方，数字自报 ⚠️ |
| 2026-08-27 | **鼎泰丰**："our robots have successfully crossed the ROI threshold, and Din Tai Fung … is rolling out Dyna's robots across its restaurant network" | [D:product] · 官方 |
| 2026-08-27 | 鼎泰丰的指标：每机 18 h 班次需 1,500 条可上桌餐巾；DYNA-1 上线时约 35 条/h、合格 75%、日产约 480；DYNA-2 现为 95 条/h、合格 93%、日产 1,590；叠好后按指令放进 5 格或 10 格餐巾盒的指定位置 | [D:product] · 官方，数字自报 ⚠️ |
| 2026-08-27 | 某鼎泰丰门店吞吐下滑，靠自动标签定位到 SOP 第 1 步（从一叠中抽单张）漏抓翻倍；新站点"从安装到达到生产 ROI 线最短 3 天"；车队 2027 上半年到数百台；酒店、物流、数据中心在铺开（"more on those soon"） | [D:product] · 官方，自报 ⚠️ |
| 2026-09-16 归档 | 官网 "Deployments" 三栏产品口径：**洗衣与服装**（烘干机→叠、堆、装袋，100 件/h，无需预分拣，≥98% 可交付，覆盖手巾/浴巾/泳池巾/服装，含缠绕、潮湿、起皱输入）；**餐饮与酒店**（收餐盆→预刮、分拣、上碗架，180 件/h，每盆 <90 s，覆盖盘、玻璃器皿、餐具）；**工厂与装配**（200 件/h，±2 mm） | [D:home] · 官方，自报 ⚠️ |

判读：

- **酒店洗衣房最接近的公开案例是 Monster Laundry**（商业洗衣店，不是酒店自营洗衣房），而且一手证言页没有归档，数字只能当第三方。官网"hospitality-grade fold""pool"字样说明他们瞄准酒店布草，但没给酒店客户名。
- **餐厅案例是前厅布草（餐巾），不是后厨烹饪**。官网的"bus tub → rack"是洗碗间前段（预刮、分拣、上架），没有一手页面说明哪个客户在用。
- 机器人是固定双臂 + 平行夹爪，工作台高度，不移动（[research-end-effector-torso.md](research-end-effector-torso.md) §2）。对应我们洗衣房方案里"叠"这一段，不覆盖装洗衣机、搬运。

### 1.2 Skild AI：商用厨房试点

| 时间 | 事件 | 来源 · 属性 |
|---|---|---|
| 2026-01-14 | 部署行业：安保、建筑、配送、数据中心、仓储、工厂装配；2025 年几个月内收入从 0 到约 $30M | [K:series-c] · 官方，自报 ⚠️ |
| 2026-03-19 | 分阶段部署观：先半结构化（工厂）→ 医院、酒店 → 家庭。酒店是**计划中的第二阶段**，不是已有案例 | [K:oem] · 官方 |
| 2026-09-10 | ARR 破 $100M（首次商用部署后 10 个月），60+ 付费客户，行业含"preparing food"；**与三井物产（日本供餐链每天 140 万份）在商用厨房试点 S1 驱动的通用机器人**；住友电装线束；Foxconn/NVIDIA Blackwell 装配 | [K:arr] · 官方，ARR 自报 ⚠️ |

判读：Skild 的厨房案例是**试点**（"piloting"），一手页面没给任务内容、台数或成功率。"preparing food"作为 60+ 客户的行业之一出现，具体客户未列。

### 1.3 Figure：洗衣、厨房只有家庭场景演示

- 2025-08 叠毛巾、2025-09 装洗碗机、2026 Helix 02 客厅/卧室整理，全部是 Figure 自己的样板环境演示，无客户（[research-four-routes.md](research-four-routes.md) §1）。
- Figure 03 发布页称"designed for … the home"，商用侧只讲可定制制服、侧屏标识、无线充电近连续运行 [F:f03]；BotQ 出厂机器人分给研发、采数、端到端家务、商用用例四类 [F:ramping]。没有酒店或餐厅客户。

### 1.4 Sunday：家庭叠衣，商用为零

- ACT-2 在未见过的家庭里叠衣 99.1%，实验室 hill-climb 后零样本迁移到家庭 [S:act-2]（官方，自报 ⚠️）。
- 2026-03 B 轮：Beta 项目"rolling out to users this Fall"，目标年内交付首批家庭自主机器人 [S:series-b]。面向家庭消费者，不做酒店/餐厅。

### 1.5 Generalist：无公开商用部署

- 采数覆盖上千个家庭/仓库/工作场所，约 9,000 种末端变体，"a few inspired by real commercial use cases" [G:hands]；融资稿列了餐厅等未来场景 [G:funding]；GEN-1 只对 early access partners 开放（[research-four-routes.md](research-four-routes.md) §0 对照表）。**采数现场不等于部署客户**，一手页面没有指名客户或付费部署。

## 2. 其他行业的商用落地

| 厂商 | 场景 | 事实 | 档位 | 来源 · 属性 |
|---|---|---|---|---|
| Figure | 汽车（BMW Spartanburg） | F.02 部署 11 个月，第 10 个月起全面上线，10 h 班次周一至周五，1,250+ h 运行，参与 3 万台 X3 生产、9 万+ 零件；钣金上料，周期 84 s，目标放置 >99%/班、干预 0/班；前臂是最高故障点 | 单站生产，已收官 | [F:bmw] · 官方 |
| Figure | 汽车（BMW Hall 52） | 2026-06-30 F.03 到场，从钣金上料转到"排序"物流工位，边走边双手操作 | 单站，新阶段 | [F:f03-bmw] · 官方 |
| Figure | 物流包裹分拣 | 2025-02 "real-world application"：传送带间转运、条码朝下；8 h 精策划数据出策略；2025-06 "three months since our initial deployment"，4.05 s/件；客户未披露 | 有部署字样，客户不明 | [F:logistics][F:scaling-logistics] · 官方 |
| Figure | 工厂班次 | 2026-05 Helix-02 8 h 全自主班次直播 | 演示 | TechTimes · 第三方 ⚠️ |
| Skild | 电子装配 | NVIDIA + Foxconn：双臂在 Blackwell 产线装汇流条、限位块、连拧 16 颗螺钉 | 部署中 | [K:oem][K:arr] · 官方 |
| Skild | 线束 | 住友电装：争取用 S1 自动化线束工序（"working towards deploying"） | 推进中 | [K:arr] · 官方 |
| Skild | 仓储 | 收购 Zebra 机器人部门（前 Fetch），AMR 平台 + 编排软件；移动业务占收入 10%（AMR 4%） | 存量客户 | [K:zebra][K:arr] · 官方 |
| Skild | OEM 渠道 | ABB、Universal Robots、MiR 把 Skild Brain 集成进产品线 | 渠道合作 | [K:oem] · 官方 |
| Skild | 安保、建筑、配送、数据中心、巡检 | 列为部署行业，未给客户名 | 已披露行业 | [K:series-c][K:arr] · 官方 |
| Dyna | 物流、数据中心、工厂装配 | "rollouts across … logistics companies, and data centers"；官网装配 200 件/h、±2 mm | 已宣布，无客户名 | [D:product][D:home] · 官方，自报 ⚠️ |
| Agility | 仓储（Digit） | 65,000 运行小时、9 个站点，2025 年营收 $1.8M | 多站点付费 | SEC S-4 经 The Robot Report · 官方文件 + 第三方（见 [data-strategy-roadmap.md](data-strategy-roadmap.md) §1） |
| 1X | 家庭（NEO） | 家庭部署以 Expert Mode 遥操作为主要数据来源 | 消费级早期 | 1x.tech、Humanoids Daily · 官方 + 第三方 |
| Apptronik | — | Apollo 2 定位为"数据采集平台，不是产品"，Robot Park 9 万平方英尺 | 非商用 | apptronik.com · 官方 |

## 3. 对洗衣房方案的含义

1. **能对标的只有 Dyna 的"叠"段**。他们公开的生产指标（每机班次产量、合格率、按客户 SOP 逐件评分、新站点 3 天达 ROI 线）可以直接借来做我们交付二"叠"的验收口径参考；"分类→洗→烘"和装取洗衣机，五家都没有公开商用案例，我们没有可照抄的现场基准（[laundry-two-plans-brief.md](laundry-two-plans-brief.md)）。
2. **内部评测接近 100% 不代表现场能过**：Dyna 自己承认 DYNA-1 在客户现场只有 46% 通过、DYNA-2 才到 87% [D:dyna-2]；鼎泰丰上线初期合格率 75% [D:product]。我们的 1 小时加速链路门验证的是功能，现场试点要预留这个落差。
3. **客户关心吞吐和 ROI，不是成功率**：鼎泰丰的门槛是"18 h 出 1,500 条"，Skild 的说法是"99.9% 准但慢 10 倍就不可部署" [K:arr]。我们的验收表应补一行每小时件数和每件成本，对照试点方人工。
4. **酒店场景整体空白**：Dyna 只说在推、Skild 把酒店排在第二阶段。如果我们先拿下一家酒店洗衣房试点，在公开案例里是靠前的。

## 4. 未覆盖与待补

- Dyna "Customer Testimonial: Monster Laundry" 页未归档；需要引用其数字时先按 [sources/MANIFEST.md](sources/MANIFEST.md) 规则抓取归档，再把 §1.1 对应行的属性从第三方改为官方。
- Dyna 酒店、物流、数据中心客户名称与台数（官方称"more on those soon"）。
- Skild 三井物产厨房试点的任务内容与指标；"preparing food"类其他客户。
- 五家之外的服务机器人（如中国的酒店配送、餐厅送餐、炒菜机器人厂商）不在本仓库调研范围，本文未收。
