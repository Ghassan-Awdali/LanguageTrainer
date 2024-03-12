from pydub import AudioSegment
import os

class AudioFileConverter:
    def __init__(self, mp3_folder, wav_folder):
        self.mp3_folder = mp3_folder
        self.wav_folder = wav_folder
        
        if not os.path.exists(self.wav_folder):
            os.makedirs(self.wav_references)