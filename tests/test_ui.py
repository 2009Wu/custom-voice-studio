import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try: import app
except ImportError: app=None


@unittest.skipIf(app is None,'Requires the UI environment')
class CustomInputTests(unittest.TestCase):
    def test_reference_is_required_and_text_song_are_exclusive(self):
        with self.assertRaises(ValueError):app.make_request(None,'你好',None)
        with tempfile.NamedTemporaryFile(suffix='.mp3') as reference:
            for text,song in [('',None),('你好','song.mp3')]:
                with self.assertRaises(ValueError):app.make_request(reference.name,text,song)

    def test_uploaded_reference_is_carried_into_both_modes(self):
        with tempfile.NamedTemporaryFile(suffix='.mp4') as reference,tempfile.NamedTemporaryFile(suffix='.mp3') as song:
            speech=app.make_request(reference.name,'你好',None)
            singing=app.make_request(reference.name,'',song.name)
            self.assertEqual(speech['reference_input'],str(Path(reference.name).resolve()))
            self.assertEqual(speech['mode'],'speak')
            self.assertEqual(singing['mode'],'sing')
            self.assertEqual(singing['steps'],40)
            self.assertEqual(singing['reference_input'],speech['reference_input'])

    def test_invalid_reference_options_are_rejected_before_starting_a_job(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3') as reference:
            for values in [{'reference_start':-1},{'reference_start':float('nan')},{'reference_seconds':50}]:
                with self.assertRaises(ValueError):app.make_request(reference.name,'你好',None,**values)
