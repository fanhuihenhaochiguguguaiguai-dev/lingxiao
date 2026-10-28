# 清璃：未完成的静态三维研究

此目录保存一份可编辑 Blender 静态工作稿与对应 GLB，不是已验收的第二人物。人物使用 MakeHuman CC0 女性基础网格建立；头发、衣身、裙片、少量饰品为本次新建的几何，颜色仅作初步材质研究，未使用参考图作人物贴片。基础网格与形变来源、许可见 `../../reference/makehuman/SOURCE.md`。

最新主参考为 `../../reference/qingli/originals/board-01.jpg` 和 `board-04.jpg`；第 2 张保留作辅助。`tools/refine_qingli_study.py` 增补的刘海、发束、眉和首饰只是静态几何实验，与原图仍有显著差距。

`Qingli_static_study.blend` 和 `Qingli_static_study.glb` 可加载，但没有骨骼、蒙皮、行走／奔跑、眨眼、表情、衣发物理或技能。没有通过相似度、美术质量或拓扑验收，未接入公开网站。正面、侧面、背面、45°和脸部真实渲染及技术检查在 `../../verification/qingli/`。工作稿的上衣、五官、发束、长裙及装饰均需要明显精修。

使用仓库内 Blender 和 MakeHuman 资产可通过 `blender -b -t 2 --python tools/build_qingli_study.py` 复现临时研究模型；结果会写入 `/tmp/qingli-study`。原始来源为 CC0，不包含校园项目的摄影脸部贴图。
