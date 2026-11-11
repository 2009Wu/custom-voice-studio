# 本地 API

Gradio `/generate` 参数按顺序为：reference, text, song, performance, steps, vocal_db, music_db, video, language, reference_start, reference_seconds, reference_text, reference_language。

reference 必填，text/song 二选一。文件使用 gradio_client.handle_file。默认：auto, 40, 4.5, -1.5, true, Chinese, 0, 20, 空字符串, Auto。

返回：试听 MP3、MP3、FLAC、WAV、MP4（可能为空）、参数 JSON、实际原始参考片段 WAV、参考原话、状态。所有任务共用一个 GPU 队列。

Worker 的 reference_input 必填，不会回退到任何内置人物参考。请求、解码文件和参考识别临时文件在任务结束后删除，导出和用于核对的参考片段按保留期限清理。


## 持久化与新界面

旧 `/generate` 参数及返回顺序保留。新 `/create`、`/preview`、`/redo` 由界面调用，包含会话状态；程序集成建议继续使用 `/generate`。导出文件现在自动保存到持久作品目录；可修改素材按 7 天、约 5 GB 的预算清理，上传与参考原话仍只在本机私有目录处理。旧临时下载 URL 的缓存期限不等于本机作品文件的保存期限。
