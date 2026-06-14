# Gemini TTS — Voices, Languages, Limits & Pricing

> Researched 2026-06-14 from https://ai.google.dev/gemini-api/docs/speech-generation
> and the models/pricing pages. Verify before relying on exact values.

## Models

| Marketing name | Model id | Best for |
|----------------|----------|----------|
| **Gemini 3.1 Flash TTS** | `gemini-3.1-flash-tts-preview` | Expressive, low-latency speech. **Default.** |
| Gemini 2.5 Pro TTS | `gemini-2.5-pro-preview-tts` | High-fidelity long-form (audiobooks, podcasts). |
| Gemini 2.5 Flash TTS | `gemini-2.5-flash-preview-tts` | Predecessor flash model. |

All are `-preview` (no GA TTS id yet). Token limits for 3.1 Flash TTS:
**8,192 input** / **16,384 output** tokens. Audio output tokenizes at **~32
tokens/second**, so 16,384 output tokens ≈ ~8.5 minutes — but quality and
consistency drift past a few minutes, so chunk long scripts. (The guide also
mentions a separate ~32k-token *session* context window — a different figure.)

For real-time / interactive voice (audio-in → audio-out), these one-shot TTS
models are the wrong tool — use the **Live API** models instead, e.g.
`gemini-3.1-flash-live-preview` or `gemini-2.5-flash-native-audio-preview-12-2025`.
Those stream and converse; the TTS models only do text-in → audio-out.

## Audio output format (critical)

The bytes at `response.candidates[0].content.parts[0].inline_data.data` are
**raw little-endian signed PCM**:

- **Sample rate:** 24000 Hz
- **Bit depth:** 16-bit → `sample_width=2`
- **Channels:** 1 (mono)

To get a playable file, wrap in WAV with exactly those parameters. Wrong
parameters → the audio plays as static/garbage.

## The 30 prebuilt voices

| Voice | Character | Voice | Character |
|-------|-----------|-------|-----------|
| Zephyr | Bright | Algenib | Gravelly |
| Puck | Upbeat | Rasalgethi | Informative |
| Charon | Informative | Laomedeia | Upbeat |
| Kore | Firm | Achernar | Soft |
| Fenrir | Excitable | Alnilam | Firm |
| Leda | Youthful | Schedar | Even |
| Orus | Firm | Gacrux | Mature |
| Aoede | Breezy | Pulcherrima | Forward |
| Callirrhoe | Easy-going | Achird | Friendly |
| Autonoe | Bright | Zubenelgenubi | Casual |
| Enceladus | Breathy | Vindemiatrix | Gentle |
| Iapetus | Clear | Sadachbia | Lively |
| Umbriel | Easy-going | Sadaltager | Knowledgeable |
| Algieba | Smooth | Sulafat | Warm |
| Despina | Smooth | Erinome | Clear |

Select a voice with `PrebuiltVoiceConfig(voice_name="Charon")`. Audition voices
in the AI Studio Voice Library before committing to one for a project.

## Languages

70+ languages, **auto-detected** from the input text (no language parameter).
Documented codes include: Arabic (ar), Bangla (bn), Dutch (nl), English (en),
French (fr), German (de), Hindi (hi), Indonesian (id), Italian (it), Japanese
(ja), Korean (ko), Marathi (mr), Polish (pl), Portuguese (pt), Romanian (ro),
Russian (ru), Spanish (es), Tamil (ta), Telugu (te), Thai (th), Turkish (tr),
Ukrainian (uk), Vietnamese (vi), Chinese Mandarin (cmn), plus many more
(Afrikaans, Albanian, Amharic, Armenian, Azerbaijani, Basque, Belarusian,
Bulgarian, Burmese, Catalan, Cebuano, Croatian, Czech, Danish, Estonian,
Filipino, Finnish, Galician, Georgian, Greek, Gujarati, Haitian Creole, Hebrew,
Hungarian, Icelandic, Javanese, Kannada, Konkani, Lao, Latin, Latvian,
Lithuanian, Luxembourgish, Macedonian, Maithili, Malagasy, Malay, Mongolian,
Nepali, Norwegian Bokmål/Nynorsk, Odia, Pashto, Persian, Punjabi, Serbian,
Sindhi, Sinhala, Slovak, Slovenian, Swahili, Swedish, Urdu, ...).

For multilingual or non-English transcripts, keep the inline audio tags
(`[laughs]`, etc.) in **English** for the most reliable results.

## Capabilities & limits

- **Single-speaker and multi-speaker** (max **2 speakers**). Speaker names in the config must match the `Name:` labels in the transcript.
- **Natural-language control** of style, tone, accent, pace, emotion — inline in the prompt.
- **200+ inline audio tags** for fine delivery control (see `prompting.md`).
- **No streaming** on the TTS models (explicitly documented). Function calling and thinking are not documented for them either — treat them as text-in, audio-out only. For real-time conversational audio, use the separate **Live API** models (see above).
- **SynthID watermark** embedded in all output.

## Pricing (per 1M tokens; input = text, output = audio)

| Model | Input | Output (audio) | Batch in | Batch out |
|-------|-------|----------------|----------|-----------|
| `gemini-3.1-flash-tts-preview` | $1.00 | $20.00 | $0.50 | $10.00 |
| `gemini-2.5-flash-preview-tts` | $0.50 | $10.00 | $0.25 | $5.00 |
| `gemini-2.5-pro-preview-tts` | $1.00 | $20.00 | $0.50 | $10.00 |

Audio ≈ 32 output tokens/second, so a 60-second clip on 3.1 Flash TTS
≈ 1,920 tokens ≈ $0.038. A free tier is available in AI Studio (2.5 Pro TTS is
paid-tier only). The 50% Batch discount makes high-volume narration much cheaper.
