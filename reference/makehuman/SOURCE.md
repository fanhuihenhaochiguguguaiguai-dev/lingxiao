# MakeHuman 图形资产来源

- `base.obj` 与两个 `.target` 来自 MakeHuman 官方仓库 `makehuman/data/3dobjs` 和 `makehuman/data/targets/macrodetails`。
- `young_male_diffuse.png` 从 MakeHuman 官方 [CC0 system assets](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) 中的 `skins/young_asian_male/young_lightskinned_male_diffuse3.png` 获取；通过 HTTP Range 只下载需要的文件。
- 图形资产许可：本目录 `LICENSE.ASSETS.md`（CC0）。保留原作者与许可信息。

- 本轮新增 `chin_*`、`cheek_*` 形变目标，同样来自 MakeHuman 官方 `makehuman/data/targets/chin` 与 `cheek` 目录，按 CC0 资产许可使用。

- 鼻唇候选使用 `nose-width1-decr`、`nose-width2-decr`、`nose-flaring-decr`、`mouth-lowerlip-volume-decr` 和 `mouth-scale-vert-decr`，同样来自官方 `makehuman/data/targets/nose` 与 `mouth` 的 CC0 图形资产；该候选未应用于正式母版。

- 清璃静态研究使用的 `asian-female-young.target` 与 `universal-female-young-averagemuscle-averageweight.target` 同样是 MakeHuman CC0 资产，与此目录现有 `base.obj` 配套；未使用校园角色的照片投影面部。

- 本轮面部实验使用 `eyes/{l,r}-eye-scale-incr.target`、`eyes/{l,r}-eye-height1-incr.target` 及 `head/head-oval.target`，来自 MakeHuman 官方代码仓库的 `makehuman/data/targets`，使用本目录 CC0 资产许可。
- `young_asian_female_diffuse.png` 是官方 CC0 system assets 中 `skins/young_asian_female/young_lightskinned_female_diffuse3.png` 的原始通用皮肤贴图；按基础网格的原始 UV 使用，不是清璃的专属面部贴图。
- `long01.obj`、`long01.mhclo` 和 `long01_diffuse.png` 是官方 CC0 system assets 中 `hair/long01/` 的网格、拟合权重和纹理。源文件署名 Data Collection AB、Joel Palmius 和 Jonas Hauquier，明确声明 CC0。`long01_silver_study.png` 是以 `tools/prepare_qingli_hair_texture.py` 改成银蓝色的派生纹理，保留原图的透明度；这是一份通用发型，非清璃原始造型。
