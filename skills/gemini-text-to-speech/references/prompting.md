# Prompting Gemini TTS

Gemini TTS is a language model that knows not just *what* to say but *how* to
say it. You direct the performance in **plain natural language**, embedded with
the text — not SSML. The model fills in nuance, so the goal is good direction,
not exhaustive control.

## Recommended structure (especially for character/expressive work)

1. **Audio Profile** — who is speaking: identity/archetype, age, background.
2. **Scene** — the physical environment and emotional "vibe."
3. **Director's Notes** — performance: style, pacing, breathing, articulation, accent.
4. **Transcript** — the actual words, with inline audio tags where useful.

**Example:**
> You are a weary lighthouse keeper in his 70s, recounting an old story late at
> night. The room is quiet except for wind against the glass. Speak slowly and
> low, with long reflective pauses and a faint coastal accent.
>
> [sighs] We didn't expect the storm that night. [pause] Nobody did.

## Quick inline direction (single line)

Prefix the text with how to say it:

- `"Say in a spooky whisper: By the pricking of my thumbs..."`
- `"Read this like an upbeat morning-radio host: And that's your traffic update!"`
- `"In a flat, deadpan tone: Wow. Amazing. I'm thrilled."`

## Multi-speaker direction

Direct each speaker, then give labeled dialogue. Names must match the config.

> Make Joe sound tired and bored, and Jane sound excited and happy.
>
> Joe: Another Monday.
> Jane: But it's launch day! Aren't you pumped?

## Inline audio tags

Tags steer delivery mid-sentence. Common ones:
`[whispers]`, `[shouting]`, `[laughs]`, `[giggles]`, `[sighs]`, `[gasp]`,
`[crying]`, `[excited]`, `[bored]`, `[tired]`, `[curious]`, `[amazed]`,
`[panicked]`, `[sarcastic]`, `[serious]`, `[trembling]`, `[mischievously]`.
Pacing: `[very fast]`, `[very slow]`. Tags can combine:
`[sarcastically, one painfully slow word at a time]`.

> `[whispers] Hey... come closer. [shouting] BOO! [laughs] Got you!`

For non-English transcripts, keep the tags in **English**.

## Director's-note tips that work

- **Be specific about accent and persona.** "A Southern-California valley girl from Laguna Beach" beats "a casual accent."
- **Name a vocal quality.** "You should be able to hear the grin in her voice" (a 'vocal smile').
- **Tie pacing to context.** "Speaks at an energetic pace, keeping up with the fast background music."

## Pitfalls

- **Don't over-constrain.** Too many rigid rules limit the model's expressiveness and can make delivery worse. Direct the intent; let it perform.
- **Keep direction and transcript aligned.** Who's speaking, what they say, and how they say it should be consistent — don't ask a "sad" voice to read upbeat copy unless that contrast is the point.
- **Chunk long scripts.** Beyond a few minutes, quality drifts; split into segments and concatenate the WAVs.
- **Tags belong inline**, woven into the text where the effect should happen — not as a separate config field.
