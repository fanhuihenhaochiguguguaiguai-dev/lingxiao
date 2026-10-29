# V3.5：闭合特效几何与头像候选续修

基线：`3528f0a42b12bdc2505a426ab13f3dba6c12e574`（原网站 V26）。保留原场景、操作、两个正式人物、六技能与既有龙形／LOD／实例／音频／回收修复。此次采纳四个技能的局部结构改善，**不是六技能、两个人物的整体精品验收通过**。

## 已采纳：真实几何缺陷

共性根因是把二维参数曲面当作实体使用：双层绕序不一致、未封口、端点收零仍继续生成四边格，以及晶体用光滑法线混合棱面。`DoubleSide` 允许它们显示，不能提供厚度或正确面向。

[`crystal-geometry.ts`](../../skill-src/src/crystal-geometry.ts) 实现封闭透镜截面与封底尖顶棱柱：花瓣／霜羽保持连续曲率，晶体使用独立面法线。不同技能保留自己的尺寸和轮廓，没有改为同一颜色／大小的复制效果。

| 部件 | 原问题 | 新结果 |
| --- | --- | --- |
| 月华霜羽：冰莲花瓣 | 28 条开边、16 个退化三角形，无实体厚度 | 闭合薄壳，208 三角形；可读边缘与曲面厚度 |
| 月华霜羽：霜羽 | 38 条共享边面向冲突、4 个退化三角形 | 正反面连续的薄透镜截面，204 三角形 |
| 月影寒潮／月陨天霜：冰莲 | 24 条开边、12 个退化三角形 | 保持原高度／伸展方向的闭合花瓣，208 三角形 |
| 月影寒潮／月陨天霜：冰晶 | 6 条底部开边、6 个退化三角形、体积符号为负 | 封底六棱晶体，面向外、硬棱受光；仍为 36 三角形 |
| 青龙缚星阵：星晶 | 原八面体不是拓扑错误，但侧面过于简化 | 独立较矮／扁的肩部与晶冠，36 三角形；没有套用月系高细晶形 |

五种新几何经位置焊接审计，均为 **0 开边、0 非流形边、0 面向冲突边、0 退化三角形，体积为正**。详见 [`surfaces/before.json`](surfaces/before.json)、[`surfaces/after.json`](surfaces/after.json)。不把这个检测套用到设计上本就开放的布料或能量面。

实际使用位置：[`moon-frost.ts`](../../skill-src/src/moon-frost.ts)、[`moon-tide.ts`](../../skill-src/src/moon-tide.ts)、[`bind-star.ts`](../../skill-src/src/bind-star.ts)。月陨天霜继承自身已经使用的月系几何库。原月轮、法阵、龙形路径、粒子数量、材质参数、时序、音频与命中规则保持。

## 真实前后画面

以下均为原网站实际 WebGL2 渲染，同一相机／光照／时刻，无生成图片替代：

| 技能 | 修改前 | 修改后 |
| --- | --- | --- |
| 缚星阵星晶 | [近景](web/before-binding-detail.png) | [近景](web/after-binding-detail.png) |
| 霜羽、冰莲 | [近景](web/before-frost-detail.png) | [近景](web/after-frost-detail.png) |
| 寒潮、冰莲与冰晶 | [近景](web/before-tide-detail.png) | [近景](web/after-tide-detail.png) |
| 月陨天霜 | [近景](web/before-moonfall-detail.png) | [近景](web/after-moonfall-detail.png) |

[`web/`](web/) 另有同角度整体图。`before.json` / `after.json` 保存相机位置、目标和绘制计数，自动断言前后相机完全一致。

固定整体帧计数：

| 技能 | Draw Calls 前 → 后 | 三角形前 → 后 |
| --- | ---: | ---: |
| 缚星阵，3.6 s | 156 → 156 | 129342 → 130406 |
| 月华霜羽，2.8 s | 117 → 117 | 171385 → 176425 |
| 月影寒潮，3.5 s | 136 → 136 | 259150 → 260302 |
| 月陨天霜，4.4 s | 133 → 133 | 239651 → 241379 |

约 0.4%–2.9% 的当前视角三角形增加用于真实截面和封口，没有增加粒子数或 Bloom。是桌面软件绘制负载，**不能视为手机 FPS 成绩**。

[`surfaces/`](surfaces/) 保存同一源几何的真实 Blender 前后渲染；Blender 材质仅用于形态检查，网页材质仍以实际 Three.js 结果为准。可编辑库是 [`Effect_surfaces.blend`](../../characters/effect-surfaces/Effect_surfaces.blend)，便携静态资源为 [`effect-surfaces.glb`](../../dist/quality/effect-surfaces.glb)。网页使用同源生成器，不把这些渲染图作为特效贴图。坐标／三角形往返检查在 [`assets.json`](assets.json)。

## 凌渊头像：继续候选，未替换正式人物

