---
name: gemini-video-generation
description: >-
  Generate video (with native synchronized audio) from text or an image using
  the Google Gemini API and Veo — Veo 3.1 (veo-3.1-generate-preview),
  Veo 3.1 Fast (veo-3.1-fast-generate-preview), or Veo 3.1 Lite
  (veo-3.1-lite-generate-preview). Use this whenever the user wants to create,
  generate, or animate a video clip through the Gemini / Google AI API with an
  API key — including text-to-video, image-to-video, cinematic shots, animated
  scenes, first/last-frame interpolation, extending a clip, or adding dialogue
  and sound effects. Trigger on "Veo", "generate a video", "make a video clip",
  "animate this image", or "text to video", even if the model id is not named.
  Note: video generation is an async long-running operation — submit, poll,
  then download.
license: MIT
---

# Gemini Video Generation (Veo 3.1)

Generate short videos with synchronized audio from a text prompt or a starting
image. Veo is **asynchronous**: you submit a job, poll the operation until it's
done (≈ 11 seconds to 6 minutes), then download the MP4. Generated videos are
**deleted from the server after 2 days** — download promptly.

## Setup

```bash
pip install google-genai
export GEMINI_API_KEY="your-key"   # or GOOGLE_API_KEY
```

## Choose the model

| Need | Model id | Audio | 4K | Extend |
|------|----------|:----:|:--:|:------:|
| Best quality (**default**) | `veo-3.1-generate-preview` | ✅ | ✅ | ✅ |
| Cheaper, same features | `veo-3.1-fast-generate-preview` | ✅ | ✅ | ✅ |
| Cheapest (text/image only) | `veo-3.1-lite-generate-preview` | ✅ | ❌ | ❌ |

All Veo 3.1 ids are `-preview`; expect rotation. **Lite cannot do 4K or video
extension** — guard against those configs. All output is 24fps with native
audio (Veo 2 was silent).

## Fastest path: use the bundled script

`scripts/generate_video.py` handles the whole async lifecycle — submit, poll,
and download — plus optional image-to-video and config.

```bash
# text to video
python scripts/generate_video.py "a paper boat sailing down a rain gutter, cinematic, shallow focus" -o boat.mp4

# portrait, 8 seconds, 1080p
python scripts/generate_video.py "neon-lit alley, rain, a cat darts past" --aspect-ratio 9:16 --duration 8 --resolution 1080p -o alley.mp4

# image to video (animate a starting frame)
python scripts/generate_video.py "the lantern flickers and the camera slowly pushes in" -i frame.png -o anim.mp4

# cheapest option
python scripts/generate_video.py "timelapse of clouds over a wheat field" -m veo-3.1-lite-generate-preview -o clouds.mp4
```

## Minimal code (text-to-video, the full async flow)

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A drone shot following a red convertible along a coastal road at "
           "sunset, waves crashing below, the engine roaring loudly.",
    config=types.GenerateVideosConfig(aspect_ratio="16:9", resolution="1080p"),
)

while not operation.done:                 # poll until finished
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)   # fetch the bytes
video.video.save("output.mp4")            # then save promptly (expires in 2 days)
```

## Image-to-video and first/last-frame

```python
# image-to-video: pass a starting frame as `image=`
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="the camera slowly pushes in as steam rises",
    image=types.Image(image_bytes=open("frame.png", "rb").read(), mime_type="image/png"),
)

# first/last-frame interpolation: start image + last_frame in the config
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="a flower blooms",
    image=first_image,
    config=types.GenerateVideosConfig(last_frame=last_image),
)
```

## Key parameters (`types.GenerateVideosConfig`)

| Param | Values | Notes |
|-------|--------|-------|
| `aspect_ratio` | `"16:9"` (default), `"9:16"` | |
| `resolution` | `"720p"` (default), `"1080p"`, `"4k"` | 1080p/4k require 8s; **Lite has no 4k** |
| `duration_seconds` | `"4"`, `"6"`, `"8"` | strings, not ints; 8s required for 1080p/4k, refs, extension |
| `number_of_videos` | `1` | |
| `negative_prompt` | comma-separated nouns | describe what to exclude as objects, **never** "no X" |
| `last_frame` | `types.Image` | with `image=` for interpolation |
| `reference_images` | up to 3 `VideoGenerationReferenceImage` | guide character/object/scene |

`person_generation` (`"allow_all"` / `"allow_adult"`) and `seed` are documented
parameters but were not shown in sample code — verify against the SDK before
relying on them. EU/UK/CH/MENA are restricted to `"allow_adult"`.

## Things to know

- **Always async.** `generate_videos` returns an operation; you must poll `client.operations.get(operation)` until `operation.done`, then `client.files.download(...)` and `.save(...)`.
- **2-day expiry.** Download immediately; the server purges videos after 48h.
- **Native audio** is always on for Veo 3.x — dialogue, SFX, and ambience come from your prompt (see prompting guide).
- **No charge for blocked videos.** Veo occasionally blocks a generation on safety/audio-processing grounds; you aren't billed for those.
- **SynthID watermark** is embedded in all output.
- **Extension** (Veo 3.1 / Fast only) can grow a clip up to ~148s at 720p; pass the prior `video=` back in. Lite can't extend.

## Prompting essentials

Build a descriptive shot: **Subject + Action + Scene + Camera + Composition +
Lighting/Ambiance + Style + Audio cues.** Put dialogue in quotes; describe SFX
and ambience explicitly. For negatives, list nouns to exclude — don't write
"no" or "don't." Full guide and worked examples in `references/prompting.md`.

## More detail

- `references/models-and-pricing.md` — model variants, per-second pricing, durations/resolutions, limits.
- `references/prompting.md` — Veo prompt structure, audio cues, image-to-video tips, negative-prompt rules.
