#!/usr/bin/env python3
"""
Piper TTS for Claude Code
Usage: speak.py "Text to speak" [--voice de_DE-thorsten-high]
"""

import sys
import os
import wave
import io
import tempfile
import argparse

# Add agent-zero path for Piper models
MODELS_DIR = os.path.expanduser("~/agent-zero-data/models/piper")
DEFAULT_VOICE = "de_DE-thorsten-high"

def speak(text: str, voice: str = DEFAULT_VOICE):
    """Synthesize and play text using Piper TTS"""
    from piper import PiperVoice

    model_path = os.path.join(MODELS_DIR, f"{voice}.onnx")
    config_path = os.path.join(MODELS_DIR, f"{voice}.onnx.json")

    if not os.path.exists(model_path):
        print(f"Error: Voice model not found: {model_path}")
        print(f"Available voices in {MODELS_DIR}:")
        for f in os.listdir(MODELS_DIR):
            if f.endswith('.onnx'):
                print(f"  - {f.replace('.onnx', '')}")
        sys.exit(1)

    # Load voice
    voice_model = PiperVoice.load(model_path, config_path=config_path)

    # Synthesize to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name
        with wave.open(tmp, 'wb') as wav:
            voice_model.synthesize_wav(text, wav)

    # Play audio (macOS)
    os.system(f"afplay {tmp_path}")

    # Cleanup
    os.unlink(tmp_path)

def main():
    parser = argparse.ArgumentParser(description="Piper TTS for Claude Code")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE, help="Voice model name")
    parser.add_argument("--list", "-l", action="store_true", help="List available voices")
    args = parser.parse_args()

    if args.list:
        print("Available voices:")
        if os.path.exists(MODELS_DIR):
            for f in sorted(os.listdir(MODELS_DIR)):
                if f.endswith('.onnx'):
                    print(f"  {f.replace('.onnx', '')}")
        else:
            print(f"  (No models found in {MODELS_DIR})")
        return

    # Read from stdin if no text argument
    if args.text:
        text = args.text
    else:
        text = sys.stdin.read().strip()

    if not text:
        print("Usage: speak.py 'Text to speak'")
        print("       echo 'Text' | speak.py")
        sys.exit(1)

    speak(text, args.voice)

if __name__ == "__main__":
    main()
