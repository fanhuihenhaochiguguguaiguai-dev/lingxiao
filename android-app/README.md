# 凌渊角色与技能展示应用：安卓构建工作稿

应用包名候选为 `com.yaojing.lingyuan`，最低 Android 8.0（API 26）。应用通过本机受限 HTTP 服务在已安装的兼容浏览器中打开 `dist/skill`，并非完整对局游戏；角色和技能仍未通过美术验收。服务、前台通知和浏览器在真实 Android 系统上的行为尚未验证。

在具备 Node、JDK 17 和 Android SDK 35 的环境中：

```sh
python android-app/build_unsigned.py
python android-app/verify_package.py
```

可通过 `ANDROID_SDK_ROOT` 和 `JAVA_HOME` 指定工具链。构建结果为 `android-app/build/unsigned-aligned.apk`。这是未签名包，**无法安装**；校验和及桌面软件渲染证据在 `verification/android-build/`。构建脚本不会创建密钥或签名。仓库内没有旧版签名密钥，不能对现有应用进行同签名升级；采用新密钥和新包名作为独立安装应用，需遵守用户此前要求的确认。真实 Android 安装与移动性能仍待验证。
