#!/usr/bin/env python3
"""Text-to-speech with the Google Gemini API (Gemini 3.1 Flash TTS).

Gemini TTS returns RAW PCM (24 kHz, 16-bit, mono), not a ready-to-play file.
This script wraps it into a WAV with the correct parameters, and supports both
single-speaker and multi-speaker (max 2) synthesis.

Requires: pip install google-genai   (WAV writing uses the stdlib `wave`)
Auth:     export GEMINI_API_KEY=...   (or GOOGLE_API_KEY)

Examples:
    # single speaker, default voice
    generate_speech.py "Say warmly: Welcome back!" -o welcome.wav

    # pick a voice
    generate_speech.py "Read calmly: The tide returns." -v Charon -o narr.wav

    # multi-speaker (names in the transcript must match the --speaker mappings)
    generate_speech.py "TTS this:
    Joe: How's it going?
    Jane: Pretty good!" --speaker Joe:Charon --speaker Jane:Puck -o chat.wav
"""
import argparse
import os
import sys
import wave

from google import genai
from google.genai import types

try:
    from google.genai import errors as genai_errors
except ImportError:  # pragma: no cover - very old SDKs
    genai_errors = None

# Gemini TTS output is always 24 kHz / 16-bit / mono. Do not change these:
# the bytes are headerless little-endian PCM, and wrong params play as noise.
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2  # bytes (16-bit)
CHANNELS = 1


def make_client() -> genai.Client:
    """Build a client, failing early if no key is set.

    genai.Client() reads GEMINI_API_KEY or GOOGLE_API_KEY; if both are set,
    GOOGLE_API_KEY silently wins, so we warn about it.
    """
    google_key = os.environ.get("GOOGLE_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not google_key and not gemini_key:
        sys.exit("error: no API key. Set GEMINI_API_KEY (or GOOGLE_API_KEY). "
                 "Get one at https://aistudio.google.com/apikey")
    if google_key and gemini_key:
        print("warning: both GOOGLE_API_KEY and GEMINI_API_KEY are set; "
              "GOOGLE_API_KEY takes precedence.", file=sys.stderr)
    # HttpRetryOptions was added in a newer SDK, so fall back if it's absent.
    try:
        return genai.Client(http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=5)))
    except (AttributeError, TypeError):
        return genai.Client()


def write_wav(path: str, pcm: bytes) -> None:
    with wave.open(path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)


def build_speech_config(voice: str, speakers: list[str]) -> types.SpeechConfig:
    if speakers:
        configs = []
        for mapping in speakers:
            if ":" not in mapping:
                raise ValueError(f"--speaker must be NAME:VOICE, got {mapping!r}")
            name, voice_name = mapping.split(":", 1)
            configs.append(types.SpeakerVoiceConfig(
                speaker=name.strip(),
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name.strip())
                ),
            ))
        return types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(speaker_voice_configs=configs)
        )
    return types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
        )
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Gemini text-to-speech.")
    p.add_argument("text", help="Text to speak (use 'Name:' lines for multi-speaker).")
    p.add_argument("-o", "--output", default="output.wav", help="Output WAV path.")
    p.add_argument("-m", "--model", default="gemini-3.1-flash-tts-preview", help="TTS model id.")
    p.add_argument("-v", "--voice", default="Kore", help="Prebuilt voice for single-speaker (default: Kore).")
    p.add_argument("--speaker", action="append", default=[], metavar="NAME:VOICE",
                   help="Multi-speaker mapping (repeatable, max 2). e.g. --speaker Joe:Charon")
    args = p.parse_args()

    if len(args.speaker) > 2:
        print("error: Gemini TTS supports at most 2 speakers.", file=sys.stderr)
        return 2

    client = make_client()

    try:
        speech_config = build_speech_config(args.voice, args.speaker)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=args.text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config,
            ),
        )
    except Exception as e:  # noqa: BLE001 - clean message, not a traceback
        if genai_errors and isinstance(e, genai_errors.APIError):
            print(f"error: API call failed ({getattr(e, 'code', '?')}): "
                  f"{getattr(e, 'message', e)}", file=sys.stderr)
            return 1
        raise

    parts = response.candidates[0].content.parts if response.candidates else []
    pcm = next((p.inline_data.data for p in parts if getattr(p, "inline_data", None)), None)
    if pcm is None:
        feedback = getattr(response, "prompt_feedback", None)
        detail = ""
        if feedback and getattr(feedback, "block_reason", None):
            detail = f" Prompt was blocked: {feedback.block_reason}."
        print(f"error: no audio returned (possibly blocked by safety filters).{detail}",
              file=sys.stderr)
        return 1

    write_wav(args.output, pcm)
    print(f"Saved audio to {args.output} ({SAMPLE_RATE} Hz, 16-bit, mono).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
