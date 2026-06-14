# Contributing

Thanks for helping keep these skills accurate. Because they wrap a fast-moving
API, the most valuable contributions are **fact updates** — new model ids,
pricing changes, and preview models graduating to GA.

## Ground rules

- **Verify against the official docs before changing a fact.** Every reference
  file cites the page it was researched from and the date. When you update a
  number or model id, update that date and the source link too.
  - Models: https://ai.google.dev/gemini-api/docs/models
  - Pricing: https://ai.google.dev/gemini-api/docs/pricing
  - Image / Speech / Video guides under https://ai.google.dev/gemini-api/docs/
- **Prefer non-`-preview` model ids** in examples once a GA id exists; quarantine
  retired ids in the catalog tables rather than leaving them in the happy path.
- **Keep `SKILL.md` lean.** Triggering text and the fast path live in `SKILL.md`;
  long detail (full catalogs, prompting guides) goes in `references/`. Aim to
  keep each `SKILL.md` body well under ~500 lines.
- **Scripts should fail clearly, not crash.** Check for the API key up front,
  surface API errors as readable messages, and detect safety blocks vs. empty
  responses. Justify any magic number (poll interval, retry count) in a comment.
- **Never commit API keys or generated media.** `.gitignore` already excludes
  `.env`, `*.key`, and common media outputs.

## Submitting

1. Make the change on a branch.
2. `python -m py_compile skills/*/scripts/generate_*.py` to confirm the scripts
   still parse.
3. If you can, smoke-test against a real key (`export GEMINI_API_KEY=...`).
4. Open a PR describing what changed and linking the official doc that confirms
   it.

Issues and PRs welcome — especially updates when Google rotates model ids or
graduates preview models to GA.
