# ASSUMPTIONS — Book 1

Phase 0. **What is given, what is open, and what must not be decided by the agent.**

Created 2026-09-22.

---

## EXCLUSION RULE — read before any creative decision

**User instruction, 2026-09-22:** *Drop all context of our old book we wrote before, the one labeled
finished.*

The finished novel **Coldbrook Junction** is **out of scope for this project.** Its premise, engine,
cast, structure, motifs, chapter-title patterns and craft habits must not inform this book. Where a
choice here resembles it, that resemblance is a defect — redo the choice.

Forbidden by this rule:

- a place that takes, keeps or absorbs people;
- a ledger, record or guest book of the dead;
- a companion who pays so the protagonist can continue;
- a relationship that must be damaged to mean anything;
- titles of the form What the X Kept.

---

## PROSE RULE — standing instruction

**User instruction, 2026-09-22:** *"When writing, use the humanizer, never use signs of AI writing,
and throw it through a deslopifyer to see if it passes."*

This applies to **every drafted chapter**, and it is a gate rather than a preference. A chapter is
not "drafted" until it passes. It does not apply to the engineering documents in this project.

**1. Write with the humanizer's rules in force.** The `humanizer` skill covers significance
inflation, promotional language, superficial `-ing` analyses, vague attribution, em-dash overuse,
rule of three, AI vocabulary, negative parallelism, filler and hedging. Its second half matters
more here: **clean-but-voiceless prose is also a fail.** Varied rhythm, opinions, specifics, some
mess.

**2. Write with the tropes.fyi list in force.** The `deslopify` skill is installed at
`.agents/skills/deslopify/`; its `references/style_guide.md` is the full anti-pattern list from
tropes.fyi across word choice, sentence structure, paragraph structure, tone, formatting and
composition. Read it before drafting. Where that list and this file disagree, it wins.

**3. Prove it, do not assert it.**

```
bash tools/deslop-check.sh book-1/manuscript/chapters/chapter-01.md
```

Required to PASS. A FAIL means the chapter is not finished, no matter how well it reads.

**The thresholds are measured, not guessed.** Calibrated against **175,144 words / 48 narrative
documents** of the reference register (*Wandering Witch: The Journey of Elaina*, Yen Press, vols.
1/2/5), with *Coldbrook Junction* chs. 1–11 as a native-English control. The rule list itself was
calibrated too: a phrase stays zero-tolerance only if it has **0 hits in that corpus**. Anything
published prose actually does — `quietly`, `landscape`, em-dash appositives, `in order to`,
*Not X. Not Y.* — is density-capped instead of banned.

Validated in both directions, because both directions matter:

```
bash tools/validate-controls.sh
```

The 51 reference files (48 narrative + 3 back matter) produce **0 failing rows**, the synthetic slop
fixture **FAILS with 17 failing rows**, and the pipeline's own earlier book (*Coldbrook Junction*)
**fails 9 of 11 chapters** while 2 pass. That last one is the control that matters: a scanner that
fails everything is a blanket rule, and one that passes everything is decoration. Full derivation
and evidence: `tools/calibration/CALIBRATION.md`.

**An empty scan is a failure, not a pass.** This is not a hypothetical rule. The corpus control was
recorded as "48/48 PASS" while directory mode globbed `*.md` only, so the `.txt` corpus matched
zero files, no check ran, and the run printed PASS. Both the scanner and the runner now treat a
zero-file expansion as a failure.

**A check that cannot fail is not a check.** The P3 short-fragment check printed the opener's
second word where its run length belonged, so its comparison was always an error, and an error is
false. It reported `ok` for every document it had ever scanned, including the slop fixture. Fixing
the read-back immediately exposed a second problem: the threshold of 6 failed published prose, so
it is now 7. All three defects found this way ran in the permissive direction, which is the only
direction that matters for a gate.

**This gate is now a required pipeline phase gate, not a project preference.** It sits at Phases 3
(Drafting), 4 (Adversarial Audit), 6 (Final Score) and 7 (Editorial Package) in
`book-genesis/references/pipeline/phases.md` and `manifest.yaml`, with the thresholds, tier rules
and control expectations in `book-genesis-codex/references/scoring/prose-gate.md`. A chapter, a
score, or a package does not advance while the gate is failing.

**What the scanner cannot see.** It catches mechanical patterns. It cannot see voice, rhythm, a
dead metaphor beaten into the ground, or one argument restated ten ways. Passing is necessary,
not sufficient — the chapter still has to be read aloud. Its duplicate-sentence check (P2) also
false-positives on deliberate refrains, so read P2 hits before rewriting them.

**Provenance, stated plainly.** `deslopify` is a third-party community skill
(github.com/glaforge/deslopify) grounded in tropes.fyi. It is a rule set, not an executable: it
cannot check anything by itself. The scan is what actually runs, and it was written for this
project. Neither is authoritative about taste.

---

## Source rule

Everything treated as true in this project is either:

1. **User-sourced** — stated by the user in this session, recorded in `INTAKE.md`, or
2. **Explicitly approved by the user at a gate**, or
3. **Marked ASSUMPTION below**, which means *provisional, must be shown at the next gate, and
   must be easy to reverse.*

