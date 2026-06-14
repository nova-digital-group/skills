---
name: gemini-text-to-speech
description: >-
  Convert text to natural, expressive speech with the Google Gemini API using
  Gemini 3.1 Flash TTS (gemini-3.1-flash-tts-preview). Use this whenever the
  user wants to synthesize audio, narrate text, voice a script, create a
  voiceover, generate a podcast or dialogue with multiple speakers, or do
  text-to-speech / TTS through the Gemini / Google AI API with an API key —
  including controlling tone, emotion, pace, and accent via natural-language
  direction, picking from 30 prebuilt voices, or producing multi-speaker
  conversations. Trigger on "Gemini TTS", "text to speech", "voiceover",
  "narrate", "read this aloud", or "make a podcast voice", even if the model
  id is not named.
license: MIT
---

# Gemini Text-to-Speech (Gemini 3.1 Flash TTS)

Generate speech from text with Google's Gemini TTS models. Audio comes back as
**raw 24 kHz, 16-bit, mono PCM** inside a response part — it must be wrapped in
a WAV (or other) container before it will play. The bundled script does this
for you.

## Setup

```bash
pip install google-genai      # no extra audio deps; WAV uses the stdlib `wave`
export GEMINI_API_KEY="your-key"   # or GOOGLE_API_KEY
```

## Choose the model

| Need | Model id |
|------|----------|
| Expressive, low-latency speech (**default**) | `gemini-3.1-flash-tts-preview` |
| Long-form audiobook/podcast fidelity | `gemini-2.5-pro-preview-tts` |
| Predecessor flash TTS | `gemini-2.5-flash-preview-tts` |

These are all currently **`-preview`** ids — there is no GA TTS id yet, so
expect them to rotate. If one 404s, run `client.models.list()` and check
https://ai.google.dev/gemini-api/docs/models.

## Fastest path: use the bundled script

`scripts/generate_speech.py` handles the audio config and the WAV wrapping
(channels=1, rate=24000, sample_width=2 — get any of these wrong and the file
plays as noise).

```bash
# Single speaker, default voice (Kore)
python scripts/generate_speech.py "Say warmly: Welcome back — it's great to see you." -o welcome.wav

# Pick a voice
python scripts/generate_speech.py "Read this like a calm documentary narrator: The tide returns." -v Charon -o narr.wav

# Multi-speaker (max 2): map each name in the transcript to a voice
python scripts/generate_speech.py \
  "TTS this conversation:
Joe: How's the launch going?
Jane: Honestly? A little chaotic, but good." \
  --speaker Joe:Charon --speaker Jane:Puck -o dialogue.wav
```

## Minimal code (single speaker)

```python
import wave
from google import genai
from google.genai import types

def write_wav(path, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents="Say cheerfully: Have a wonderful day!",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
            )
        ),
    ),
)
pcm = response.candidates[0].content.parts[0].inline_data.data
write_wav("out.wav", pcm)
```

## Multi-speaker (max 2 speakers)

Label each speaker by name in the transcript, then map each name to a voice:

```python
speech_config=types.SpeechConfig(
    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
        speaker_voice_configs=[
            types.SpeakerVoiceConfig(speaker="Joe",
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon"))),
            types.SpeakerVoiceConfig(speaker="Jane",
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck"))),
        ]
    )
)
```

The speaker names in the config **must match** the `Name:` labels in the prompt.

## Steering the performance (this is the point of an LLM TTS)

You direct *how* it speaks in plain language, inline with the text:

- **Style:** `"Say in a spooky whisper: ..."`, `"Read this like an excited sports announcer: ..."`
- **Accent:** describe it in the style direction — `"with a London Brixton accent"`. There is **no language/accent parameter**; accents are triggered by the prompt.
- **Per-speaker (multi):** `"Make Joe sound tired and bored, and Jane sound thrilled."`
- **Inline audio tags** steer delivery mid-sentence. 3.1 Flash TTS supports **200+** of them: emotion (`[excited]`, `[sarcastic]`, `[tired]`, `[awe]`, `[nervousness]`), sounds (`[laughs]`, `[sighs]`, `[gasp]`, `[cough]`), pacing (`[slow]`, `[fast]`), pauses (`[short pause]`, `[long pause]`), even character (`[like dracula]`). Example: `"[whispers] I have a secret... [long pause] [shouting] but I can't keep it in!"`

> **Never place two tags back-to-back** (`[slow][whispers]`) — separate them
> with text or punctuation, or the model errors. Put each tag exactly where the
> change should happen, woven into the words.

See `references/prompting.md` for the recommended 4-part structure (Audio
Profile → Scene → Director's Notes → Transcript) and the full tag list.

## Recipes by use case

| Job | Model | Approach |
|-----|-------|----------|
| Audiobook / long narration | `gemini-2.5-pro-preview-tts` | Pick a warm, even voice (Sulafat, Schedar); chunk per chapter and concatenate; minimal tags for naturalness. |
| Podcast / two-host dialogue | 3.1 Flash | Two speakers, distinct voices; per-speaker direction; conversational tags (`[laughs]`, `[short pause]`). |
| IVR / phone prompts / alerts | 3.1 Flash | A clear, firm voice (Kore, Charon); plain, unhurried delivery; short scripts. |
| E-learning / explainer VO | 3.1 Flash | A knowledgeable, friendly voice (Sadaltager, Achird); steady pace; `[short pause]` between points. |
| Game / character lines | 3.1 Flash | Character tags + persona in the Director's Notes; expressive voices (Fenrir, Puck). |
| Accessibility / audio descriptions | 3.1 Flash | Neutral, even delivery; avoid heavy emotion; keep pace measured. |
| Multilingual content | 3.1 Flash | Write the body in the target language; keep audio tags in **English**; language is auto-detected. |

## Things to know

- **Output is raw PCM**, not a WAV/MP3 file. Always wrap with `channels=1, rate=24000, sample_width=2`.
- **30 prebuilt voices**, each with a character (e.g. Kore=firm, Puck=upbeat, Charon=informative, Achird=friendly, Sulafat=warm). Full list in `references/voices-and-languages.md`.
- **70+ languages**, auto-detected from the input text — no language parameter. For non-English text, keep audio tags in English for best results.
- **Length:** ~8,192 input tokens / ~16,384 output audio tokens (≈ a few minutes). Quality drifts on very long outputs — split long scripts into chunks and concatenate.
- **SynthID watermark** is embedded in all output.
- Don't over-constrain: too many rigid rules hurt naturalness — leave the model room to perform.

## More detail

- `references/voices-and-languages.md` — all 30 voices with their characteristics, the language list, token limits, pricing.
- `references/prompting.md` — the 4-part directing structure, audio tags, worked examples, pitfalls.
