# 凌渊角色工作稿

这是根据用户提供的四张角色设定图制作的**未完成三维工作稿**，不具备正式验收质量。独立于原《曜境》工程，不覆盖原文件。参考图位于 `reference/`。

- `dist/Lingyuan_working.blend`：唯一 Blender 工作母版，贴图已打包，Blender 4.3.2 可打开。
- `dist/lingyuan-lod0.glb`、`lod1`、`lod2`：可加载的三个模型层级，包含骨架与基础动作。
- `dist/inspection/`：来自 Blender 工作稿的正面、侧面和背面渲染，非原画和非修图。
- `dist/`：网页静态文件。可运行 `python3 -m http.server 8765 --directory dist`，在浏览器打开本地地址。
- `verification/`：验证记录及浏览器实际截图，结果见 `verification/REPORT.md`。

来源：人体和枪从 `/workspace/yaojing/assets/heroes_rebuilt/poxiao.glb` 的重建候选提取，以 Blender 建立独立工作稿；其不是原设定图的原始三维资产。新增衣袍、发束、肩部纹理和饰物由 `tools/build_character.py` 生成。当前头部拓扑和皮肤来自 CC0 MakeHuman 基础网格、形变与官方皮肤资产（见 `reference/makehuman/LICENSE.ASSETS.md`）；它们经过缩放、绑定、UV 映射和基础外形处理，不是凌渊原始面部数据。重建脚本依赖上述已有源文件路径，母版和 GLB 本身包含模型与纹理，可脱离原项目打开；源码重建不具备独立性。

网页通过 WASD / 方向键或触屏摇杆移动人物，拖动旋转镜头。网页只加载所需的模型，手机尺寸默认 LOD1；支持 `?renderer=webgl2` 兼容模式和加载失败提示。精修问题及流程见 `docs/REFINEMENT_WORKFLOW.md`。网页引擎 PlayCanvas，许可见 `dist/engine/PlayCanvas-MIT.txt`。网页默认优先 WebGPU，失败使用 WebGL 2；`?renderer=webgl2` 供兼容性检查。

新增的十张参考图及局部对应关系见 `reference/detail/INDEX.md`。可编辑脸部包含三个初步形变目标；详见最新验证报告。当前并非正式高质量成品。

第一技能工作稿位于 `dist/skill/`，源码位于 `skill-src/`。运行 `npm ci --prefix skill-src` 和 `npm run build --prefix skill-src` 可重新构建；在 `dist/` 启动静态服务器后访问 `/skill/`。现有角色和技能特效均未达到最终美术验收，参见 `verification/SKILL01_REPORT.md`。

二技能工作稿已接入现有 `/skill/` 页面，按钮可独立释放两个技能。新增法阵、青龙、晶体、光柱、锁链与粒子显隐控制；实现与未通过项目见 `verification/SKILL02_REPORT.md`。模型、动作与视觉效果尚未达到原画标准，安卓真机尚未验证。
