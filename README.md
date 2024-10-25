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

Clone the repository and change into the directory:
```bash
git clone https://github.com/AidfulAI/aidful-whisper-typer.git
cd aidful-whisper-typer
```

**Step 3:**

Create and activate a virtual environment and install the requirements:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

Using a virtual environment keeps dependencies isolated from your system Python installation and other projects. This prevents version conflicts and makes the project more portable and reproducible.

**Step 4:**

Adapt the `settings.json` file in the project directory.

**Step 5:**

`python3 aidful-whisper-typer.py`

# Usage Instructions

1. Press Ctrl+Alt+S (default) to start recording
2. Speak clearly into your microphone
3. Press Ctrl+Alt+S again to stop recording and start transcription
4. Based on your settings.json configuration, the text will be:
   - Typed out character by character (type mode)
   - Pasted at cursor position (paste mode)
   - Copied to clipboard (clipboard mode)

# Autostart

If the script works as intended for you, you might want to add it to start at boot.

**Step 1:**

Adapt the `run-aidful-whisper-typer.sh` shell script which activates the virtual environment and runs the Python script to match your system paths.

**Step 2:**

Configure your system to run the shell script at startup.

# Features
- Configurable keyboard shortcuts for starting/stopping recording (default: Ctrl+Alt+S)
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
