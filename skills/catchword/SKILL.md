---
name: catchword
description: Evaluates and repairs a chapter's opening (hook) and ending (pull). Scores both 1-10, rewrites the first and last three to five sentences when they fall below threshold, and enforces hook-type variation so no two consecutive chapters open the same way. Dialogue and structure are left alone. Use in Incunabula Phase 3.2.
---

# Catchword

A *catchword* is the single word a compositor sets at the foot of a page — the first word of the
next one — so the reader's eye is already moving before they decide to turn. It exists to be
followed.

You are the catchword. You do not write the chapter; you make its first line pull the reader in and
its last line push them forward.

## When You Run

Phase 3.2, after `register`, once per chapter. The Pass must not be applied to a chapter whose
`Register` pass has not run.

## Before You Start

1. Read the chapter: `manuscript/chapters/chapter-[N].md`.
2. Read `outline.md` for the next chapter — its opening must not be pre-empted, and its hook type
   must differ from this chapter's.
3. Read `voice-matrix.md`. Anything you write must be in the POV character's voice, not yours.
4. Read the previous chapter's ending to establish the transition.

## The Two Scores

Score each **1–10** and cite the exact text you are scoring. A score without a citation is invalid.

- **Hook** — the opening. Does the first sentence create a question, a friction, or a forward lean?
- **Pull** — the ending. Does the last line make the next chapter feel necessary?

**Pull is not required of every chapter, and that is the point.** A book where all eleven
chapters end on a line engineered to make the next one feel necessary does not read as
tense. It reads as a metronome, and it is the clearest mechanical signature a finished book
can carry. Check `tools/check-uniformity.py` before scoring: published prose closes **0 of 50**
chapters on an explanatory coda, and the books this system produced close 15 of 25 on one.

So: score the Pull of a chapter *against what that chapter is for*. A quiet chapter that
ends flat and lets the reader breathe is not a 4. A chapter that ends on a rhetorical coda
designed to sound profound is not a 9 — it is a defect, and `F1` fails it outright.

**Thresholds by positioning** (from the state file):

| Positioning | Hook | Pull |
|---|---|---|
| Commercial / thriller | >= 7 | >= 7 |
| Literary | >= 6 | >= 6 |

## Hook Types

Classify the opening and record it. The type **must differ from the previous chapter's type**. No
two consecutive chapters may open the same way.

1. **In-scene action** — the reader lands mid-motion.
2. **Statement of fact** — a hard, declarative line that poses a question by its bluntness.
3. **Image** — a concrete sensory picture before any person arrives.
4. **Voice / interior** — the character's mind mid-thought, no framing.
5. **Dialogue** — the chapter opens on a line of speech, unattributed. The line does not
   have to be plot-bearing. A hook's job is to make the reader stay, and a beat the reader
   has to sit through does that as well as a revelation and without spending the chapter's
   only surprise. If the opening line is doing plot work, the chapter has spent its hook in
   the first paragraph and has nothing left to withhold.
6. **Time / place shift** — a clean spatial or temporal dislocation.
7. **Object** — a thing described with weight, the person secondary.
8. **Question** — an explicit or implied question the chapter then delays.

## Ending Types

Classify the closing the same way, with the same rule: **the type must differ from the
previous chapter's type.** Openings have had this discipline from the start; endings never
did, and that is where the uniformity crept in.

1. **Plain stop** — the scene finishes and the chapter finishes. No gesture, no turn, no
   last word placed for effect. The commonest ending in published prose and the one this
   system under-uses.
2. **Mid-action cut** — the chapter stops before the action resolves.
3. **Dialogue exit** — the closing line is speech, with no narration after it to interpret it.
4. **Image held** — a concrete picture, and then nothing. No sentence telling the reader what
   the picture meant.
5. **Reversal** — the last line re-reads the preceding scene. Earned, and used at most once
   or twice in a book.
6. **Question left open** — an explicit question the chapter does not answer.
7. **Time jump** — the chapter steps past itself, forward or back.
8. **Understatement** — a deliberately flat, anticlimactic line where the scene promised more.

**Not a type: the coda.** *That is why…* *Which is why…* *It is also why…* *the next chapter
is about…* — an ending that explains the chapter's meaning to the reader. It can be scored
as a 9 and still be wrong; it is a separate rule (`F1`) and it fails on its own. The test is
simple: cut the coda and see whether the chapter still lands. If it does, the coda was
furniture. If it does not, the scene is the problem, not the ending.

**Shape budget.** Across a book, at least a third of chapters should close on type 1 or 8.
A manuscript where every chapter ends on a curated note has no plain endings in it, and the
absence of plain endings is the tell — see **Consistency Is the Fingerprint** in the
deslopify guide.

## The Repair

If Hook or Pull is **below threshold**, rewrite the relevant end:

- **Hook:** rewrite the first 3–5 sentences.
- **Pull:** rewrite the last 3–5 sentences.
- Keep the POV character's voice from `voice-matrix.md`.
- Do not change what happens — change when the reader learns it.
- The new opening must take a **different hook type** from the previous chapter.
- Remove invented tension: no "little did she know," no rhetorical questions to the reader, no
  weather-as-emotion openers (pattern #7, pattern #9).

If both scores clear threshold, **change nothing** and say so. A pass that edits a working opening
has made it worse.

## Prohibited Openers

Never repair toward any of these — they are the system's tell:

- Weather or scenery as the first beat, standing in for mood.
- The character waking, or arriving, or "little did she know."
- A pseudo-philosophical generalisation.
- An explanatory Overprint in the first sentence — the image completed and unpacked.
- A symmetrical construction ("By day X, by night Y").

## Output

Append the scores to `evaluations/eval-chapter-[N].md` (create it if the Evaluator has not yet run):

```markdown
## Catchword

**Hook:** [n]/10 — "[exact first sentence]" — type: [type]
**Pull:** [n]/10 — "[exact last sentence]" — ending type: [type]
**Previous chapter hook type:** [type] — differs: yes/no
**Previous chapter ending type:** [type] — differs: yes/no
**Plain endings so far:** [n] of [chapters written] — must reach a third by the last chapter
**Coda check:** none present — [if present, say so; F1 fails the chapter regardless of Pull]
**Rewritten:** no / hook / pull / both
**Before → after (opening):** "…" → "…"
**Before → after (ending):** "…" → "…"
**Passing Reader check:** would they turn the page? yes/no — [why]
```

Record the hook type in the state file's chapter entry so the next chapter can differ from it.
