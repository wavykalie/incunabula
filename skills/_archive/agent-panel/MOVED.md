# MOVED — `agent-panel` → `reader-swarm --light`

Retired 2026-10-15. Use `reader-swarm` with the **`--light` preset** (its SKILL.md,
"The light preset: `--light` (the market panel)").

What moved where:

- **The four voices** — literary agent, acquiring editor, bookseller / category buyer,
  target reader — are the preset, unchanged. They were a strict subset of the swarm's
  `package-reaction` default cohorts.
- **The verdict contract** — PASS / FLAG / BLOCK per voice, overall = the weakest of the
  four, one block means not market-ready — carries over unchanged.
- **The output** is still one file, `evaluations/agent-panel.md`.
- **The cost contract** (cheap gate vs. deep instrument) is now stated in
  `reader-swarm/SKILL.md`: the light preset runs often; the full swarm runs twice per
  book, pre-launch and post-draft.

This directory keeps the original skill and its `agents/openai.yaml` for provenance.
Do not dispatch it.
