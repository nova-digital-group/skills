# Gemini Media Skills

[Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) for generating **images, speech, and video** with the [Google Gemini API](https://ai.google.dev/gemini-api/docs) (the API-key developer API on `generativelanguage.googleapis.com` — *not* Vertex AI).

Each skill teaches an AI agent (Claude Code, the Claude Agent SDK, or any skill-aware tool) how to call a specific Gemini generative model correctly: the right model id, the exact request shape, how to extract the binary result, and how to write a prompt that actually works for that modality.

> **Unofficial.** This project is not affiliated with or endorsed by Google. "Gemini", "Veo", "Imagen", and "Nano Banana" are trademarks of Google LLC. Always confirm model ids, parameters, and pricing against the [official docs](https://ai.google.dev/gemini-api/docs) — they change often.

## Skills in this repository

| Skill | Modality | Default model | What it covers |
|-------|----------|---------------|----------------|
| [`gemini-image-generation`](skills/gemini-image-generation/) | Text → image, image editing | `gemini-3.1-flash-image` (**Nano Banana 2**) | Generation, editing, multi-image composition, character consistency, text-in-image, infographics |
| [`gemini-text-to-speech`](skills/gemini-text-to-speech/) | Text → speech | `gemini-3.1-flash-tts-preview` (**Gemini 3.1 Flash TTS**) | Single- & multi-speaker audio, 30 voices, 70+ languages, style/emotion control via natural language |
| [`gemini-video-generation`](skills/gemini-video-generation/) | Text/image → video | `veo-3.1-generate-preview` (**Veo 3.1**) | Async video generation with native audio, image-to-video, first/last-frame, Veo 3.1 Lite for low cost |

## Quick start

### 1. Get an API key

Create a key at [Google AI Studio → API keys](https://aistudio.google.com/apikey) and export it. The SDKs read `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) automatically:

```bash
export GEMINI_API_KEY="your-key-here"
```

> Never commit keys to source control or ship them in client-side apps. For production, use a secret store and call the API from a backend.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs the official [`google-genai`](https://pypi.org/project/google-genai/) SDK (the older `google-generativeai` package is deprecated) plus `pillow` for image handling.

### 3. Install the skills

These are standard Agent Skills — a folder with a `SKILL.md` plus bundled references and scripts. Use whichever fits your setup:

- **Claude Code (personal):** copy a skill folder into `~/.claude/skills/`
  ```bash
  cp -r skills/gemini-image-generation ~/.claude/skills/
  ```
- **Claude Code (per project):** copy it into `<your-project>/.claude/skills/`
- **Claude Agent SDK / API:** point your skills source at the `skills/` directory, or upload individual skill folders.

Each skill is **self-contained** — it embeds its own setup notes, so you can install just the one you need.

### 4. Use it

Once installed, just ask in natural language. The skill descriptions are tuned to trigger on phrasings like:

- *"Generate a product photo of a matte-black water bottle on a marble counter with Nano Banana."*
- *"Turn this script into a two-host podcast intro using Gemini TTS, one voice upbeat and one calm."*
- *"Make an 8-second cinematic drone shot of a coastal road at sunset with Veo 3.1."*

You can also run the bundled scripts directly:

```bash
python skills/gemini-image-generation/scripts/generate_image.py "a watercolor fox in a snowy forest" -o fox.png
python skills/gemini-text-to-speech/scripts/generate_speech.py "Say warmly: Welcome back!" -v Achird -o hello.wav
python skills/gemini-video-generation/scripts/generate_video.py "a paper boat sailing down a rain gutter, cinematic" -o boat.mp4
```

## Choosing a model (quick guidance)

- **Images:** `gemini-3.1-flash-image` (Nano Banana 2) for fast, high-volume work; `gemini-3-pro-image` (Nano Banana Pro) when you need 4K, dense text, or complex layouts.
- **Speech:** `gemini-3.1-flash-tts-preview` for low-latency, expressive speech; `gemini-2.5-pro-preview-tts` for long-form audiobook/podcast fidelity.
- **Video:** `veo-3.1-generate-preview` for top quality; `veo-3.1-fast-generate-preview` to cut cost; `veo-3.1-lite-generate-preview` for the cheapest option (no 4K, no extension).

Pricing and rate limits live with each skill's reference docs and on the [official pricing page](https://ai.google.dev/gemini-api/docs/pricing). All generated media carries a [SynthID](https://deepmind.google/technologies/synthid/) watermark.

## Requirements

- Python 3.9+
- A Gemini API key with billing enabled for the preview/paid models (image, TTS, and video models are generally paid)

## License

[MIT](LICENSE) © 2026 Nova Digital Solutions GmbH. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome — especially updates when Google rotates model ids or graduates preview models to GA.
