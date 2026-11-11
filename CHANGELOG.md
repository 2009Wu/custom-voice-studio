# v0.2.0 — 作品历史与歌曲试听

## v0.2.1 · 启动时自动更新

- 打开 Windows 工作室时，启动器自动检查并安装已发布的新版。通过 SHA-256 和文件清单校验后才会替换程序文件，完成后自动打开工作室。
- 更新在网页打开前进行。网络异常或检查超时后会继续启动，成功检查后六小时内跳过重复检查。
- “更新与帮助”可以关闭自动更新，也可以手动更新和回退。回退后，自动更新会等到发布更高版本。
- 已安装旧版的用户，在“更新与帮助”手动更新一次，或从发布页下载新版安装包。作品、收藏音色和模型缓存继续沿用。

Windows now checks for and installs verified releases before opening the studio. Use Updates & Help to switch automatic updates off, update manually, or roll back. Install this release once from the existing updater to enable the feature.

- 生成后自动保存作品，关闭程序后可从历史载入、试听和下载。
- 歌曲支持 10 / 15 / 20 秒试听，再沿用确认片段生成整首。
- 可选择最多 120 秒区间单独重做，新旧作品分别保留。
- 参考片段可先听、裁剪和收藏，下次直接选用。
- 两个工作室共用模型缓存，整理旧缓存时保留相同模型内容。
- 增加检查更新、下载校验、安装重启、回退和不含录音文字的诊断报告。

模型、参考素材、默认 40 步、音高、推理精度和混音默认值不变。物理 6 GB 显卡仍需更多实机验证，配置要求不变。

首次升级请下载下方完整 Windows ZIP，关闭启动器后覆盖原程序目录并保留 `.runtime`。不要只替换 EXE。以后的更新可在程序“更新与帮助”中完成。ZIP 不含模型权重，首次安装仍需联网下载数 GB。

作品保存在系统“文档”里的 Voice Studio作品。用于重做的素材保留 7 天、总量约 5 GB；最终作品不会自动删除。详细操作见 docs/作品与更新.md。

English: persistent works history, short cover previews with reuse, selected-interval redo, shared model cache, verified explicit updates and rollback. Custom edition also supports local voice favorites and reference trimming. Engines and default audio quality settings are unchanged.


# 更新日志

## v0.1.3 — 安装空间说明与进一步精简

- 明确 30 GB 是首次安装前的可用空间要求（含临时文件）；自选音色装好并缓存完整模型后实测约 11.25 GiB。
- 清理本程序不使用的上游演示界面、开发头文件和工具文档，当前环境再减少 183,939,829 字节，约 184 MB。
- 保留当前界面、许可文件、模型、运行 DLL、Python 与模型加速缓存；不改生成计算、精度、步数和导出设置。
- 完成后记录精简状态，下次启动不再扫描数千个文件；修复安装后自动重新清理。

English: Clarify temporary setup space versus installed size and trim unused demo assets, headers and tool manuals without changing the inference runtime or model settings.

## v0.1.2 — 精简安装体积

- 安装与启动时自动清理本程序不使用的 PyTorch 开发静态库和 ffplay 播放器，实测运行环境节省 980,103,826 字节（约 980 MB / 0.91 GiB）。不改模型权重、运行 DLL、精度、步数、音高和混音。保留模型缓存和 Python 缓存。安装时仍需预留 30 GB，首次仍会下载数 GB。
- 已验证两个程序的真实配音和翻唱；同一段自选配音在精简前后 WAV 逐字节一致。

English: Remove unused build-only files from the private inference runtime; preserve model weights, generation settings, runtime DLLs and caches.

## v0.1.1 — 桌面一键打开

- 首次运行和安装成功后自动创建中文桌面快捷方式；安装后双击直接启动并打开网页。
- 重复点击复用已有启动器；新增「创建 / 修复桌面快捷方式」，支持移动目录后修复入口。
- 桌面写入失败不会导致安装失败；不改变生成模型、参考音频或音质参数。

English: Automatic per-user desktop shortcuts, direct opening after setup, single-instance reuse and shortcut repair after moving the app folder.

## v0.1.0 — 自选参考人声

- 上传 MP3/MP4 等参考人声，输入文字或上传歌曲即可一键生成。
- 自动选取有声音的参考片段；文字语音自动在本机识别参考原话，也可手动修正。
- 中文界面、独立 Windows 安装器、6/8/12 GB 自动显存档位。
- 保留 40 步翻唱和人声突出混音，导出 MP3/无损 FLAC/WAV 和可选视频。
- 代码与运行目录独立，不附带固定人物参考录音。
