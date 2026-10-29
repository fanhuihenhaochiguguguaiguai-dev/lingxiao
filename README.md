# 凌渊角色工作稿

## 当前版本与经验索引

最新有效网页是 [凌渊角色工作室](https://lingyuan-character-studio.earthyaspen11.chatgpt.site/skill/)（公开访问）。当前包含凌渊与月璃及六个技能。最新将已验证的龙形方法分别适配至缚星盘龙、苍穹巨龙和月璃冰龙，修正反向法线、俯冲龙身塌缩、转头突跳和爪部朝向；一技能已验证几何保持不变。仅采纳局部结构与运动改善，未认定整体精品通过。头部候选仍未替换正式人物脸部；头发 LOD 等合格修复保留。两个人物仍未通过最终原画还原；真机性能和专业听感仍未验证。下方是历次工作记录，旧状态以最新报告及其继承证据为准。

- 项目决策、成功经验、失败原因与预防措施：[`docs/PROJECT_LESSONS.md`](docs/PROJECT_LESSONS.md)。
- 人物制作经验与失败候选：[`docs/qingli-production-lessons.md`](docs/qingli-production-lessons.md)、[`docs/REFINEMENT_WORKFLOW.md`](docs/REFINEMENT_WORKFLOW.md)。
- 最新龙形差异化推广、自然运动修复、资源与实测：[`verification/promotion/README.md`](verification/promotion/README.md)。后续继承约定见 [`AGENTS.md`](AGENTS.md)。
- 一技能龙体样板、复用边界及真实画面：[`verification/dragon32/README.md`](verification/dragon32/README.md)。
- LOD 根因修复、头部候选：[`verification/lingyuan31/README.md`](verification/lingyuan31/README.md)。同一网站的[头部候选入口](https://lingyuan-character-studio.earthyaspen11.chatgpt.site/skill/?sample=lingyuan31-head)明确标注艺术未验收。
- 已有共性治理、运行结果：[`verification/governance/README.md`](verification/governance/README.md)；大招验收见 [`verification/moonfall/README.md`](verification/moonfall/README.md)。
- Git 历史保留了各阶段源码、资源及必要的回退点；部分生成脚本依赖外部工作区源资产，见下方来源说明。

这是根据用户提供的四张角色设定图制作的**未完成三维工作稿**，不具备正式验收质量。独立于原《曜境》工程，不覆盖原文件。参考图位于 `reference/`。

- `dist/Lingyuan_working.blend`：唯一 Blender 工作母版，贴图已打包，Blender 4.3.2 可打开。
- `dist/lingyuan-lod0.glb`、`lod1`、`lod2`：可加载的三个模型层级，包含骨架与基础动作。
- `dist/inspection/`：来自 Blender 工作稿的正面、侧面和背面渲染，非原画和非修图。
- `dist/`：网页静态文件。可运行 `python3 -m http.server 8765 --directory dist`，在浏览器打开本地地址。
- `verification/`：验证记录及浏览器实际截图，结果见 `verification/REPORT.md`。

来源：人体和枪从原工作区 `/workspace/yaojing/assets/heroes_rebuilt/poxiao.glb` 的重建候选提取，以 Blender 建立独立工作稿；其不是原设定图的原始三维资产。该原始依赖的副本位于 `reference/legacy-source/poxiao.glb`，`tools/build_character.py` 默认使用仓库内副本，也可通过 `LINGYUAN_LEGACY_SOURCE` 指定其他路径。新增衣袍、发束、肩部纹理和饰物由该脚本生成。当前头部拓扑和皮肤来自 CC0 MakeHuman 基础网格、形变与官方皮肤资产（见 `reference/makehuman/LICENSE.ASSETS.md`）；它们经过缩放、绑定、UV 映射和基础外形处理，不是凌渊原始面部数据。模型母版与 GLB 本身包含模型和纹理；部分历史辅助脚本仍引用旧工作区路径，不保证可直接在新环境运行。

网页通过 WASD / 方向键或触屏摇杆移动人物，拖动旋转镜头。网页只加载所需的模型，手机尺寸默认 LOD1；支持 `?renderer=webgl2` 兼容模式和加载失败提示。精修问题及流程见 `docs/REFINEMENT_WORKFLOW.md`。网页引擎 PlayCanvas，许可见 `dist/engine/PlayCanvas-MIT.txt`。网页默认优先 WebGPU，失败使用 WebGL 2；`?renderer=webgl2` 供兼容性检查。

新增的十张参考图及局部对应关系见 `reference/detail/INDEX.md`。可编辑脸部包含三个初步形变目标；详见最新验证报告。当前并非正式高质量成品。

第一技能工作稿位于 `dist/skill/`，源码位于 `skill-src/`。运行 `npm ci --prefix skill-src` 和 `npm run build --prefix skill-src` 可重新构建；在 `dist/` 启动静态服务器后访问 `/skill/`。现有角色和技能特效均未达到最终美术验收，参见 `verification/SKILL01_REPORT.md`。

二技能工作稿已接入现有 `/skill/` 页面，按钮可独立释放两个技能。新增法阵、青龙、晶体、光柱、锁链与粒子显隐控制；实现与未通过项目见 `verification/SKILL02_REPORT.md`。模型、动作与视觉效果尚未达到原画标准，安卓真机尚未验证。

大招「星渊龙卷」已加入同一技能展示页作为第三个演示按钮；质量状态、截图和未完成项见 `verification/SKILL03_REPORT.md`。展示页不含伤害与冷却系统，未宣称正式对局接入。

人物与三技能质量对照及本轮增量修复见 `verification/quality/REPORT.md`；当前仅完成共享流光的有限改进，人物精修和真机验收仍未完成。

本轮二技能龙身盘旋修复与人物候选记录见 `verification/character-refine/REPORT.md`；参考图对应见 `reference/detail174/部件对应.md`。候选人物未通过视觉采纳，正式模型仍为原工作稿。

本轮优先修复一技能龙首与枪尖同步、二技能晶体结构和大招腾空落地，并增加三个画质档与七种观察角度。339 张参考裁图见 `reference/skillboards/`；真实截图、测量与限制见 `verification/SKILL_UPGRADE_REPORT.md`。安卓构建位于 `android-app/`，现有 APK 尚未签名且不能安装，没有安卓真机验证。人物和三个技能仍是未达到原画验收的工作稿。

V4 三技能龙首、背鳍、可选镜头跟随及人物移动过渡的有限升级与证据见 `verification/v4-dragon/REPORT.md`。展示页当前画质档为高清和极致；自然表情、专业跑步、手机实测和最终美术验收仍未完成。

V11 在现有技能页接入可移动角色、当前位置施法、扩大平台、跟拍、简化界面与 CC0 授权素材音效。运行记录、参考截图和未完成项见 `verification/v11/REPORT.md`；角色与技能仍未达到最终美术标准，手机真机未验证。

V12 修复了三个技能共享龙首的几何合并及法线问题，并改进施法输入、后台声音与错误提示。资源核对、真实对照、未采用的跑步候选和未完成项见 `verification/v12/REPORT.md`。

新增清璃参考裁切与静态三维研究：用户选择第 2 张银白发设计为主参考。`reference/qingli/` 保存原图、原像素裁图、插值图和索引；`characters/qingli/` 的模型尚无骨骼、未通过静态美术验收，因此未接入网站。详见 `verification/qingli/REPORT.md`。
