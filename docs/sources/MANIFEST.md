# 一手资料归档清单（docs/sources）

> 全部于 2026-09-14 用 curl 直抓（WebFetch 对各站均被拦截；skild.ai 白天超时、晚间可达），HTML 去标签后存为纯文本；每个文件头部记录 URL、页面日期、抓取日期、原始 HTML 的 sha256 与字节数。原始 HTML 未入库（Sunday 技术页 2.7 MB、Dyna 研究页 2.1 MB），需要复核时按 sha256 重新抓取比对。用途：让 research-*.md 里每条事实都能指向一份可 grep 的本地一手文本；引用格式 `sources/<company>/<slug>.txt`。版权归各公司，仅作引用与核对，不再分发。

| 公司 | 文件 | 标题 | 页面日期 | URL | 文本字符 | HTML sha256 前 12 位 |
|---|---|---|---|---|---|---|
| figure | [`figure/helix.txt`](figure/helix.txt) | Helix: A Vision-Language-Action Model for Generalist Humanoid Control | 2025-02-20 | https://www.figure.ai/news/helix | 15,282 | `54567d6fd45f` |
| figure | [`figure/helix-logistics.txt`](figure/helix-logistics.txt) | Helix Accelerating Real-World Logistics | 2025-02-26 | https://www.figure.ai/news/helix-logistics | 9,325 | `cff2245a2842` |
| figure | [`figure/reinforcement-learning-walking.txt`](figure/reinforcement-learning-walking.txt) | Natural Humanoid Walk Using Reinforcement Learning | 2025-03-25 | https://www.figure.ai/news/reinforcement-learning-walking | 5,143 | `a9596163b9fd` |
| figure | [`figure/scaling-helix-logistics.txt`](figure/scaling-helix-logistics.txt) | Scaling Helix: a New State of the Art in Humanoid Logistics | 2025-06-07 | https://www.figure.ai/news/scaling-helix-logistics | 14,571 | `2bc3ef824430` |
| figure | [`figure/helix-learns-to-fold-laundry.txt`](figure/helix-learns-to-fold-laundry.txt) | Helix Learns to Fold Laundry | 2025-08-12 | https://www.figure.ai/news/helix-learns-to-fold-laundry | 2,547 | `578806289d2f` |
| figure | [`figure/helix-loads-the-dishwasher.txt`](figure/helix-loads-the-dishwasher.txt) | Helix Loads the Dishwasher | 2025-09-03 | https://www.figure.ai/news/helix-loads-the-dishwasher | 1,944 | `8cc18dd89e5d` |
| figure | [`figure/project-go-big.txt`](figure/project-go-big.txt) | Project Go-Big: Internet-Scale Humanoid Pretraining and Direct Human-to-Robot Transfer | 2025-09-18 | https://www.figure.ai/news/project-go-big | 5,208 | `7ac5c72d5b8c` |
| figure | [`figure/introducing-figure-03.txt`](figure/introducing-figure-03.txt) | Introducing Figure 03 | 2025-10-09 | https://www.figure.ai/news/introducing-figure-03 | 10,253 | `042557a2a3e7` |
| figure | [`figure/production-at-bmw.txt`](figure/production-at-bmw.txt) | F.02 Contributed to the Production of 30,000 Cars at BMW | 2025-11-19 | https://www.figure.ai/news/production-at-bmw | 3,688 | `d7cbfd216f1d` |
| figure | [`figure/helix-02.txt`](figure/helix-02.txt) | Introducing Helix 02: Full-Body Autonomy | 2026-01-27 | https://www.figure.ai/news/helix-02 | 11,079 | `a2f842e6ec33` |
| figure | [`figure/helix-02-living-room-tidy.txt`](figure/helix-02-living-room-tidy.txt) | Helix 02 Living Room Tidy | 2026-03-09 | https://www.figure.ai/news/helix-02-living-room-tidy | 3,165 | `917d5c0e34a6` |
| figure | [`figure/ramping-figure-03-production.txt`](figure/ramping-figure-03-production.txt) | Ramping Figure 03 Production | 2026-04-29 | https://www.figure.ai/news/ramping-figure-03-production | 8,106 | `cbed69592b2a` |
| figure | [`figure/helix-02-bedroom-tidy.txt`](figure/helix-02-bedroom-tidy.txt) | Helix 02 Bedroom Tidy | 2026-05-08 | https://www.figure.ai/news/helix-02-bedroom-tidy | 4,857 | `517f0f50683d` |
| figure | [`figure/introducing-index.txt`](figure/introducing-index.txt) | Introducing Index: Building The World’s Largest and Most Diverse Physical Dataset | 2026-08-25 | https://www.figure.ai/news/introducing-index | 4,552 | `edb8f2c6e7f7` |
| figure | [`figure/f-03-at-bmw.txt`](figure/f-03-at-bmw.txt) | F.03 Arrives at BMW | 2026-06-30 | https://www.figure.ai/news/f-03-at-bmw | 2,901 | `730754cc9d50` |
| figure | [`figure/f-03-battery-development.txt`](figure/f-03-battery-development.txt) | F.03 Battery Development | 2025-07-17 | https://www.figure.ai/news/f-03-battery-development | 7,626 | `6ab63ed7187a` |
| figure | [`figure/figure-and-nscale.txt`](figure/figure-and-nscale.txt) | Figure and Nscale Sign Strategic Partnership (up to 100,000 GPUs) | 2026-09-03 | https://www.figure.ai/news/figure-and-nscale-sign-strategic-partnership | 2,397 | `ae70ec8f2884` |
| figure | [`figure/index-app.txt`](figure/index-app.txt) | Index | Figure（产品页，数字随时间更新） | 页面无日期 | https://www.figure.ai/index-app | 867 | `3f5c6f76043b` |
| dyna | [`dyna/dyna-1.txt`](dyna/dyna-1.txt) | Dynamism v1 (DYNA-1) Model: A Breakthrough in Performance and Production-Ready Embodied AI | 2025-06-24 | https://www.dyna.co/research/dyna-1 | 9,845 | `602d5b50f0f6` |
| dyna | [`dyna/open-world-dexterity.txt`](dyna/open-world-dexterity.txt) | Open-World Dexterity and Live Demos around the World (DYNA-1i) | 2025-10-15 | https://www.dyna.co/research/open-world-dexterity | 4,816 | `7a291ca33d0c` |
| dyna | [`dyna/pre-training.txt`](dyna/pre-training.txt) | DYNA-1 Pre-Training: Zero-Shot Dexterity Is Here | 2025-11-20 | https://www.dyna.co/research/pre-training | 1,451 | `cc1d96764a00` |
| dyna | [`dyna/dyna-2.txt`](dyna/dyna-2.txt) | Dyna-2: A 1-Million-Hour Scaling Law for World-Action Models | 2026-08-15 | https://www.dyna.co/dyna-2 | 54,499 | `1cf6c0acd620` |
| dyna | [`dyna/dyna-2-infrastructure.txt`](dyna/dyna-2-infrastructure.txt) | Training Dyna-2 at million-hour scale, repeatably | 2026-08-17 | https://www.dyna.co/research/dyna-2-infrastructure | 28,265 | `74fd2c48df9d` |
| dyna | [`dyna/scaling-customer-deployments.txt`](dyna/scaling-customer-deployments.txt) | Not Just a Model, But a Product | 2026-08-27 | https://www.dyna.co/research/scaling-customer-deployments | 21,768 | `4fdaa6368742` |
| sunday | [`sunday/no-robot-data.txt`](sunday/no-robot-data.txt) | ACT-1: A Robot Foundation Model Trained on Zero Robot Data | 2025-11-19 | https://www.sunday.ai/blog/no-robot-data | 9,479 | `4b2b811c298c` |
| sunday | [`sunday/series-b.txt`](sunday/series-b.txt) | Sunday's Series B: No More Demos | 2026-03-12 | https://www.sunday.ai/blog/series-b | 1,896 | `94369ce78db3` |
| sunday | [`sunday/act-2-preview.txt`](sunday/act-2-preview.txt) | ACT-2 Preview: Generalizing Reliability | 2026-07-17 | https://www.sunday.ai/blog/act-2-preview | 25,729 | `e28a90a77b4c` |
| sunday | [`sunday/technology.txt`](sunday/technology.txt) | Technology | Sunday Robotics（产品页） | 页面无日期 | https://www.sunday.ai/technology | 1,326 | `52463750dbce` |
| generalist | [`generalist/research-preview.txt`](generalist/research-preview.txt) | Research Preview | 2025-06-17 | https://generalistai.com/blog/research-preview | 4,102 | `fde921ea2669` |
| generalist | [`generalist/the-robots-build-now-too.txt`](generalist/the-robots-build-now-too.txt) | The Robots Build Now, Too | 2025-09-24 | https://generalistai.com/blog/the-robots-build-now-too | 2,168 | `56c46e77ce6e` |
| generalist | [`generalist/gen-0.txt`](generalist/gen-0.txt) | GEN-0 / Embodied Foundation Models That Scale with Physical Interaction | 2025-11-04 | https://generalistai.com/blog/gen-0 | 17,574 | `d81c1843846a` |
| generalist | [`generalist/physical-commonsense.txt`](generalist/physical-commonsense.txt) | The Dark Matter of Robotics: Physical Commonsense | 2026-01-29 | https://generalistai.com/blog/physical-commonsense | 12,004 | `8a3f834cff8a` |
| generalist | [`generalist/the-real-breakthrough-behind-our-gtc-demo.txt`](generalist/the-real-breakthrough-behind-our-gtc-demo.txt) | The Real Breakthrough Behind Our GTC Demo | 2026-03-24 | https://generalistai.com/blog/the-real-breakthrough-behind-our-gtc-demo | 3,471 | `3925e33d2a66` |
| generalist | [`generalist/gen-1.txt`](generalist/gen-1.txt) | GEN-1: Scaling Embodied Foundation Models to Mastery | 2026-04-02 | https://generalistai.com/blog/gen-1 | 18,682 | `7bea19b70805` |
| generalist | [`generalist/beyond-world-models.txt`](generalist/beyond-world-models.txt) | Going Beyond World Models & VLAs | 2026-04-07 | https://generalistai.com/blog/beyond-world-models | 7,960 | `595032007c83` |
| generalist | [`generalist/accelerating-the-next-phase-of-physical-ai.txt`](generalist/accelerating-the-next-phase-of-physical-ai.txt) | Accelerating the Next Phase of Physical AI | 2026-06-04 | https://generalistai.com/blog/accelerating-the-next-phase-of-physical-ai | 3,579 | `4f32a47d3425` |
| generalist | [`generalist/towards-machines-with-a-thousand-hands.txt`](generalist/towards-machines-with-a-thousand-hands.txt) | Towards Machines with a Thousand Hands | 2026-07-23 | https://generalistai.com/blog/towards-machines-with-a-thousand-hands | 8,907 | `de0d67349743` |
| generalist | [`generalist/gen-1.5.txt`](generalist/gen-1.5.txt) | GEN-1.5: Embodied Foundation Models are One-Shot Learners | 2026-08-19 | https://generalistai.com/blog/gen-1.5 | 25,195 | `b56d7a36a497` |

