import unittest
from waveform import Waveform


class TestWaveform(unittest.TestCase):

    def test_single_pad_audio_repeat(self, filenamepath: str='data\\0_0_0.wav'):
        waveform = Waveform(filenamepath)
        waveform.load_params()
        original_duration = waveform.get_duration()
        waveform.pad_audio_repeat(repeat_duration=2.0)
        waveform.load_params()
        modified_duration = waveform.get_duration()
        if modified_duration <= original_duration:
            print(f'Modified Duration: {modified_duration}, Original Duration: {original_duration}')
            assert False
        assert True

    
    def test_clip_audio(self, filenamepath: str='data\\0_0_0.wav'):
        waveform = Waveform(filenamepath)
        waveform.clip_audio(0.0, 2.0)
        waveform.load_params()
        modified_duration = waveform.get_duration()
        if modified_duration != 2:
            print(f'Modified Duration: {modified_duration}, Expected Duration: 2.0')
            assert False
        assert True
    

if __name__ == '__main__':
    unittest.main()