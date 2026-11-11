"""Custom Voice Studio: upload a voice, then text or a vocal song."""
import os
from pathlib import Path
import gradio as gr
from studio_paths import public_output_paths
from runner import run_job
from settings import CACHE, LANGUAGES, MAX_MB, MAX_SECONDS, MAX_TEXT, ROOT

MEDIA = ['.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mov', '.aac', '.mkv']
CSS = '.gradio-container {max-width:1120px!important;margin:auto} footer {display:none!important}.hint {color:#64748b;font-size:13px}'


def checked_media(value, label):
    if not value:
        raise ValueError(f'请先上传{label}。')
    path = Path(value)
    if not path.is_file() or path.stat().st_size > MAX_MB * 1024**2:
        raise ValueError(f'{label}必须是一个不超过 {MAX_MB} MB 的文件。')
    if path.suffix.lower() not in MEDIA:
        raise ValueError(f'{label}格式不支持，请使用 MP3、MP4、WAV、M4A 或 FLAC 等。')
    return str(path.resolve())


def make_request(reference, text, song, performance='auto', steps=40, vocal_db=4.5,
                 music_db=-1.5, video=True, language='Chinese', reference_start=0,
                 reference_seconds=20, reference_text='', reference_language='Auto'):
    reference = checked_media(reference, '参考人声')
    text = (text or '').strip()
    if bool(text) == bool(song):
        raise ValueError('输入要朗读的文字，或上传要翻唱的歌曲；一次只选择一种。')
    if len(text) > MAX_TEXT:
        raise ValueError(f'文字最多 {MAX_TEXT} 字。')
    if language not in LANGUAGES or reference_language not in LANGUAGES:
        raise ValueError('请选择支持的语言。')
    start, seconds = float(reference_start), float(reference_seconds)
    if not (0 <= start <= 3600 and 5 <= seconds <= 25):
        raise ValueError('参考起点应为 0–3600 秒，参考长度应为 5–25 秒。')
    if len(reference_text or '') > 1000:
        raise ValueError('参考片段原话最多 1000 字。')
    request = {'mode': 'speak' if text else 'sing', 'reference_input': reference,
               'reference_start': start, 'reference_seconds': seconds,
               'reference_text': (reference_text or '').strip(), 'reference_language': reference_language,
               'performance': performance, 'steps': steps, 'vocal_db': vocal_db,
               'music_db': music_db, 'video': video, 'language': language}
    if text:
        request['text'] = text
    else:
        request['input'] = checked_media(song, '歌曲')
    return request


def generate(reference, text, song, performance, steps, vocal_db, music_db, video,
             language, reference_start, reference_seconds, reference_text, reference_language,
             progress=gr.Progress()):
    try:
        request = make_request(reference, text, song, performance, steps, vocal_db, music_db,
                               video, language, reference_start, reference_seconds, reference_text, reference_language)
        yield None, None, None, None, None, None, None, '', '正在准备参考人声…'
        for fraction, message, result in run_job(request):
            progress(fraction, desc=message)
            if result:
                yield (result['audio'], result['audio'], result['flac'], result['wav'], result['video'],
                       result['details'], result['reference'], result.get('reference_text', ''), message)
            else:
                yield *(gr.skip() for _ in range(8)), message
    except Exception as error:
        raise gr.Error(str(error)) from error


def build_app():
    from studio_ui import build_app as build_shared
    return build_shared(globals())


if __name__ == '__main__':
    build_app().queue(max_size=8,default_concurrency_limit=1).launch(
        server_name=os.getenv('HOST','127.0.0.1'),server_port=int(os.getenv('PORT','7870')),
        theme=gr.themes.Soft(primary_hue='teal',neutral_hue='slate'),css=CSS,max_file_size=f'{MAX_MB}mb',
        show_error=False,allowed_paths=public_output_paths(),blocked_paths=[str(CACHE),str(ROOT/'vendor'),str(ROOT/'.runtime')],footer_links=[])
