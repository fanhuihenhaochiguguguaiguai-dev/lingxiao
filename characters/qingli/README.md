# 月璃当前工作稿

`Yueli_working.blend` 是当前唯一制作主稿，`Yueli_working.glb` 是对应导出；网页使用同源的 `dist/yueli-study.glb`。显示名沿用用户最后确认的「月璃」。

当前包含 36 根骨骼、全身初步蒙皮、眼球枢轴、Blink 形变、连续内裙与局部前发调整。本轮同步修改实际基础网格与 Blink 的眼眶／鼻唇／下颌比例，替换僵硬前发条，补贴体衣片、细金饰与尖瓣花饰。实际 GLB 顶点差异及同灯光前后对照见 `../../verification/moonfall/character/`，不将局部变化当作原画神韵已还原。

待机、独立的行走／跑步轨迹、双腿接触求解、跳跃与三个技能的施法姿势由网页共享的 `CharacterMotion` 控制；没有将旧失败跑步片段复制进来。月华霜羽、月影寒潮、月陨天霜现均为可运行技能工作稿。原静态 `Qingli_static_study.*` 仅为迁移源，不是最新成果。

`../../verification/dual-quality/` 保存真实网页、固定灯光近景对照和检查。脸型、发型、衣甲、鞋靴与原画仍有明显差距；完整面部表情、服装碰撞与自然动作没有通过艺术验收。详细旧问题见 `../../docs/qingli-production-lessons.md` 和 `../../verification/qingli/REPORT.md`。CC0 基础资源来源保留在 `../../reference/makehuman/SOURCE.md`。

最新验收记录为 `../../verification/moonfall/README.md`。人物造型仍以原始 board-04／board-01 为准，技能图不替代人物外观标准。一次性参考变形迁移脚本拒绝在已调整母稿上再次叠加；重现实验须显式指定 V21 的原始母稿。
