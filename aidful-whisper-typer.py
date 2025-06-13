#!/usr/bin/env python3
from pynput import keyboard
import codecs
import time
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import pygame
import signal
import sys
from datetime import datetime
import json
import pyperclip
import subprocess
import re

file_ready_counter=0
stop_recording=False
is_recording=False
shutdown_event = threading.Event()
pykeyboard= keyboard.Controller()

def cleanup():
    """Perform cleanup operations before shutdown"""
    global stop_recording, is_recording
    shutdown_event.set()

    if is_recording:
        stop_recording = True
        time.sleep(1)

    pygame.mixer.quit()
    print("\nCleanup complete")

def signal_handler(sig, frame):
    print('\nInitiating shutdown...')
    cleanup()
    sys.exit(0)

def play_sound(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            return validate_settings(settings)
    except FileNotFoundError:
        print("The setting.json file was not found. Initiating shutdown.")
        cleanup()
        sys.exit(0)

def validate_settings(settings):
    valid_output_modes = settings["output"]["options"]

    if settings["output"]["mode"] not in valid_output_modes:
        print(f"Invalid output mode. Using default 'type'")
        settings["output"]["mode"] = "paste"

    if "shortcut" not in settings or "keys" not in settings["shortcut"]:
        print("Invalid shortcut configuration. Using default CTRL+SHIFT+S")
        settings["shortcut"] = {"keys": ["ctrl", "alt", "s"]}

    if "logging" not in settings:
        settings["logging"] = {"enabled": False}

    if "delete_wav" not in settings:
        settings["delete_wav"] = {"enabled": False}

    # Whisper.cpp settings
    if "whisper_cpp" not in settings:
        settings["whisper_cpp"] = {
            "executable_path": "whisper-cli", # Default, assumes it's in PATH
            "model_path": "ggml-base.en.bin" # Default, user needs to ensure this exists
        }
    else:
        if "executable_path" not in settings["whisper_cpp"]:
            settings["whisper_cpp"]["executable_path"] = "whisper-cli"
        if "model_path" not in settings["whisper_cpp"]:
            settings["whisper_cpp"]["model_path"] = "ggml-base.en.bin"

    return settings

settings = load_settings()

print("Using whisper.cpp for transcription.")
# Check if whisper.cpp essentials are likely to work
if not os.path.exists(settings["whisper_cpp"]["executable_path"]):
    # A more robust check would be to try `subprocess.run([settings["whisper_cpp"]["executable_path"], "--version"], ...)`
    # but for simplicity, we just check path existence.
    print(f"Warning: whisper.cpp executable not found at '{settings['whisper_cpp']['executable_path']}'. Transcriptions will fail.")
if not os.path.exists(settings["whisper_cpp"]["model_path"]):
    print(f"Warning: whisper.cpp model not found at '{settings['whisper_cpp']['model_path']}'. Transcriptions will fail.")
play_sound("model_loaded.wav")

def get_key_combination(key_names):
    key_set = set()
    for key_name in key_names:
        if key_name == "ctrl":
            key_set.add(keyboard.Key.ctrl)
        elif key_name == "shift":
            key_set.add(keyboard.Key.shift)
        elif key_name == "alt":
            key_set.add(keyboard.Key.alt)
        elif key_name.startswith('f') and key_name[1:].isdigit():
            key_set.add(keyboard.Key.f1 if key_name == 'f1' else
                       keyboard.Key.f2 if key_name == 'f2' else
                       keyboard.Key.f3 if key_name == 'f3' else
                       keyboard.Key.f4 if key_name == 'f4' else
                       keyboard.Key.f5 if key_name == 'f5' else
                       keyboard.Key.f6 if key_name == 'f6' else
                       keyboard.Key.f7 if key_name == 'f7' else
                       keyboard.Key.f8 if key_name == 'f8' else
                       keyboard.Key.f9 if key_name == 'f9' else
                       keyboard.Key.f10 if key_name == 'f10' else
                       keyboard.Key.f11 if key_name == 'f11' else
                       keyboard.Key.f12)
        else:
            key_set.add(keyboard.KeyCode(char=key_name))
    return key_set

def handle_transcribed_text(transcribed_text):
    output_mode = settings["output"]["mode"]

    pyperclip.copy(transcribed_text)

    if output_mode == "type":
        for element in transcribed_text:
            if shutdown_event.is_set():
                break
            try:
                pykeyboard.type(element)
                time.sleep(settings["type"]["delay"])
            except:
                print("empty or unknown symbol")

    elif output_mode == "paste":
        try:
            with pykeyboard.pressed(keyboard.Key.ctrl):
                pykeyboard.tap('v')
        except Exception as e:
            print(f"Error pasting text: {e}")

    elif output_mode == "clipboard":
        print("Text copied to clipboard")

    else:
        print(f"Unknown output mode: {output_mode}")

def transcribe_speech():
    global file_ready_counter
    i=1
    print("ready - start transcribing with keyboard shortcut...\n")
    while not shutdown_event.is_set():
        while file_ready_counter<i and not shutdown_event.is_set():
            time.sleep(0.01)

        if shutdown_event.is_set():
            break

        current_audio_file = "test"+str(i)+".wav"
        transcribed_text = ""

        try:
            print(f"Transcribing {current_audio_file} using whisper.cpp...")
            wcpp_config = settings["whisper_cpp"]
            command = [
                wcpp_config["executable_path"],
                "--model", wcpp_config["model_path"],
                "-l", "auto", # without this options, German voice was translated to English
                current_audio_file
            ]
            
            # Remove whisper.cpp's output timestamp. Doing this manually as the "-nt" parameter leads to a degraded result. See GitHub issue: https://github.com/ggml-org/whisper.cpp/issues/2312
            try:
                process = subprocess.run(command, capture_output=True, text=True, check=True, timeout=300)
                timestamped_output = process.stdout.strip()
                
                plain_text_segments = []
                # Regex from test-whispercpp.py
                timestamp_pattern = re.compile(r"^\[\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\]\s*(.*)$")

                for line in timestamped_output.splitlines():
                    line = line.strip()
                    if line:
                        match = timestamp_pattern.match(line)
                        if match:
                            text_segment = match.group(1)
                            plain_text_segments.append(text_segment)
                
                transcribed_text = " ".join(plain_text_segments).strip()

                if process.stderr:
                    print(f"whisper.cpp stderr: {process.stderr.strip()}")

            except FileNotFoundError:
                print(f"Error: whisper.cpp executable not found at '{wcpp_config['executable_path']}'. Check settings.json.")
                transcribed_text = "" # Ensure it's empty on error
            except subprocess.CalledProcessError as e:
                print(f"Error during whisper.cpp transcription (exit code {e.returncode}): {e}")
                print(f"Command: {' '.join(e.cmd)}")
                print(f"Stdout: {e.stdout}")
                print(f"Stderr: {e.stderr}")
                transcribed_text = ""
            except subprocess.TimeoutExpired:
                print(f"Error: whisper.cpp process timed out.")
                transcribed_text = ""
            except Exception as e:
                print(f"An unexpected error occurred with whisper.cpp: {e}")
                transcribed_text = ""

            print(">"+transcribed_text+"<\n")
            if settings["logging"]["enabled"] and transcribed_text:
                now = str(datetime.now()).split(".")[0]
                with codecs.open('transcribe.log', 'a', encoding='utf-8') as f:
                    f.write(now+" : "+transcribed_text+"\n")
            
            if transcribed_text: # Only handle if text was actually transcribed
                handle_transcribed_text(transcribed_text)
            
            if settings["delete_wav"]["enabled"] and os.path.exists(current_audio_file):
                os.remove(current_audio_file)
            i=i+1
        except Exception as e:
            # This outer try-except should catch errors not specific to transcription process itself
            print(f"Error in transcription processing loop: {e}")

#keyboard events
pressed = set()

shortcut_keys = settings["shortcut"]["keys"]
COMBINATIONS = [ # list not needed in current version, but allows to register multiple shortcuts later
    {
        "keys": get_key_combination(shortcut_keys),
    },
]

#------------

#record audio
def record_speech():
    global file_ready_counter
    global stop_recording
    global is_recording

    is_recording = True
    sample_format = settings["audio"]["sample_format"]
    channels = settings["audio"]["channels"]
    fs = settings["audio"]["sample_rate"]

    frames = []  # Initialize list to store frames

    print("Start recording...\n")
    play_sound("on.wav")

    def callback(indata, frames_count, time_info, status):
        if status:
            print(status)
        frames.append(indata.copy())
        if stop_recording or shutdown_event.is_set():
            raise sd.CallbackStop()

    try:
        with sd.InputStream(samplerate=fs, channels=channels, dtype=sample_format, callback=callback):
            while not stop_recording and not shutdown_event.is_set():
                sd.sleep(100)

        if not shutdown_event.is_set():
            audio_data = np.concatenate(frames, axis=0)
            filename = "test" + str(file_ready_counter + 1) + ".wav"
            sf.write(filename, audio_data, fs)
            file_ready_counter = file_ready_counter + 1
            play_sound("off.wav")
            print('Finish recording')
    except Exception as e:
        print(f"Error during recording: {e}")
    finally:
        stop_recording = False
        is_recording = False

#------------

#transcribe speech in infinite loop
t2 = threading.Thread(target=transcribe_speech, daemon=True)
t2.start()

#hot key events
def on_press(key):
    global pressed
    pressed.add(key)

def on_release(key):
    global pressed
    global stop_recording
    global is_recording
    for c in COMBINATIONS:
        if c["keys"] == pressed:
            if stop_recording==False and is_recording==False:
                t1 = threading.Thread(target=record_speech)
                t1.start()
            else:
                stop_recording=True
    pressed = set()

signal.signal(signal.SIGINT, signal_handler)

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\nReceived keyboard interrupt")
except Exception as e:
    print(f"\nError occurred: {e}")
finally:
    cleanup()
    sys.exit(0)
