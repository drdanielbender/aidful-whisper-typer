from pynput import keyboard
import codecs
import whisper
import time
import subprocess
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import pygame
from datetime import datetime

def play_sound(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

#load model
#model selection -> (tiny base small medium large)
print("loading model...")
model_name = "tiny"
model = whisper.load_model(model_name)
play_sound("model_loaded.wav")
print(f"{model_name} model loaded")

file_ready_counter=0
stop_recording=False
is_recording=False
pykeyboard= keyboard.Controller()

def transcribe_speech():
    global file_ready_counter
    i=1
    print("ready - start transcribing with F2 ...\n")
    while True:
        while file_ready_counter<i:
            time.sleep(0.01)

        result = model.transcribe("test"+str(i)+".wav")
        transcribed_text = str(result["text"]).strip()
        print(">"+transcribed_text+"<\n")
        now = str(datetime.now()).split(".")[0]
        with codecs.open('transcribe.log', 'a', encoding='utf-8') as f:
            f.write(now+" : "+transcribed_text+"\n")
        for element in transcribed_text:
            try:
                pykeyboard.type(element)
                time.sleep(0.0025)
            except:
                print("empty or unknown symbol")
        os.remove("test"+str(i)+".wav")
        i=i+1

#keyboard events
pressed = set()

COMBINATIONS = [
    {
        "keys": [
            #{keyboard.Key.ctrl ,keyboard.Key.shift, keyboard.KeyCode(char="r")},
            #{keyboard.Key.ctrl ,keyboard.Key.shift, keyboard.KeyCode(char="R")},
            {keyboard.Key.f2},
        ],
        "command": "start record",
    },
]

#------------

#record audio
def record_speech():
    global file_ready_counter
    global stop_recording
    global is_recording

    is_recording = True
    sample_format = 'int16'  # Data type
    channels = 2
    fs = 44100  # Sample rate

    frames = []  # Initialize list to store frames

    print("Start recording...\n")
    play_sound("on.wav")

    def callback(indata, frames_count, time_info, status):
        if status:
            print(status)
        frames.append(indata.copy())
        if stop_recording:
            raise sd.CallbackStop()

    with sd.InputStream(samplerate=fs, channels=channels, dtype=sample_format, callback=callback):
        while not stop_recording:
            sd.sleep(100)

    # Concatenate recorded data
    audio_data = np.concatenate(frames, axis=0)

    # Save the recorded data as a WAV file
    filename = "test" + str(file_ready_counter + 1) + ".wav"
    sf.write(filename, audio_data, fs)

    stop_recording = False
    is_recording = False
    file_ready_counter = file_ready_counter + 1
    play_sound("off.wav")
    print('Finish recording')

#------------

#transcribe speech in infinte loop
t2 = threading.Thread(target=transcribe_speech)
t2.start()

#hot key events
def on_press(key):
    pressed.add(key)

def on_release(key):
    global pressed
    global stop_recording
    global is_recording
    for c in COMBINATIONS:
        for keys in c["keys"]:
            if keys.issubset(pressed):
                if c["command"]=="start record" and stop_recording==False and is_recording==False:
                    t1 = threading.Thread(target=record_speech)
                    t1.start()
                else:
                    if c["command"]=="start record" and is_recording==True:
                        stop_recording=True
                pressed = set()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
