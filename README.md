# aidful-whisper-typer
This is a Python script using [openai/whisper](https://github.com/openai/whisper) to transcribe speech to text. After starting the script, use the configured keyboard shortcut to start/stop recording. The transcribed text will be handled according to your settings (typing, pasting, or copying to clipboard).

**Note:** This tool has been primarily tested on Linux systems using PulseAudio. While it should theoretically work on other operating systems due to the cross-platform nature of the used libraries, your experience may vary. The `sounddevice` library which is used to record the audio supports multiple backends:
- PortAudio
- ALSA (on Linux)
- PulseAudio (on Linux)
- Core Audio (on macOS)
- WASAPI/DirectSound (on Windows)

# Setup Instructions
**Step 1:**
Download and install ffmpeg and python3.11 (might work with other versions, but this is not tested)

**Step 2:**
`pip install -r requirements.txt`

**Step 3:**
Adapt the `settings.json` file in the same directory

**Step 4:**
`python3 aidful-whisper-typer.py`

# Features
- Configurable keyboard shortcuts for starting/stopping recording
- Multiple output modes:
  - `type`: Types out the text character by character
  - `paste`: Pastes the text at once using Ctrl+V
  - `clipboard`: Only copies the text to clipboard
- Different Whisper model options (tiny, base, small, medium, large, turbo). Best based on available VRAM of GPU:
  - `turbo`: ~6GB of VRAM and ~8x relative speed at highest quality
  - `small`: ~2GB of VRAM and ~4x relative speed at good quality
  - `base`: ~1GB of VRAM and ~7x relative speed at ok quality
- Audio transcription logging (can be turned off)
- Sound notifications for recording start/stop
