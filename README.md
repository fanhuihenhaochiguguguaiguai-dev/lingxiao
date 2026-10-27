# 凌渊角色工作稿

这是根据用户提供的四张角色设定图制作的**未完成三维工作稿**，不具备正式验收质量。独立于原《曜境》工程，不覆盖原文件。参考图位于 `reference/`。

- `dist/Lingyuan_working.blend`：唯一 Blender 工作母版，贴图已打包，Blender 4.3.2 可打开。
- `dist/lingyuan-lod0.glb`、`lod1`、`lod2`：可加载的三个模型层级，包含骨架与基础动作。
- `dist/inspection/`：来自 Blender 工作稿的正面、侧面和背面渲染，非原画和非修图。
- `dist/`：网页静态文件。可运行 `python3 -m http.server 8765 --directory dist`，在浏览器打开本地地址。
- `verification/`：验证记录及浏览器实际截图，结果见 `verification/REPORT.md`。

来源：人体和枪从 `/workspace/yaojing/assets/heroes_rebuilt/poxiao.glb` 的重建候选提取，以 Blender 建立独立工作稿；其不是原设定图的原始三维资产。新增衣袍、发束、肩部纹理和饰物由 `tools/build_character.py` 生成。重建脚本依赖上述已有源文件路径，母版和 GLB 本身包含模型与纹理，可脱离原项目打开；源码重建不具备独立性。

网页引擎 PlayCanvas，许可见 `dist/engine/PlayCanvas-MIT.txt`。网页默认优先 WebGPU，失败使用 WebGL 2；`?renderer=webgl2` 供兼容性检查。
