"""Internal CPU transcript for the reference prompt, not a user ASR feature."""
import argparse,json,os
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('audio',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--language',default='Auto')
    args=parser.parse_args()
    from settings import CACHE,ROOT
    os.environ.setdefault('HF_HOME',str(CACHE/'huggingface'))
    import torch,torchaudio,soundfile as sf
    from transformers import WhisperProcessor,WhisperForConditionalGeneration
    torch.set_num_threads(int(os.getenv('CPU_THREADS','4')))
    manifest=json.loads((ROOT/'models.json').read_text(encoding='utf-8'))['whisper']
    processor=WhisperProcessor.from_pretrained(manifest['repo'],revision=manifest['revision'])
    model=WhisperForConditionalGeneration.from_pretrained(manifest['repo'],revision=manifest['revision'],
        torch_dtype=torch.float32,low_cpu_mem_usage=True).eval().to('cpu')
    wave,rate=sf.read(args.audio,dtype='float32')
    if wave.ndim>1:wave=wave.mean(axis=1)
    if rate!=16000:wave=torchaudio.functional.resample(torch.from_numpy(wave),rate,16000).numpy()
    inputs=processor(wave,sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
    options={'task':'transcribe','do_sample':False,'max_new_tokens':384}
    if args.language!='Auto':options['language']=args.language.lower()
    with torch.inference_mode():
        tokens=model.generate(**inputs,**options)
    text=processor.batch_decode(tokens,skip_special_tokens=True)[0].strip()
    if not text or len(text)>1000:
        raise ValueError('无法识别参考讲话，请换清晰片段，或在高级选项填写片段原话。')
    args.output.write_text(json.dumps({'text':text},ensure_ascii=False),encoding='utf-8')


if __name__=='__main__':main()
