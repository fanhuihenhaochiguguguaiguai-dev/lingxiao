# 月璃网页工作稿验证

网页使用 `dist/yueli-study.glb`，它与 `characters/qingli/Qingli_static_study.glb` 是同一个静态模型；角色显示名为用户确认的「月璃」。它仍不是已验收的正式角色，没有骨骼、动作或表情。网页摇杆移动模型在场景中的位置，不代表走路或跑步动画；月璃不具备技能。新增参考原图保存在 `reference/qingli/originals/board-05-yueli.jpg`，尚未拆图或用于本轮建模。

`result.json`、`yueli-initial.png` 和 `yueli-webgl.png` 来自桌面 Chromium 软件 WebGL2 实际网页运行。测试覆盖设置面板、静音、画质、选择框、模型加载、位置改变、镜头拖动、切回凌渊及三个技能按钮触发、月璃模型缓存；`landscape-simulated.png` 来自横屏触屏模拟。技能美术质量、完整动作、移动端帧率与真实手机触控未在本次测试中验收。

`tools/test_yueli_switch.py` 使用本地静态服务；实际设备测试仍需真机。原 Blender/GLB 的衣层修改器已导出为真实几何，详见 `verification/qingli/REPORT.md`。

`default-renderer.json` 记录默认后端下的加载验证：本次桌面 Chromium 使用软件 WebGPU。它验证模型加载和渲染帧推进，不代表硬件 WebGPU 或移动端性能达标。