保留原 4514 顶点笼、UV、60 骨骼与全部面部形变。局部修整上眼睑、眼眶深度、鼻梁／鼻尖、下唇和颊面；眼球直径未放大，附属睫毛／眼部结构一并适配。最大局部位移约 1.89 mm。不是手工精雕完成或原画神韵通过。

沿用既有高低模管线重新生成 71861 顶点离线基底／可编辑 Multires，实际重新烘焙 2048² 切线法线与 1024² AO，并嵌入候选 GLB。高模未导出到运行场景，仍仅加载 LOD1。见 [`head/structure.json`](head/structure.json)、[`head/bake.json`](head/bake.json)、[`assets.json`](assets.json)。

**发型候选撤回：** 第一版出现 [宽扁尖片](rejected/groom-blocks.png)，第二版出现 [帽状头皮与过齐发条](rejected/groom-scalp-cap.png)。射线贴合和曲线分束并未解决艺术问题。两者均未采纳，最终候选保留原前后发与权重；不向月璃推广。失败实验仅通过脚本的 `LING35_GROOM=experimental` 显式开启。

- [正面前](head/before-front.png)／[正面后](head/after-front.png)
- [45° 前](head/before-angle.png)／[45° 后](head/after-angle.png)
- [侧面前](head/before-side.png)／[侧面后](head/after-side.png)
- [背面前](head/before-back.png)／[背面后](head/after-back.png)

这些是固定低模笼、姿态、灯光／相机的真实 Blender 对照。原画依据仍为 `reference/1-1000069993.jpg` 与 `reference/detail/4-mmexport1793091788549.jpg`。当前脸型、眼神、发型与原图仍有明显差距；**艺术未验收**。

只更新已有 [`Lingyuan_head_candidate.blend`](../../characters/lingyuan/Lingyuan_head_candidate.blend) 与 [`lingyuan31-head.glb`](../../dist/quality/lingyuan31-head.glb)，通过同一网站的 [`?sample=lingyuan31-head`](https://lingyuan-character-studio.earthyaspen11.chatgpt.site/skill/?sample=lingyuan31-head) 查看。正式入口两个人物 GLB 保持字节不变。

## 定向验证与复现

- TypeScript 构建通过；Python 检查与几何审计通过。
- [`assets.json`](assets.json) 验证默认双人物、三个正式凌渊 LOD、既有龙形／运动／实例／音频源码相对基线不变；候选法线、蒙皮权重、形变、唯一活动 LOD 与离线母模排除正确。
- [`runtime/head.json`](runtime/head.json)：候选在软件 WebGL2／WebGPU 实际加载、睁闭眼、走跑速度区别、跳跃与双人物往返切换通过。截图中眨眼仍有简化感，不等于自然表情艺术验收。
- 受影响四技能的 1/3/5/10 次即时释放、独立音频事件、跑跳施法、十实例训练命中、池复用见 [`runtime/instances.json`](runtime/instances.json)。属于合成输入与事件层测试，不是物理音频延迟或真机触控测试。
- [`runtime/surfaces.json`](runtime/surfaces.json)：两个软件后端实际绘制四种效果各十实例；WebGL2 三轮回收计数比较，不把计数稳定当成总内存／长时泄漏证明。

回收测试最初错误地假定 `advance(13)` 会让原生 AudioContext 同时经过 13 秒，误判霜羽声尾未结束。修正为独立等待原生声音自然播放结束，再断言声音与待播放队列归零；没有为通过测试而停止音频、删除声音层或更改正式播放逻辑。`nativeAudioTailDrainWallMs` 是测试等待声尾的时间，**不是音频触发延迟**。

关键脚本：`check_surface35.mjs before|after`、`build_surface35_baseline.mjs`、`capture_surface35.py before|after`、`render_surface35.py`、`validate_v35_assets.py`、`test_surface35_runtime.py`、`test_head35_runtime.py`。前图路由仅在测试中恢复 `3528f0a` 的三个受影响源模块，保持同一网页和 QA 相机；正式产物没有旧代码切换功能。

头像复现先从 Git 基线恢复 `/tmp/lingyuan35-before.blend`，通过 `LING35_SOURCE` 指向它运行 `refine_lingyuan35.py`，再以 `LINGYUAN_HEAD_WORK=/tmp/lingyuan35` 运行现有 `bake_lingyuan31_head.py`。脚本拒绝重复叠加已经带 `refinement35` 标记的候选。新数据用 Git 保存，不另建主工程。

## 剩余状态

**未达标／未完成：** 两个人物原画级脸部神韵、完整发型、服装／武器、材质细化、自然表情、专业步态、全身 IK、衣发碰撞；六技能整体的雕刻级结构、完整演出与最终艺术品质。此轮只采纳上文局部几何改善，没有宣称六技能全部精修完成。

**未验证：** 安卓真机 FPS／帧时间、触控／音频物理延迟、长时内存与专业听感。软件环境仍不能代表流畅手机表现。

未增加普攻、生命值、伤害、破坏、1v1、第三人物、地图、引擎或 APK；用户设置、操作布局和公开网站保持。
