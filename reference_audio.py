"""Local reference-clip selection; never uses a bundled person's voice."""
import math
from pathlib import Path
import numpy as np
import soundfile as sf
from audio_utils import FORMATS, ffmpeg, probe


def select_clip(audio, rate, seconds=20):
    audio = np.asarray(audio, dtype='float32')
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if not np.isfinite(audio).all() or len(audio) < rate * 3:
        raise ValueError('参考人声至少需要 3 秒有效音频，推荐 10–25 秒清晰单人讲话。')
    frame = max(1, int(rate * .04))
    count = len(audio) // frame
    rms = np.sqrt(np.mean(audio[:count*frame].reshape(count,frame).astype('float64')**2,axis=1))
    if np.max(rms) < 0.0001:
        raise ValueError('参考素材几乎没有声音，请选择清晰讲话片段。')
    threshold = max(.0015, float(np.percentile(rms,90))*.08)
    active = rms > threshold
    width = min(count, max(1,int(seconds*rate)//frame))
    if count > width:
        scores = np.convolve(active.astype(float),np.ones(width),mode='valid')
        # Penalize clipping without favoring an isolated loud spike.
        clipped = np.mean(np.abs(audio[:count*frame].reshape(count,frame))>.98,axis=1)
        scores -= 2*np.convolve(clipped,np.ones(width),mode='valid')
        first = int(np.argmax(scores))
    else:
        first = 0
    last = min(count,first+width)
    voiced = np.flatnonzero(active[first:last])
    if len(voiced)*.04 < 1.5:
        raise ValueError('参考片段里有效声音太少，请调整参考起点或换一段讲话。')
    begin = max(first,first+int(voiced[0])-3)*frame
    end = min(len(audio), (first+int(voiced[-1])+4)*frame, (first+width)*frame)
    clip = audio[begin:end].copy()
    if len(clip) < rate*3:
        raise ValueError('选出的参考声音不足 3 秒，请提供更长的单人讲话。')
    clip -= np.mean(clip)
    rms_value = float(np.sqrt(np.mean(clip.astype('float64')**2)))
    gain = min(.1/max(rms_value,1e-8), .92/max(float(np.max(np.abs(clip))),1e-8), 20)
    return clip*gain, begin/rate


def prepare_reference(source, job, start=0, seconds=20, max_mb=500):
    source = Path(source).resolve(strict=True)
    start,seconds=float(start),float(seconds)
    if not source.is_file() or source.stat().st_size > max_mb*1024**2:
        raise ValueError(f'参考素材不能超过 {max_mb} MB。')
    if not math.isfinite(start) or not math.isfinite(seconds) or not (0<=start<=3600 and 5<=seconds<=25):
        raise ValueError('参考起点或片段长度不正确。')
    metadata = probe(source)
    duration=float(metadata.get('format',{}).get('duration',0))
    if not math.isfinite(duration) or duration-start<3:
        raise ValueError('参考起点之后需要至少 3 秒音频。')
    scan=job/'reference-scan.wav'
    ffmpeg(['-v','error','-protocol_whitelist','file,pipe','-format_whitelist',FORMATS,
            '-ss',str(start),'-i',source,'-t',str(min(90,duration-start)),
            '-map','0:a:0','-vn','-ac','1','-ar','44100','-c:a','pcm_f32le',scan])
    audio,rate=sf.read(scan,dtype='float32')
    clip,offset=select_clip(audio,rate,seconds)
    target=job/'reference.wav'
    sf.write(target,clip,rate,subtype='PCM_24')
    return target, {'source_duration_seconds':duration,'clip_start_seconds':round(start+offset,3),
                    'clip_duration_seconds':round(len(clip)/rate,3),'sample_rate':rate}
