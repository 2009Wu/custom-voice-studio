"""Custom Voice Studio: upload a voice, then text or a vocal song."""
import os
from pathlib import Path
import gradio as gr
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
    with gr.Blocks(title='自选音色工作室', delete_cache=(600, 3600)) as demo:
        gr.Markdown('# 自选音色工作室\n**上传参考人声 → 输入文字或放入歌曲 → 一键生成。**')
        with gr.Row(equal_height=False):
            with gr.Column(scale=6):
                reference = gr.File(label='1. 参考人声：想使用谁的声音', file_types=MEDIA, type='filepath')
                gr.Markdown('支持 MP3/MP4。推荐单人、少噪声、无背景音乐的清晰讲话；自动取一段有声音的参考片段。', elem_classes='hint')
                text = gr.Textbox(label='2A. 输入文字：用参考声音朗读', placeholder='输入想让这个声音说的话……', lines=4)
                song = gr.File(label='2B. 上传歌曲：用参考声音翻唱', file_types=MEDIA, type='filepath')
                gr.Markdown(f'2A / 2B 任选一种。文字最多 {MAX_TEXT} 字；歌曲最多 {MAX_SECONDS//60} 分钟，文件最多 {MAX_MB} MB。', elem_classes='hint')
                with gr.Accordion('高级选项（通常无需修改）', open=False):
                    performance = gr.Dropdown([('自动选择（推荐）','auto'),('6 GB 节省显存','low'),('8 GB 均衡','balanced'),('12 GB+ 性能优先','fast')], value='auto', label='性能档位')
                    steps = gr.Dropdown([('快速 · 20 步',20),('标准 · 40 步',40),('精细 · 60 步',60)], value=40, label='翻唱质量')
                    vocal_db = gr.Slider(-2,9,value=4.5,step=.5,label='人声响度（dB）')
                    music_db = gr.Slider(-12,3,value=-1.5,step=.5,label='伴奏响度（dB）')
                    video = gr.Checkbox(True,label='输入歌曲视频时同时导出 MP4')
                    language = gr.Dropdown(LANGUAGES,value='Chinese',label='生成语音的语言')
                    reference_start = gr.Number(value=0,minimum=0,maximum=3600,label='参考素材从第几秒开始寻找片段')
                    reference_seconds = gr.Dropdown([5,10,15,20,25],value=20,label='参考片段最长秒数')
                    reference_language = gr.Dropdown(LANGUAGES,value='Auto',label='参考讲话的语言')
                    reference_text = gr.Textbox(label='参考片段原话（留空自动识别）',lines=2,
                        placeholder='仅当知道所选片段的准确原话时填写；一般留空。')
                with gr.Row():
                    create = gr.Button('3. 一键生成',variant='primary',scale=3)
                    stop = gr.Button('停止',scale=1)
            with gr.Column(scale=5):
                status = gr.Textbox(label='进度',value='等待参考人声与文字／歌曲。',interactive=False)
                audio = gr.Audio(label='AI 生成试听',type='filepath',interactive=False)
                mp3 = gr.DownloadButton('下载 MP3 · 通用')
                flac = gr.DownloadButton('下载 FLAC · 无损')
                with gr.Accordion('更多下载',open=False):
                    wav = gr.DownloadButton('下载 WAV · 无损')
                    movie = gr.DownloadButton('下载 MP4 · 翻唱视频')
                    details = gr.DownloadButton('下载生成参数')
                with gr.Accordion('实际使用的参考片段与原话',open=False):
                    ref_preview = gr.Audio(label='原始参考片段（用于核对）',type='filepath',interactive=False)
                    ref_transcript = gr.Textbox(label='参考原话（自动识别或手动提供）',interactive=False,lines=3)
        gr.Markdown('首次使用会下载模型。参考素材和生成在本机处理。**生成作品为 AI 合成，不能作为本人真实录音。** 结果临时保留，请及时下载。',elem_classes='hint')
        event = create.click(generate,[reference,text,song,performance,steps,vocal_db,music_db,video,language,
                                      reference_start,reference_seconds,reference_text,reference_language],
                             [audio,mp3,flac,wav,movie,details,ref_preview,ref_transcript,status],
                             concurrency_limit=1,concurrency_id='gpu',api_name='generate')
        stop.click(lambda:'已停止，可以重新生成。',outputs=status,cancels=[event],queue=False,api_name=False)
    return demo


if __name__ == '__main__':
    build_app().queue(max_size=8,default_concurrency_limit=1).launch(
        server_name=os.getenv('HOST','127.0.0.1'),server_port=int(os.getenv('PORT','7870')),
        theme=gr.themes.Soft(primary_hue='teal',neutral_hue='slate'),css=CSS,max_file_size=f'{MAX_MB}mb',
        show_error=False,blocked_paths=[str(CACHE),str(ROOT/'vendor'),str(ROOT/'.runtime')],footer_links=[])
