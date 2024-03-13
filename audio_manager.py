
import os
import sounddevice as sd
import soundfile as sf
import contextlib
import numpy as np
import wave
import matplotlib.pyplot as plt



class AudioManager():
    
    def __init__(self):
        self.SAMPLE_RATE = 44100 #Hz
        self.CWD = os.getcwd() # Fetches current directory
        
    def record_mic(self,duration,out_path):
        """Records mic for duration and saves to output file"""
        print("recording...")
        out_aud = sd.rec(int(self.SAMPLE_RATE * duration), samplerate = self.SAMPLE_RATE, channels = 1,blocking = True)
        sf.write(out_path,out_aud,self.SAMPLE_RATE)
        
    def get_aud_length(self,f_path,milleseconds = False):
        with contextlib.closing(wave.open(f_path,"r")) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            dur = frames / float(rate)
            if milleseconds:
                dur = dur * 1000
            return dur
    
    def create_wav_img(self,in_path,out_path,color="red",graph_dim=(20,5)):
        """Creates a waveform image from a .wav file."""

        f_title = os.path.basename(in_path).split('.')[0]

        spf = wave.open(in_path,"r")

        fs = spf.getframerate()

        # extract the raw audio from wav
        signal = spf.readframes(-1) #-1 means read all frames
        signal = np.frombuffer(signal,"int16")
        
        # get the time length
        time_length = np.linspace(0, len(signal) / fs, num=len(signal))



        # graph formatting
        plt.figure(figsize=graph_dim)
        plt.rc('font',family = "Meiryo")

        plt.title("Audio: {}".format(f_title))
        plt.plot(time_length,signal,color)
        plt.xlabel('Time [sec]')
        
        plt.savefig(out_path,bbox_inches='tight')
        print("Created Image")
        
        
#test = AudioManager()       
#record_mic(3,"my_recordings\mic_record.wav")
#print(test.get_aud_length("my_recordings\mic_record.wav"))
#test.create_wav_img("my_recordings\mic_record.wav","my_recordings\mic_waveform.png")