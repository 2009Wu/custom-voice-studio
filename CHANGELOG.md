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
