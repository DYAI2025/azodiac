#!/usr/bin/env python3
"""
Push-to-Talk für Claude Code
Wird von Hammerspoon gesteuert (Option+Space halten)
"""

import sys
import os
import signal
import tempfile
import subprocess
import threading

# Globals
recording_process = None
temp_audio_file = None
is_recording = False

def start_recording():
    """Start audio recording"""
    global recording_process, temp_audio_file, is_recording

    if is_recording:
        return

    temp_audio_file = tempfile.mktemp(suffix='.wav')

    # Start sox recording (no time limit)
    recording_process = subprocess.Popen([
        'rec', '-q', '-r', '16000', '-c', '1', '-b', '16',
        temp_audio_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    is_recording = True
    print("🎤 Recording... (release keys to stop)", flush=True)

def stop_recording():
    """Stop recording and transcribe"""
    global recording_process, temp_audio_file, is_recording

    if not is_recording or recording_process is None:
        return

    # Stop recording
    recording_process.terminate()
    recording_process.wait()
    is_recording = False

    print("✓ Recording stopped", flush=True)

    if not os.path.exists(temp_audio_file) or os.path.getsize(temp_audio_file) < 1000:
        print("⚠ Recording too short", flush=True)
        return

    # Transcribe
    print("🔄 Transcribing...", flush=True)
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_file, language="de")
        text = result["text"].strip()

        if text:
            print(f"\n📝 {text}\n", flush=True)
            # Copy to clipboard
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
            print("✓ Copied to clipboard", flush=True)

            # Also speak confirmation
            subprocess.Popen([
                'python3', os.path.expanduser('~/.claude/scripts/speak.py'),
                f"Ich habe verstanden: {text[:100]}"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("⚠ No speech detected", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        # Cleanup
        if temp_audio_file and os.path.exists(temp_audio_file):
            os.unlink(temp_audio_file)

def signal_handler(signum, frame):
    """Handle signals from Hammerspoon"""
    if signum == signal.SIGUSR1:
        start_recording()
    elif signum == signal.SIGUSR2:
        stop_recording()

def main():
    # Register signal handlers
    signal.signal(signal.SIGUSR1, signal_handler)  # Start recording
    signal.signal(signal.SIGUSR2, signal_handler)  # Stop recording

    # Write PID file for Hammerspoon
    pid_file = os.path.expanduser('~/.claude/scripts/ptt.pid')
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    print("🎙️ Push-to-Talk ready (Option+Space)", flush=True)
    print(f"   PID: {os.getpid()}", flush=True)

    # Keep running
    try:
        while True:
            signal.pause()
    except KeyboardInterrupt:
        print("\n👋 Push-to-Talk stopped", flush=True)
        if os.path.exists(pid_file):
            os.unlink(pid_file)

if __name__ == "__main__":
    main()
