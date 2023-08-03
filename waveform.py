import numpy as np
import soundfile as sf
import wave
import os

class Waveform:

    audio = None
    params = None
    filenamepath = None

    def __init__(self, filenamepath: str=None) -> None:
        if filenamepath is not None:
            self.read(filenamepath)
        pass


    def read(self, filenamepath: str=filenamepath):
        if self.audio is not None:
            self.close()
        self.filenamepath = filenamepath
        self.audio = wave.open(self.filenamepath, 'rb')


    def read_as_array(self, filenamepath: str=filenamepath):
        audio_np, _ = sf.read(filenamepath)
        return audio_np


    def write(self, filenamepath: str=filenamepath):
        if self.audio is not None:
            self.close()
        self.filenamepath = filenamepath
        self.audio = wave.open(self.filenamepath, 'wb')


    def overwrite(self, audio):
        self.write(self.filenamepath)
        self.audio.setparams(audio.getparams())
        self.audio.writeframes(audio.readframes(audio.getnframes()))


    def close(self):
        self.audio.close()
        self.audio = None

    
    def load_params(self):
        self.params = self.audio.getparams()


    def get_duration(self):
        return self.params.nframes / self.params.framerate


    def pad_audio_repeat(self, repeat_duration: float=1.0):
        if repeat_duration <= 0:
            raise ValueError("Repeat duration must be greater than 0.")
        
        self.load_params()
        audio_np = np.frombuffer(self.audio.readframes(self.params.nframes), dtype=np.int16)

        repeat_frames = int(self.params.framerate * repeat_duration)
        total_frames = len(audio_np) + repeat_frames

        repeated_audio_np = np.zeros(total_frames, dtype=np.int16)
        repeated_audio_np[:len(audio_np)] = audio_np

        repetitions = repeat_frames // len(audio_np)
        remainder_frames = repeat_frames % len(audio_np)
        for i in range(repetitions):
            repeated_audio_np[len(audio_np) + i * len(audio_np): len(audio_np) + (i + 1) * len(audio_np)] = audio_np

        repeated_audio_np[len(audio_np) + repetitions * len(audio_np): len(audio_np) + repetitions * len(audio_np) + remainder_frames] = audio_np[:remainder_frames]

        with wave.open('tempfile.wav', 'wb') as tempfile:
            tempfile.setparams(self.audio.getparams())
            tempfile.writeframes(repeated_audio_np.tobytes())

        with wave.open('tempfile.wav', 'rb') as tempfile:
            self.overwrite(tempfile)

        os.unlink('tempfile.wav')


    def clip_audio(self, startpos: float, clip_duration: float):
        if clip_duration <= 0:
            raise ValueError("Repeat duration must be greater than 0.")

        self.load_params()

        with wave.open('tempfile.wav', 'wb') as tempfile:
            tempfile.setparams(self.audio.getparams())
            tempfile.writeframes(self.audio.readframes(self.params.nframes))

        audio_np = self.read_as_array(self.filenamepath)

        start_frame = int(startpos * self.params.framerate)
        end_frame = min(start_frame + int(clip_duration * self.params.framerate), self.params.nframes)

        clipped_audio_np = audio_np[start_frame:end_frame]
        clipped_audio_data = clipped_audio_np.tobytes()

        clipped_audio_np = np.frombuffer(clipped_audio_data, dtype=np.float64)  # Assuming 24-bit PCM audio
        
        sf.write('tempfile.wav', clipped_audio_np, self.params.framerate, subtype='PCM_24')

        with wave.open('tempfile.wav', 'rb') as tempfile:
            self.overwrite(tempfile)

        os.unlink('tempfile.wav')
