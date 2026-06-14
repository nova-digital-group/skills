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

Tags steer delivery mid-sentence — 3.1 Flash TTS supports **200+**. Interleave
them with the text at the exact point the change should happen:
`[pacing] words [emotion] words [pause] words`.

- **Emotion / tone:** `[excited]`, `[bored]`, `[tired]`, `[curious]`, `[amazed]`,
  `[panicked]`, `[sarcastic]`, `[serious]`, `[determination]`, `[enthusiasm]`,
  `[awe]`, `[nervousness]`, `[frustration]`, `[hope]`, plus polarity
  `[positive]` / `[neutral]` / `[negative]`.
- **Sounds / non-verbal:** `[laughs]`, `[giggles]`, `[sighs]`, `[gasp]`,
  `[crying]`, `[cough]`, `[mischievously]`, `[trembling]`.
- **Pacing:** `[slow]`, `[fast]` (and descriptive `[very fast]`).
- **Pauses:** `[short pause]`, `[long pause]` — for timing dramatic beats.
- **Character:** creative tags work too, e.g. `[like dracula]`, `[like a cartoon dog]`.

Tags can combine descriptively: `[sarcastically, one painfully slow word at a time]`.

> `[whispers] Hey... come closer. [long pause] [shouting] BOO! [laughs] Got you!`

**Two hard rules:**
- **Never place two tags directly adjacent** (`[slow][whispers]`) — separate
  them with text or punctuation, or the model throws an error.
- For non-English transcripts, keep the tags themselves in **English** even
  though the spoken words are in another language.

## Accents and pronunciation

- **Accent:** describe it in the style direction — *"with a London Brixton
  accent,"* *"a Southern-California valley-girl cadence."* Accents come from the
  prompt, **not** from any language/accent parameter (there isn't one; language
  is auto-detected from the text).
- **Pronunciation:** there's no SSML/IPA/phoneme control. If a name or term is
  mispronounced, **respell it phonetically** in the transcript
  (e.g. "Cholmondeley" → "Chum-lee").

## Director's-note tips that work

- **Be specific about accent and persona.** "A Southern-California valley girl from Laguna Beach" beats "a casual accent."
- **Name a vocal quality.** "You should be able to hear the grin in her voice" (a 'vocal smile').
- **Tie pacing to context.** "Speaks at an energetic pace, keeping up with the fast background music."

## Pitfalls

- **Don't over-constrain.** Too many rigid rules limit the model's expressiveness and can make delivery worse. Direct the intent; let it perform.
- **Keep direction and transcript aligned.** Who's speaking, what they say, and how they say it should be consistent — don't ask a "sad" voice to read upbeat copy unless that contrast is the point.
- **Chunk long scripts.** Beyond a few minutes, quality drifts; split into segments and concatenate the WAVs.
- **Tags belong inline**, woven into the text where the effect should happen — not as a separate config field.
