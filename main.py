from audio_converter import AudioFileConverter
from audio_manager import AudioManager
from colors import *
import pygame as pg
from PIL import Image
import time
import os
import send2trash
import threading
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf



class App():
    def __init__(self):
        #pygame's init
        pg.init()
        pg.font.init()
        pg.mixer.init()
        pg.mixer.set_num_channels(8)
        
        #create channels
        self.REF_AUD_CHAN = pg.mixer.Channel(5)
        self.YOUR_AUD_CHAN = pg.mixer.Channel(3)
        
        #clock for time reference
        self.CLOCK = pg.time.Clock()
        self.FPS = 30
        
        #files references/variables
        self.CWD = os.getcwd()
        self.WAV_REF_FLDER = os.path.join(self.CWD, "wav_references")
        self.WAV_IMG_REF_FLDER = os.path.join(self.CWD, "wav_img_references")
        self.MY_REC_FLDER = os.path.join(self.CWD, "my_recordings")
        
        #pygame window attributes
        DISPLAY_W, DISPLAY_Y = pg.display.Info().current_w, pg.display.Info().current_h
        self.WIN_X = int(DISPLAY_W)
        self.WIN_Y = int(DISPLAY_Y)
        self.WIN = pg.display.set_mode((self.WIN_X, self.WIN_Y))
        pg.display.set_caption("Language Trainer")
        self.FONT = pg.font.SysFont('Comic Sans MS',35)
        self.AUD_IMG_CENTER = (int(self.WIN_X//2),int(self.WIN_Y * 0.75)) #png of the audio
        
        # for the audio / img changes
        self.REF_NAME = None
        self.REF_AUD = None
        self.REF_IMG= None
     
        
        # for timing the audio
        self.AUD_FINISHED = False
        self.PLAYING_AUD = False
        self.CURRENT_AUD = None
        self.AUD_FIN_EVENT = pg.USEREVENT + 1
        
        # for when you record on your mic
        self.OUT_AUD_PATH = None
        self.OUT_AUD_IMG = None
        self.OUT_AUD_IMG_RECT = None
        
        # for indexing the audio
        self.AUD_INDEX = 0
        self.IS_RECORDING = False
        self.REC_AUD_PRESENT = False
        
        # for audio managing
        self.AUD_MAN = AudioManager()

        self.RUNNING = True
        
    def get_pg_img(self,f_path):
        return pg.image.load(f_path)
    
    def get_img_size(self,f_path):
        img = Image.open(f_path)
        return img.size #returns tuple(w,h)
    
    def img_create(self, found_aud_path, f_name):
        time.sleep(.5)
        self.AUD_MAN.create_wav_img(found_aud_path, f_name, color = "red")
        self.OUT_AUD_IMG = self.get_pg_img(f_name)
        self.OUT_AUD_IMG_RECT = self.OUT_AUD_IMG.get_rect(center=(int(self.WIN_X//2),int(self.WIN_Y * 0.3)))
    
        
    def delete_recordings(self,your_rec_dir):
        if(len(your_rec_dir) !=0):
            for f in your_rec_dir:
                working_path = os.path.join(self.MY_REC_FLDER,f)
                send2trash.send2trash(working_path)
                
    def select_reference_audio(self):
        # Get a list of WAV files in the folder
        wav_files = [f for f in os.listdir(self.WAV_REF_FLDER) if f.endswith('.wav')]
        if wav_files:
            # Choose the first WAV file in the list as reference audio
            return os.path.join(self.WAV_REF_FLDER, wav_files[0])
                
    def run(self):
        #start by deleting all prior recordings
        my_recording_dir = os.listdir(self.MY_REC_FLDER)
        self.delete_recordings(my_recording_dir)

        quick_controls_text = self.FONT.render("R to record your mic. P to play recording.",False,(0,0,0))
        aud_finished_text = self.FONT.render("Audio finished recording..", False, (255,0,0))
        
        
        while self.RUNNING:
            #check if recording file has been updated
            my_recording_dir = os.listdir(self.MY_REC_FLDER)
            
            self.WIN.fill(WHITE)
            self.WIN.blit(quick_controls_text,(15,0))
            
            if len(my_recording_dir)!=0 and self.REC_AUD_PRESENT != True:
                for f in my_recording_dir:
                    if os.path.splitext(f)[-1] == ".wav":
                        self.REC_AUD_PRESENT = True
                        rec_aud_path = os.path.join(self.MY_REC_FLDER,f)
                        f_name = "recording-{}.png".format(self.REF_NAME)
                        f_path = os.path.join(self.MY_REC_FLDER,f_name)

                        threading.Thread(target=self.img_create,args=[rec_aud_path,f_path]).start()

            if self.OUT_AUD_IMG != None and self.IS_RECORDING != True:
                self.WIN.blit(self.OUT_AUD_IMG,self.OUT_AUD_IMG_RECT)


            if(self.AUD_FINISHED):
                self.WIN.blit(aud_finished_text,(1000,0))
           
            
            for event in pg.event.get():

                if event.type == self.AUD_FIN_EVENT:
                    self.AUD_FINISHED = True

                # check key presses
                elif event.type == pg.KEYDOWN:


                    # check if key pressed == "r", then we record
                    if event.key == pg.K_r:
                        self.REC_AUD_PRESENT = False
                        
                        
                        # reset the audio
                        self.AUD_FINISHED = False
                        self.PLAYING_AUD = True

                        # need to delete the recordings / imgs generated prior
                        self.delete_recordings(my_recording_dir)

                       
                        self.REF_AUD = self.select_reference_audio() #reference the audio file to get size of audio from api as example recording
                        aud_time_ms = int(self.AUD_MAN.get_aud_length(self.REF_AUD))
                        
                        duration = aud_time_ms / 1000
                        name = "recording-{}.wav".format(self.REF_NAME)
                        self.OUT_AUD_PATH = os.path.join(self.MY_REC_FLDER,name)

                        #
                        threading.Thread(target=self.AUD_MAN.record_mic,args=[duration,self.OUT_AUD_PATH]).start()
                        threading.Thread(target=self.PLAYING_AUD,args=[aud_time_ms]).start()
                        pg.time.set_timer(self.AUD_FIN_EVENT,aud_time_ms)

                       


                    elif event.key == pg.K_q:
                        self.delete_recordings(my_recording_dir)
                        # quit prog
                        self.RUNNING = False

                
                # if event is quit, quit
                if event.type == pg.QUIT:
                    self.RUNNING = False


            # update the surf
            pg.display.update()
            self.CLOCK.tick(self.FPS)
        
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.RUNNING = False
            
            # Handle mouse clicks
            if event.type == pg.MOUSEBUTTONDOWN:
                # Check if mic button was clicked
                if self.mic_button_rect.collidepoint(event.pos):
                    self.record_user_audio()
            
            # Handle audio finished event
            if event.type == self.AUD_FIN_EVENT:
                self.AUD_FINISHED = True
                self.PLAYING_AUD = False

    def draw(self):
        # Draw background
        self.WIN.fill(DARK_GRAY)
        
        # Draw reference audio spectrogram if available
        if self.REF_IMG:
            self.WIN.blit(self.REF_IMG, self.REF_IMG.get_rect(center=self.AUD_IMG_CENTER))
        
        # Draw user audio spectrogram if available
        if self.OUT_AUD_IMG:
            self.WIN.blit(self.OUT_AUD_IMG, self.OUT_AUD_IMG_RECT)
        
        # Draw microphone button
        mic_img = pg.image.load(os.path.join(self.WAV_IMG_REF_FLDER, "mic_record.png"))
        self.mic_button_rect = mic_img.get_rect(center=(self.WIN_X//2, self.WIN_Y - 100))
        self.WIN.blit(mic_img, self.mic_button_rect)
        
        # Draw recording indicator if recording
        if self.IS_RECORDING:
            recording_text = self.FONT.render("Recording...", True, RED)
            self.WIN.blit(recording_text, (self.WIN_X//2 - recording_text.get_width()//2, 
                                          self.WIN_Y - 150))
        
        pg.display.update()

if __name__ == "__main__":
    app = App()

    app.run()
            
        
        
        
        
        
    
        
        
        
        