| skild | [`skild/announcing-our-300m-series-a.txt`](skild/announcing-our-300m-series-a.txt) | Announcing our $300M Series A Funding | 2024-07-09 | https://www.skild.ai/blogs/announcing-our-300m-series-a | 5,675 | `0c3bcecd6847` |
| skild | [`skild/building-the-general-purpose-robotic-brain.txt`](skild/building-the-general-purpose-robotic-brain.txt) | Building the general-purpose robotic brain | 2025-07-29 | https://www.skild.ai/blogs/building-the-general-purpose-robotic-brain | 6,908 | `7f327e46fcfd` |
| skild | [`skild/one-policy-all-scenarios.txt`](skild/one-policy-all-scenarios.txt) | One Model, Any Scenario: End-to-end Locomotion from Vision | 2025-08-06 | https://www.skild.ai/blogs/one-policy-all-scenarios | 4,710 | `938452222827` |
| skild | [`skild/omni-bodied.txt`](skild/omni-bodied.txt) | The case for an omni-bodied robot brain | 2025-09-24 | https://www.skild.ai/blogs/omni-bodied | 6,161 | `bf95b609b739` |
| skild | [`skild/learning-by-watching.txt`](skild/learning-by-watching.txt) | Learning by watching human videos | 2026-01-12 | https://www.skild.ai/blogs/learning-by-watching | 2,573 | `de256ae15a50` |
| skild | [`skild/series-c.txt`](skild/series-c.txt) | Announcing Series C | 2026-01-14 | https://www.skild.ai/blogs/series-c | 3,295 | `b32d83ad605e` |
| skild | [`skild/bengaluru.txt`](skild/bengaluru.txt) | Skild AI Expands Global Footprint To Bengaluru | 2026-02-19 | https://www.skild.ai/blogs/bengaluru | 2,155 | `682476dffecc` |
| skild | [`skild/reindustrial-revolution.txt`](skild/reindustrial-revolution.txt) | The Reindustrial Revolution: Partnering with ABB Robotics, Universal Robots, and NVIDIA | 2026-03-19 | https://www.skild.ai/blogs/reindustrial-revolution | 6,668 | `fbd4b6025441` |
| skild | [`skild/skild-zebra.txt`](skild/skild-zebra.txt) | Skild AI Acquires Zebra Technologies' Robotics Arm | 2026-04-15 | https://www.skild.ai/blogs/skild-zebra | 3,806 | `2b785a385635` |
| skild | [`skild/s1.txt`](skild/s1.txt) | Introducing S1: In-Context Learning for Robotics | 2026-08（页面只写月份；100M ARR 文说 S1 发布于其两周前，即约 2026-08-27） | https://www.skild.ai/blogs/s1 | 23,821 | `18fb93bfaec8` |
| skild | [`skild/skild-crosses-100m-arr.txt`](skild/skild-crosses-100m-arr.txt) | The Hidden Pillar of Robotics (Skild AI crossed $100 million in ARR) | 2026-09-10 | https://www.skild.ai/blogs/skild-crosses-100m-arr | 8,357 | `39535a1a56af` |
共 49 篇：Figure 18、Dyna 6、Sunday 4、Generalist 10、Skild 11（skild.ai 于 2026-09-14 晚间可达，全部博客归档）。