Anything not in one of those three categories does not exist. This rule exists because the
previous build failed exactly here: the agent authored a planet name, a species name, a
communication medium, character wounds, a theme, nine chapter titles and a character's fate
without asking, and the story engine it authored was another book's.

---

## Given (user-sourced)

| Item | Value |
|---|---|
| Protagonist / narrator | **Merope**, 19 |
| Partner | **Achird**, 19, kuudere |
| Relationship | **Unspoken** — the book is where the romance fails to happen |
| Achird's want | **To be seen by Merope** |
| Vehicle | **Amendment (2026-09-22):** NOT a chariot, no horse. An **old-style sleigh** — glazed enclosed cabin on runners — whose **steed is drawn from a constellation and morphs into that constellation's shape**. Achird owns and pilots it; Merope narrates as if she were the pilot. It is **its own character** and will act on its own to save someone |
| Structural decisions | **A** the world was expecting them / **B** Achird finds the belongings first and is not believed / **C** no host, no confrontation, no chase |
| Tone balance | **Partly escalatory** — movement I genuinely warm; dread enters late and rises steadily; dread never announces itself |
| References | **A** Elaina (POV/register) · **B** Twinstar Cyclone Runaway (tone, the pair) · **C** Shoujo Seikan Hyouryuuki (format). All read; see `references/tone-references.md` |
| Setting | A peaceful planet; silicon-based, hedge-like beings |
| The beings | **Friendly aliens, very inviting** |
| Fate of prior visitors | **They all died, and the hedges grew from them** |
| The danger | **The hospitality is the mechanism** — being welcomed and kept comfortable is how visitors stay long enough to die. No absorption, no chorus |
| Do the beings know | **No.** Genuinely innocent; no idea they are grown from the dead |
| The crisis | **Merope refuses to leave. Achird has to act** |
| Theme question | Does a place that asks nothing of you keep you from becoming anything? — never answered |
| Shape | **7 chapters**, ~2,450 words each (~17,150 total) |
| Naming | **Nothing is named.** No planet name, no name for the beings |
| The ending | **Growth, not damage.** Merope realises Achird loves her; too tsundere to say it plainly, but it is acknowledged |
| Merope, extra trait | **Tsundere** |
| Merope's voice | Grandiose, certain, self as center; boastful then cruel under pressure |
| Merope's register | First person, "narcissistic… in the style of Merope" |
| Chapter narration | Tight present tense, single POV |
| Fact presentation | In the style of *The Wandering Witch: The Journey of Elaina* |
| The "you" addressed | **The reader, directly** |
| Positioning | Short novel / serial installment |
| Delivery form | Outline + scene packets |
| Length | **60 formatted pages (~15,000–18,000 words)** |
| Book 2 scoped change | New location + changed Merope/Achird relationship state |

---

## Content boundary (author-set)

- **On-page violence, dread and body horror are permitted** when the scene requires them.
- **Intimacy may be on-page when the scene requires it.** Both characters are **adults (19)**, so
  no minors-based restriction applies. This is the author's standing instruction: *"adult — both
  allowed when the scene requires it."*
- **Correction on the record:** earlier in this project I set intimacy to "non-explicit, always"
  on my own assumption that "teenage" meant minors. That was my inference, not the user's
  instruction. The ages are 19. **The restriction is lifted.**
- The standard is "when the scene requires it" — it is not a licence to insert sex where a scene
  does not need it.

---

## ASSUMPTIONS (provisional — must be shown at the Phase 2 gate)

The previous build invented facts silently. These are the minimum scaffold needed to run
Phase 1 research, and each is flagged so you can kill it:

- **A1 — Genre shelf.** Treat "quiet exploration SF with a horror turn" as a *research* frame only,
  used to find comps. It is not a positioning decision.
- **A2 — Length floor/ceiling.** 12,000 / 20,000 words as the tolerance band around the 60-page
  target. Arithmetic, not creative.
- **A3 — Prose comps.** Any comp beyond Elaina is a *proposal* in `artifacts/01-market-map.md`,
  not canon. None are approved.

---

## OPEN — do not fill these in

- Planet name; beings' name. (Constellation names **are** permitted — the vehicle's steed is named
  for the constellation it is shaped from.)
- ~~The chapter 4 discovery~~ — **settled: only belongings. No bodies, and the absence is the
  horror.**
- Whether anything else is alive on the planet.
- Whether the beings approach them differently than they approached prior visitors.
- How long they have been there when the pile is found.
- **Chapter titles — DEFERRED by user.** Nothing is titled until the chapters are drafted. Do not
  propose title sets.
- The detailed beats of chapters 6-7.

**No longer open (settled):** ages (19); relationship at open (unspoken); the beings' knowledge
(they do not know what they are); the theme; the chapter count; the ending; naming.

**Deliberately unstated, and that is the decision:** both girls' histories, origins, why they
travel, and what the sleigh is. **Merope does not explain herself.** That is characterization,
not an omission to be filled later.

**If a phase cannot proceed without one of these, the phase stops and asks. It does not decide.**
