"""Separate GPU process for each job; exiting releases all model memory."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from settings import CACHE, LANGUAGES, MAX_MB, MAX_SECONDS, MAX_TEXT, SING_PYTHON


def emit(fraction, message):
    print("@@PROGRESS " + json.dumps({"fraction": fraction, "message": message}), flush=True)


def prepare_environment():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, suffix in [("HF_HOME", "huggingface"), ("TORCH_HOME", "torch"), ("NUMBA_CACHE_DIR", "numba")]:
        os.environ.setdefault(name, str(CACHE / suffix))
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    import torch
    torch.set_num_threads(int(os.getenv("CPU_THREADS", "4")))
    if not torch.cuda.is_available():
        if os.getenv("VOICE_STUDIO_DESKTOP") == "1":
            raise RuntimeError("A CUDA GPU is required. Update the NVIDIA driver and use Repair setup in the launcher.")
        raise RuntimeError("A CUDA GPU is required. Select GPU hardware in the Space Settings and restart.")
    torch.manual_seed(42)


def separate(source_path, job, policy):
    import gc
    import torch
    import numpy as np
    import soundfile as sf
    from demucs.api import Separator
    emit(.08, "正在分离人声和伴奏…")
    separator = Separator(model="htdemucs", device="cpu" if policy["profile"] == "low" else "cuda", shifts=1, progress=False)
    _, stems = separator.separate_audio_file(source_path)
    vocals = stems["vocals"].cpu().numpy().T
    music = sum(v for k, v in stems.items() if k != "vocals").cpu().numpy().T
    sf.write(job / "original-vocals.wav", vocals, 44100, subtype="FLOAT")
    sf.write(job / "instrumental.wav", music, 44100, subtype="FLOAT")
    del separator, stems
    gc.collect()
    torch.cuda.empty_cache()
    return vocals.mean(axis=1).astype("float32"), music.astype("float32")


def sing(request, job):
    from studio_song import generate_song
    return generate_song(request, job, emit, separate)


def speak(request, job):
    import numpy as np
    import soundfile as sf
    import torch
    from huggingface_hub import snapshot_download
    from qwen_tts import Qwen3TTSModel
    from audio_utils import split_text, master, export_mp3
    text = str(request.get("text", "")).strip()
    language = request.get("language", "Chinese")
    if not text or len(text) > MAX_TEXT or language not in LANGUAGES:
        raise ValueError(f"Enter 1–{MAX_TEXT} characters and choose a supported language.")
    emit(.04, "正在载入语音模型（首次使用需下载）…")
    manifest = json.loads((ROOT / "models.json").read_text(encoding="utf-8"))
    # Hub 0.36's first symlink-support probe is not thread-safe on Windows.
    # Download serially so normal users use the supported file-copy fallback.
    model_path = snapshot_download(manifest["tts"]["repo"], revision=manifest["tts"]["revision"],
                                   max_workers=1 if os.name == "nt" else 8)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = Qwen3TTSModel.from_pretrained(model_path, device_map="cuda:0", dtype=dtype, attn_implementation="sdpa")
    prompt = model.create_voice_clone_prompt(ref_audio=request["_reference_path"],
                                            ref_text=request["_reference_text"], x_vector_only_mode=False)
    chunks = split_text(text)
    audio = []
    rate = None
    for i, part in enumerate(chunks):
        emit(.2 + .65 * i / len(chunks), f"正在朗读 {i + 1}/{len(chunks)}…")
        torch.manual_seed(42 + i)
        waves, rate = model.generate_voice_clone(text=part, language=language, voice_clone_prompt=prompt,
                                                 max_new_tokens=1536)
        wave = np.asarray(waves[0], dtype="float32").reshape(-1)
        if not len(wave) or not np.isfinite(wave).all():
            raise RuntimeError("The speech model returned invalid audio")
        # A full token budget usually indicates truncation: don't silently return missing words.
        if len(wave) / rate >= 125:
            raise RuntimeError("This sentence took too long to read. Use shorter sentences and try again.")
        if audio:
            audio.append(np.zeros(int(rate * .18), dtype="float32"))
        audio.append(wave)
    raw = job / "speech-raw.wav"
    sf.write(raw, np.concatenate(audio), rate, subtype="FLOAT")
    public = job / "results"
    public.mkdir(exist_ok=True)
    wav, mp3 = public / "Custom-Voice-AI-speech.wav", public / "Custom-Voice-AI-speech.mp3"
    emit(.9, "正在导出语音…")
    master(raw, wav, rate=rate, target=-16)
    export_mp3(wav, mp3)
    from audio_utils import export_flac
    flac = wav.with_suffix(".flac")
    export_flac(wav, flac)
    details = {"ai_generated": True, "engine": manifest["tts"]["repo"], "language": language,
               "characters": len(text), "chunks": len(chunks), "sample_rate": rate}
    (public / "generation.json").write_text(json.dumps(details, indent=2), encoding="utf-8")
    return {"audio": str(mp3), "wav": str(wav), "flac": str(flac), "video": None, "details": str(public / "generation.json")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    job = args.request.resolve().parent
    prepare_environment()
    from performance import configure, memory_report
    request["_policy"] = configure(request)
    emit(.01, "自动性能档位：" + request["_policy"]["label"])
    started = time.monotonic()
    if request.get("mode") not in {"sing", "speak"}:
        raise ValueError("未知任务类型。")
    from reference_audio import prepare_reference
    emit(.015, "正在从上传素材中选取参考人声…")
    if request.get("reference_prepared"):
        from reference_audio import use_prepared
        reference_path, reference_info = use_prepared(request["reference_input"], job)
    else:
        reference_path, reference_info = prepare_reference(request["reference_input"], job,
            request.get("reference_start", 0), request.get("reference_seconds", 20), MAX_MB)
    request["_reference_path"] = str(reference_path)
    transcript_method = "not_needed"
    request["_reference_text"] = ""
    if request["mode"] == "speak":
        request["_reference_text"] = str(request.get("reference_text", "")).strip()
        if len(request["_reference_text"]) > 1000:
            raise ValueError("参考片段原话最多 1000 字。")
        transcript_method = "manual" if request["_reference_text"] else "automatic"
        if not request["_reference_text"]:
            emit(.025, "正在本机识别参考片段原话（首次可能下载识别组件）…")
            transcript_path = job / "reference-transcript.json"
            options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
            completed = subprocess.run([SING_PYTHON, "-u", str(ROOT / "ref_asr.py"),
                str(reference_path), str(transcript_path), "--language", request.get("reference_language", "Auto")],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900, **options)
            if completed.returncode:
                print(completed.stderr[-2500:], flush=True)
                raise RuntimeError("参考原话识别失败，请检查网络或换一段清晰讲话；也可在高级选项填写所选片段的准确原话。")
            request["_reference_text"] = json.loads(transcript_path.read_text(encoding="utf-8"))["text"].strip()
            if not request["_reference_text"]:
                raise ValueError("没有识别到参考讲话，请换一个片段。")
    result = sing(request, job) if request["mode"] == "sing" else speak(request, job)
    public_reference = Path(result["details"]).parent / "reference-used.wav"
    shutil.copy2(reference_path, public_reference)
    result["reference"] = str(public_reference)
    result["reference_text"] = request["_reference_text"]
    result["elapsed_seconds"] = round(time.monotonic() - started, 1)
    details_path = Path(result["details"])
    details = json.loads(details_path.read_text(encoding="utf-8"))
    details["reference_clip"] = reference_info
    details["reference_transcript_source"] = transcript_method
    details["performance"] = memory_report(request["_policy"])
    details["elapsed_seconds"] = result["elapsed_seconds"]
    details_path.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    (job / "result.json").write_text(json.dumps(result), encoding="utf-8")
    emit(1, "已完成 · AI 生成音频")


if __name__ == "__main__":
    main()
