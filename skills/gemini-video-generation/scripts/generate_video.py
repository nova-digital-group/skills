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
import os
import sys
import time

from google import genai
from google.genai import types

try:
    from google.genai import errors as genai_errors
except ImportError:  # pragma: no cover - very old SDKs
    genai_errors = None

# Veo jobs finish in ~11s to ~6min; 20 min is a generous ceiling before we stop
# polling so the script can't hang forever on a stuck operation.
MAX_POLL_SECONDS = 20 * 60


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

    client = make_client()

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
    try:
        operation = client.models.generate_videos(**kwargs)
    except Exception as e:  # noqa: BLE001 - clean message, not a traceback
        if genai_errors and isinstance(e, genai_errors.APIError):
            print(f"error: submit failed ({getattr(e, 'code', '?')}): "
                  f"{getattr(e, 'message', e)}", file=sys.stderr)
            return 1
        raise

    print("Polling (videos take ~11s to ~6min)...")
    waited = 0
    while not operation.done:
        if waited >= MAX_POLL_SECONDS:
            print(f"error: still not done after {MAX_POLL_SECONDS // 60} min — "
                  "giving up polling. The job may still finish server-side.",
                  file=sys.stderr)
            return 1
        time.sleep(args.poll_interval)
        waited += args.poll_interval
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
