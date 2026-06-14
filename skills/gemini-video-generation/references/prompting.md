# Prompting Veo

A good Veo prompt reads like a shot description from a script: it names the
subject, what it's doing, where, how it's framed and lit, in what style — and
what it sounds like. Assemble these into a vivid sentence or short paragraph.

## The prompt elements

- **Subject** — the person, animal, object, or scenery.
- **Action** — what the subject is doing (walking, turning, accelerating).
- **Scene / context** — where it takes place.
- **Camera position & motion** — `aerial view`, `eye-level`, `top-down`, `dolly shot`, `tracking shot`, `worm's-eye view`, `drone shot`.
- **Composition** — `wide shot`, `close-up`, `two-shot`, `extreme close-up`.
- **Focus & lens** — `shallow focus`, `deep focus`, `macro lens`, `wide-angle lens`.
- **Ambiance** — color and light: `warm golden tones`, `cool blue night`, `harsh midday sun`.
- **Style** — `cinematic`, `film noir`, `horror`, `stop-motion`, `3D animation`.
- **Audio** — see below; Veo 3.x generates sound natively.

## Audio cues (Veo 3.x has native sound)

- **Dialogue:** put speech in quotes, with a speaker descriptor.
  `A man murmurs, "This must be it."` / `She whispers excitedly, "What did you find?"`
- **Sound effects:** describe them explicitly. `tires screeching loudly`, `the engine roars`.
- **Ambient noise:** describe the soundscape. `an eerie hum resonates through the cavern`.

## Worked examples

**Cinematic, with SFX**
> Drone shot following a classic red convertible driven by a man along a winding
> coastal road at sunset, waves crashing against the rocks below. The convertible
> accelerates fast and the engine roars loudly.

**Dialogue scene**
> A close-up of two people staring at a cryptic drawing on a wall, torchlight
> flickering. A man murmurs, "This must be it. That's the secret code." The woman
> looks at him and whispers excitedly, "What did you find?"

**Animation**
> A whimsical stop-motion animation of a tiny robot tending a garden of glowing
> mushrooms on a miniature planet, soft warm light, shallow focus.

## Refine vague → specific

> ❌ "A man on the phone."
>
> ✅ "A close-up cinematic shot of a desperate man in a weathered green trench
> coat dialing a rotary phone mounted on a gritty brick wall, bathed in green
> neon glow, shallow depth of field focused on the tension in his jaw."

Use the word **"portrait"** when you want facial detail to be the focus.

## Negative prompts — the important rule

Veo's `negative_prompt` is a **comma-separated list of things to exclude**, named
as plain nouns/characteristics. **Do not** use instructive language like "no" or
"don't."

> ❌ negative_prompt: "no walls, don't show frames"
>
> ✅ negative_prompt: "wall, frame"

## Image-to-video tips

- Pick a starting image that looks like the **first frame** of the shot you want.
- Great for: animating a still product/photo, bringing a drawing or painting to life, adding motion + sound to a static nature scene.
- Describe the *motion and camera move* you want from that frame onward, plus any audio.

## Pitfalls

- Forgetting it's async — you must poll and then download (and within 2 days).
- Instructive negatives ("no X") — list nouns instead.
- Requesting 4K on Lite, or extension on Lite — unsupported.
- Expecting 1080p/4k at 4 or 6 seconds — those resolutions require 8s.
- Vague prompts — Veo rewards specific camera, lighting, and audio direction.
