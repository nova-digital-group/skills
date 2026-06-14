#!/usr/bin/env python3
"""Generate video with the Google Gemini API (Veo 3.1 / Fast / Lite).

Veo is an ASYNCHRONOUS long-running operation: this script submits the job,
polls until it's done (~11s to 6min), then downloads the MP4. Generated videos
are deleted from the server after 2 days, so download promptly.

Requires: pip install google-genai
Auth:     export GEMINI_API_KEY=...   (or GOOGLE_API_KEY)

Examples:
    # text to video
    generate_video.py "a paper boat sailing down a rain gutter, cinematic" -o boat.mp4

    # portrait, 8s, 1080p
    generate_video.py "neon alley at night, a cat darts past" --aspect-ratio 9:16 --duration 8 --resolution 1080p

    # image to video
    generate_video.py "the camera slowly pushes in as steam rises" -i frame.png -o anim.mp4

    # cheapest model
    generate_video.py "timelapse of clouds over a field" -m veo-3.1-lite-generate-preview
"""
import argparse
import mimetypes
import sys
import time

from google import genai
from google.genai import types


def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "image/png"


def main() -> int:
    p = argparse.ArgumentParser(description="Generate video with Veo (async).")
    p.add_argument("prompt", help="Describe the shot: subject, action, camera, lighting, style, audio.")
    p.add_argument("-o", "--output", default="output.mp4", help="Output MP4 path.")
    p.add_argument("-m", "--model", default="veo-3.1-generate-preview",
                   help="Veo model id (default: veo-3.1-generate-preview). "
                        "Use -fast- for cheaper, -lite- for cheapest (no 4k/extension).")
    p.add_argument("--aspect-ratio", choices=["16:9", "9:16"], default=None)
    p.add_argument("--resolution", choices=["720p", "1080p", "4k"], default=None,
                   help="1080p/4k require --duration 8; lite has no 4k.")
    p.add_argument("--duration", choices=["4", "6", "8"], default=None, help="Seconds (string).")
    p.add_argument("--negative-prompt", default=None,
                   help='Comma-separated nouns to exclude, e.g. "wall, frame" (never "no X").')
    p.add_argument("-i", "--image", default=None, help="Starting frame for image-to-video.")
    p.add_argument("--poll-interval", type=int, default=10, help="Seconds between status checks.")
    args = p.parse_args()

    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY

    cfg = {}
    if args.aspect_ratio:
        cfg["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        cfg["resolution"] = args.resolution
    if args.duration:
        cfg["duration_seconds"] = args.duration
    if args.negative_prompt:
        cfg["negative_prompt"] = args.negative_prompt

    kwargs = {"model": args.model, "prompt": args.prompt}
    if cfg:
        kwargs["config"] = types.GenerateVideosConfig(**cfg)
    if args.image:
        try:
            with open(args.image, "rb") as f:
                data = f.read()
        except OSError as e:
            print(f"error: cannot read image {args.image}: {e}", file=sys.stderr)
            return 2
        kwargs["image"] = types.Image(image_bytes=data, mime_type=guess_mime(args.image))

    print("Submitting video job...")
    operation = client.models.generate_videos(**kwargs)

    print("Polling (videos take ~11s to ~6min)...")
    while not operation.done:
        time.sleep(args.poll_interval)
        operation = client.operations.get(operation)
        print("  ...still generating")

    if getattr(operation, "error", None):
        print(f"error: generation failed: {operation.error}", file=sys.stderr)
        return 1

    videos = getattr(operation.response, "generated_videos", None)
    if not videos:
        print("error: no video returned (possibly blocked by safety filters — "
              "blocked generations are not billed).", file=sys.stderr)
        return 1

    video = videos[0]
    client.files.download(file=video.video)
    video.video.save(args.output)
    print(f"Saved video to {args.output} (download within 2 days — the server purges it).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
