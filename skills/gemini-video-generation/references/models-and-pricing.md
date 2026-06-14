# Veo Video Models — Catalog, Pricing & Limits

> Researched 2026-06-14 from https://ai.google.dev/gemini-api/docs/video and the
> models/pricing pages. Verify before relying on exact values — these are
> preview models and change frequently.

## Model ids

| Marketing name | Model id | Audio | Resolutions | Duration | Extension |
|----------------|----------|:----:|-------------|----------|:---------:|
| **Veo 3.1** | `veo-3.1-generate-preview` | ✅ | 720p, 1080p, 4k | 4 / 6 / 8 s | ✅ |
| **Veo 3.1 Fast** | `veo-3.1-fast-generate-preview` | ✅ | 720p, 1080p, 4k | 4 / 6 / 8 s | ✅ |
| **Veo 3.1 Lite** | `veo-3.1-lite-generate-preview` | ✅ | 720p, 1080p | 4 / 6 / 8 s | ❌ |
| Veo 3 | `veo-3.0-generate-001` | ✅ | 720p, 1080p | 8 s | — |
| Veo 3 Fast | `veo-3.0-fast-generate-001` | ✅ | 720p, 1080p | 8 s | — |
| Veo 2 | `veo-2.0-generate-001` | ❌ silent | 720p | 5–8 s | — |

All Veo output is **24fps**. Veo 3.1 Lite is text+image only (no extension, no
4K) and limits prompt text to ~1,024 tokens; at 720p it's **≈ half** the cost of
Veo 3.1 Fast ($0.05 vs $0.10/s).

## The async lifecycle (always)

```python
operation = client.models.generate_videos(model=..., prompt=..., config=...)
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("output.mp4")
```

REST equivalent: POST to `:predictLongRunning`, then poll
`GET {operation_name}` until `.done`, then download from
`.response.generateVideoResponse.generatedSamples[0].video.uri` (the download
URL also needs the `x-goog-api-key` header).

- **Latency:** ~11 seconds to ~6 minutes.
- **Storage:** videos are kept on the server for **2 days**, then deleted. Download promptly.

## Parameters (`types.GenerateVideosConfig`)

| Param | Values / type | Notes |
|-------|---------------|-------|
| `aspect_ratio` | `"16:9"` (default), `"9:16"` | |
| `resolution` | `"720p"` (default), `"1080p"`, `"4k"` | 1080p/4k require 8s duration; Lite has no 4k; extension is 720p only |
| `duration_seconds` | `"4"`, `"6"`, `"8"` | docs show **strings**; some SDK builds also accept ints — pass strings to be safe, or check your installed `google-genai` |
| `number_of_videos` | int (1; Veo 2 allows 1–2) | |
| `negative_prompt` | string (comma-separated nouns) | exclude objects/characteristics; never use "no"/"don't" |
| `last_frame` | `types.Image` | use with top-level `image=` for first/last-frame interpolation |
| `reference_images` | up to 3 `VideoGenerationReferenceImage(image=..., reference_type="asset")` | guide character/object/scene appearance |
| `person_generation` | `"allow_all"` / `"allow_adult"` | documented but not shown in sample code — verify; EU/UK/CH/MENA forced to `"allow_adult"` |
| `seed` | int | documented but not shown in sample code — verify |

Top-level args to `generate_videos` (not in the config object):
- `image=types.Image(...)` — starting frame for image-to-video.
- `video=...` — a prior generated video, for **extension** (Veo 3.1 / Fast only).

## Capabilities & limits

- **Native audio** for all Veo 3.x (always on, no toggle); dialogue + SFX + ambience are driven by the prompt.
- **Image-to-video:** provide a starting frame via `image=`.
- **First/last-frame interpolation:** `image=` + `last_frame=`.
- **Reference images:** up to 3, `reference_type="asset"`, for subject/scene consistency.
- **Extension:** Veo 3.1 / Fast can extend a Veo-generated clip; output can reach ~148s (720p, 16:9 or 9:16). Extended videos reset the 2-day clock. **Not on Lite.**
- **Safety:** prompts/outputs pass safety filters; blocked generations are **not billed**.
- **SynthID watermark** embedded in all output.

## Pricing (per second of video, audio included)

| Model | 720p | 1080p | 4K |
|-------|------|-------|----|
| Veo 3.1 (`veo-3.1-generate-preview`) | $0.40 | $0.40 | $0.60 |
| Veo 3.1 Fast (`veo-3.1-fast-generate-preview`) | $0.10 | $0.12 | $0.30 |
| **Veo 3.1 Lite (`veo-3.1-lite-generate-preview`)** | **$0.05** | **$0.08** | n/a |
| Veo 3 (`veo-3.0-generate-001`) | $0.40 | $0.40 | — |
| Veo 2 (`veo-2.0-generate-001`) | $0.35 (silent) | — | — |

So an 8-second 1080p clip costs ≈ $3.20 on Veo 3.1, ≈ $0.96 on Veo 3.1 Fast,
and ≈ $0.64 on Veo 3.1 Lite. Pricing includes audio for all **Veo 3.x** models;
**Veo 2 is silent**, so its $0.35/s buys video only.

## Rate limits

Per-model RPM/concurrent-job limits aren't published in the docs; check Google
AI Studio (https://aistudio.google.com/rate-limit). Video generation is heavily
rate-limited relative to text — design for queuing and retries.
