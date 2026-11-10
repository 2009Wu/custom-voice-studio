# Custom Voice Studio

[中文完整说明](README.md)

Upload a reference voice (MP3/MP4/WAV/M4A/FLAC), then enter text OR upload an existing vocal song, and click Generate. No fixed person's reference or separate speaker training is used.

Extract Custom-Voice-Studio-Windows.zip completely, run Start Custom Voice Studio.exe and click 安装并打开工作室 (Set up and open). Keep the launcher open. Advanced settings are optional.

For TTS, an internal CPU Whisper process transcribes the selected reference clip, then Qwen3-TTS 0.6B Base generates the requested text using that clip and transcript. Transcription can be corrected manually in advanced settings. Singing uses Seed-VC with the uploaded reference and Demucs separation. Default 40 steps, pitch and vocal-forward mix are preserved.

Use a clear, single-speaker reference of at least 3 seconds. The app scans up to 90 seconds after the selected start and chooses an active clip, by default up to 20 seconds. This is energy-based selection, not speaker diarization. Multiple speakers, noise or background music can reduce similarity. Instrumental-only songs do not create singing or lyrics.

Requires Windows 10/11 x64, a 6 GB-class or larger NVIDIA CUDA GPU and driver, recommended 16 GB RAM and 30 GB free setup disk space. Physical 6 GB hardware remains unvalidated. Memory profiles trade CPU work/transfers for GPU memory. See VALIDATION.md for actual checks.

Independent app runtime/models live in .runtime/.cache. No system Python or external inference API is used. First setup/model downloads require internet. Defaults to localhost port 7870. Outputs are temporary: save MP3, lossless FLAC/WAV and optional MP4 promptly.

Software is GPL-3.0, derived from Wang Hongwen Voice Studio v0.3.0. Upstream code/model notices are in THIRD_PARTY_NOTICES.md. No personal voice reference or model weights are bundled in the ZIP. All generated audio is synthetic, not an authentic recording.

## Desktop shortcut

First launcher run and successful setup create a current-user desktop shortcut. After setup, double-click it to start the local server and open the studio directly. A second click reuses the running instance. Keep the extracted app folder. After moving it, run the EXE from the new location or use 创建 / 修复桌面快捷方式 (Create / repair desktop shortcut). Downloading a ZIP alone does not execute the app. Desktop permission errors do not invalidate installation.

## 安装体积 / Disk use

安装与启动时自动清理本程序不使用的 PyTorch 开发静态库和 ffplay 播放器，实测运行环境节省 980,103,826 字节（约 980 MB / 0.91 GiB）。不改模型权重、运行 DLL、精度、步数、音高和混音。保留模型缓存和 Python 缓存。安装时仍需预留 30 GB，首次仍会下载数 GB。

开发者需要编译自定义 C++ 扩展时，请另建完整开发环境；启动器维护的是配音和翻唱所需的推理环境。升级时先保存结果、关闭启动器，把新 ZIP 完整解压覆盖回原位置，可保留 `.runtime` 和 `.cache`；下次打开会自动精简。请勿只复制 EXE。