## 图片归档（docs/assets/sources/）

只归档研究文档需要观察其硬件细节的官方图片；文件缩到 ≤1600 px 以控制仓库体积，原图 sha256 记录在此供复核。

| 公司 | 文件 | 所在页面 | 原图 URL | 原图 sha256 前 12 位 | 体积 | 说明 |
|---|---|---|---|---|---|---|
| sunday | [`assets/sources/sunday/sunday-glove-vs-memo-hand.jpg`](../assets/sources/sunday/sunday-glove-vs-memo-hand.jpg) | https://www.sunday.ai/blog/no-robot-data | https://cdn.sanity.io/images/1omys9i3/production/6fdf2cb073bd2830ef2bac165afa4c14ad848d36-1920x1080.png | `aec5ae3578f8` | 109 KB（缩到 ≤1600 px JPEG，原图 549 KB） | ACT-1 博客配图，页面 caption："Skill Capture Glove (left) and Memo's hand (right)" |
| sunday | [`assets/sources/sunday/sunday-glove-holding-orange.jpg`](../assets/sources/sunday/sunday-glove-holding-orange.jpg) | https://www.sunday.ai/technology | https://cdn.sanity.io/images/1omys9i3/production/69317e0507b6454687e7d0ae1d36f611e141f1c8-4000x2668.jpg | `26cb83ec3857` | 217 KB（缩到 ≤1600 px JPEG，原图 836 KB） | 技术页照片（无 alt/caption）：戴着 Skill Capture Glove 握橙子 |
| sunday | [`assets/sources/sunday/sunday-glove-closeup-screw.jpg`](../assets/sources/sunday/sunday-glove-closeup-screw.jpg) | https://www.sunday.ai/technology | https://cdn.sanity.io/images/1omys9i3/production/c0de3a6e4eb0140002e7b058cd05786c67511865-4000x2668.jpg | `9a2e6f0e1e22` | 242 KB（缩到 ≤1600 px JPEG，原图 941 KB） | 技术页照片（无 alt/caption）：手套特写，相机吊舱与两片接触面，捏着一枚螺钉 |
| sunday | [`assets/sources/sunday/sunday-og-head-camera.jpg`](../assets/sources/sunday/sunday-og-head-camera.jpg) | https://www.sunday.ai/technology | https://cdn.sanity.io/images/1omys9i3/production/319392a9e6c83e4b9f7c2158c5b10fa6f75e84c1-2400x1260.png | `34ee61edfdc7` | 190 KB（缩到 ≤1600 px JPEG，原图 1919 KB） | 站点 OG 图（无 alt）：头戴帽檐上的相机镜头与长条开口 |

## 归档规则

1. research 文档引用四家公司的事实时，必须指向本目录的文件（`sources/<company>/<slug>.txt`），未归档的一手页面先归档再引用；第三方转述照旧标 ⚠️ 并给 URL。
2. 新增归档用同一头部格式；页面更新后重抓时不覆盖旧文件，另存 `<slug>.<YYYY-MM-DD>.txt` 并在本表加行。
3. 数字类事实引用时给到文件内可 grep 的原文短语（英文原句片段），便于核对。
