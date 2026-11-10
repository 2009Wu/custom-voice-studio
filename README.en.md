# Custom Voice Studio

[使用说明](README.md) · [Windows download](https://github.com/2009Wu/custom-voice-studio/releases/latest/download/Custom-Voice-Studio-Windows.zip) · [Hugging Face](https://huggingface.co/spaces/Little-Wang/custom-voice-studio)

Upload a reference voice (MP3/MP4/WAV/M4A/FLAC), then enter text OR upload an existing vocal song, and click Generate. No fixed person's reference or separate speaker training is used.

Extract Custom-Voice-Studio-Windows.zip completely, run Start Custom Voice Studio.exe and click 安装并打开工作室 (Set up and open). Keep the launcher open. Advanced settings are optional.

For TTS, an internal CPU Whisper process transcribes the selected reference clip, then Qwen3-TTS 0.6B Base generates the requested text using that clip and transcript. Transcription can be corrected manually in advanced settings. Singing uses Seed-VC with the uploaded reference and Demucs separation. Default 40 steps, pitch and vocal-forward mix are preserved.

Use a clear, single-speaker reference of at least 3 seconds. The app scans up to 90 seconds after the selected start and chooses an active clip, by default up to 20 seconds. This is energy-based selection, not speaker diarization. Multiple speakers, noise or background music can reduce similarity. Instrumental-only songs do not create singing or lyrics.

Requires Windows 10/11 x64, a 6 GB-class or larger NVIDIA CUDA GPU and driver, recommended 16 GB RAM and 30 GB free setup disk space. Physical 6 GB hardware remains unvalidated. Memory profiles trade CPU work/transfers for GPU memory. See VALIDATION.md for actual checks.

Independent app runtime/models live in .runtime/.cache. No system Python or external inference API is used. First setup/model downloads require internet. Defaults to localhost port 7870. Outputs are temporary: save MP3, lossless FLAC/WAV and optional MP4 promptly.

Software is GPL-3.0, derived from Wang Hongwen Voice Studio v0.3.0. Upstream code/model notices are in THIRD_PARTY_NOTICES.md. No personal voice reference or model weights are bundled in the ZIP. All generated audio is synthetic, not an authentic recording.

![一键生成界面 / App preview](docs/app-preview.png)

## Desktop shortcut

First launcher run and successful setup create a current-user desktop shortcut. After setup, double-click it to start the local server and open the studio directly. A second click reuses the running instance. Keep the extracted app folder. After moving it, run the EXE from the new location or use 创建 / 修复桌面快捷方式 (Create / repair desktop shortcut). Downloading a ZIP alone does not execute the app. Desktop permission errors do not invalidate installation.

## Disk use

Setup/startup removes only unused PyTorch build-time `.lib` files and `ffplay.exe` from this app’s private runtime. The measured saving on the pinned Windows runtime is 980,103,826 bytes (0.91 GiB). Model tensors, runtime DLLs, bytecode caches, precision, inference settings and export formats are unchanged. The self-contained development compiler/linker workflow is not part of this inference runtime; developers needing custom C++ extensions should use a separate full PyTorch environment. Reserve 30 GB during setup.
