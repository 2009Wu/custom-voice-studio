import sys,tempfile,unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference_audio import select_clip,prepare_reference
from audio_utils import ffmpeg


class ReferenceTests(unittest.TestCase):
    def test_long_silence_is_not_selected_instead_of_the_voice(self):
        rate=16000
        speech=.1*np.sin(2*np.pi*220*np.arange(rate*20)/rate)
        source=np.concatenate([np.zeros(rate*30),speech,np.zeros(rate*15)]).astype('float32')
        clip,start=select_clip(source,rate,20)
        self.assertGreaterEqual(start,29.8)
        self.assertLessEqual(start,30.2)
        self.assertGreater(len(clip)/rate,19)
        self.assertLessEqual(float(np.abs(clip).max()),.92001)

    def test_silence_short_and_nonfinite_references_fail(self):
        rate=16000
        for wave in [np.zeros(rate*5),np.ones(rate),np.full(rate*5,np.nan)]:
            with self.assertRaises(ValueError): select_clip(wave,rate)

    def test_mp4_reference_extracts_audio_and_validates_offset(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);rate=16000
            signal=.1*np.sin(2*np.pi*220*np.arange(rate*6)/rate)
            sf.write(root/'source.wav',signal,rate)
            ffmpeg(['-v','error','-f','lavfi','-i','color=c=black:s=160x90:r=10',
                    '-i',root/'source.wav','-shortest','-c:v','libx264','-pix_fmt','yuv420p',
                    '-c:a','aac',root/'reference.mp4'])
            reference,info=prepare_reference(root/'reference.mp4',root,start=1,seconds=5)
            self.assertTrue(reference.is_file())
            self.assertGreaterEqual(info['clip_start_seconds'],1)
            self.assertGreaterEqual(info['clip_duration_seconds'],3)
            self.assertLessEqual(info['clip_duration_seconds'],5)
            with self.assertRaises(ValueError): prepare_reference(root/'reference.mp4',root,start=100)
