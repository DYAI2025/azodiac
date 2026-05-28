#!/usr/bin/env python3
"""
Whisper STT for Claude Code
Records audio and transcribes using Whisper
Usage: listen.py [--duration 5] [--language de]
"""

import sys
import os
import tempfile
import argparse
import subprocess

def record_audio(duration: int = 5, output_path: str = None) -> str:
    """Record audio from microphone using sox"""
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.wav')

    print(f"🎤 Recording for {duration} seconds... (speak now)")

    # Use sox for recording (brew install sox)
    try:
        subprocess.run([
            'rec', '-q', '-r', '16000', '-c', '1', '-b', '16',
            output_path, 'trim', '0', str(duration)
        ], check=True, capture_output=True)
    except FileNotFoundError:
        print("Error: 'sox' not installed. Install with: brew install sox")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Recording error: {e}")
        sys.exit(1)

    print("✓ Recording complete")
    return output_path

def transcribe(audio_path: str, language: str = "de") -> str:
    """Transcribe audio using Whisper"""
    try:
        import whisper
    except ImportError:
        print("Error: whisper not installed. Install with: pip install openai-whisper")
        sys.exit(1)

    print("🔄 Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    return result["text"].strip()

def main():
    parser = argparse.ArgumentParser(description="Whisper STT for Claude Code")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Recording duration in seconds")
    parser.add_argument("--language", "-l", default="de", help="Language code (de, en, etc.)")
    parser.add_argument("--no-copy", action="store_true", help="Don't copy to clipboard")
    args = parser.parse_args()

    # Record
    audio_path = record_audio(args.duration)

    try:
        # Transcribe
        text = transcribe(audio_path, args.language)

        print(f"\n📝 Transcription:\n{text}\n")

        # Copy to clipboard (macOS)
        if not args.no_copy:
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
            print("✓ Copied to clipboard (Cmd+V to paste)")

        # Also print to stdout for piping
        return text

    finally:
        # Cleanup
        if os.path.exists(audio_path):
            os.unlink(audio_path)

if __name__ == "__main__":
    result = main()
    if result:
        print(result)
