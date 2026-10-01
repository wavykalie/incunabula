---
name: composing
description: Mechanical cleanup pass on a chapter or batch. Runs the shell pipeline for em-dash cap, the Overprint, adverb density, sentence-start repetition, and filter words, then reviews every diff for false positives before applying. No structural or creative changes. Use in Incunabula Phase 3.8.
---

# Composing

A compositor does not write. The compositor takes the author's copy and sets it — correct measure,
even spacing, no strays, no turned letters. The work is mechanical and it is checked.

You are the composing pass. Every change you make is measurable, and every change is reviewed.

## When You Run

Phase 3.8, after the Quoin and before `proof-panel`. Per chapter, or across a batch. This is a
mechanical pass — it must not become a prose revision.

## The Pipeline

Run the checks against the project's calibrated thresholds. Where a threshold is not recorded,
read it from the project's calibration record — **never from taste**.

```bash
# 1. Em-dashes -- measured cap: 10 per 1,000 words, warn above 7
#    (the old per-page genre figures were guesses and failed most published prose)
grep -o "—" "$CHAPTER" | wc -l
awk 'END{print NR}' "$CHAPTER"        # for the per-1,000 basis

# 2. The Overprint -- completed, unpacked similes (the single worst fingerprint)
grep -nE "like |as if |as though " "$CHAPTER"

# 3. Adverb density -- flag above 2 per page
grep -oE "\b\w+ly\b" "$CHAPTER" | wc -l

# 4. Sentence-start repetition -- no 3+ consecutive paragraphs opening the same way
grep -nE "^[A-Z][a-z]+ " "$CHAPTER"

# 5. Filter words -- just, really, very, quite, rather, somewhat
grep -noiE "\b(just|really|very|quite|rather|somewhat)\b" "$CHAPTER"
```

Also scan for: turned letters and doubled words, em-dash overuse against the cap, forced symmetry
("by day X, by night Y"), rule-of-three, and empty poetic vocabulary (tapestry, symphony, journey,
dance).

# 6. Uniformity -- a whole-manuscript check, not a per-chapter one
bash tools/check-uniformity.py                 # or: python tools/check-uniformity.py <book>

# 7. Surplus -- reports, never gates. How much of the dialogue carries no plot.
python tools/check-surplus.py <book>           # speech-turn distribution + spread across chapters

# 7b. Recoverable -- reports, never gates. Is each tic somewhere the text licensed it?
python tools/check-recoverable.py <book>       # per-chapter tic x dialogue enrichment

# 8. The pipeline's own protocol -- PRINTERS_COPY.md and ERRATA.md. Not a prose check.
python tools/check-errata.py                   # end of a project, and after any change

Every counter above reads one chapter and compares it to a rate. None of them can see the
failure that comes from every chapter being the same, because none of them ever holds two
chapters at once. Run this step in batch mode and at the end of the manuscript.

It reports three things, each measured against published prose:

- **U1 chapter-length variance** — fails a book whose chapters all land within a few percent
  of each other. Published volumes run 48–71% CV; the books this system produced ran 3.2%.
- **U2 rhythm variance** — fails a book whose chapters share one sentence-length profile.
- **U3 coda distribution** — fails a book where too many chapters close on an explanatory
  coda. Published prose: 0 of 50 chapters.

**U4 and U5 are paragraph rows and they do not have the same standing.** U5 (paragraph-length
variance) is enforced: across 140 public-domain English novels — 13.06M words, five eras —
**not one** falls below its failure line, and machine prose is the flat one in every corpus
measured. U4 (one-line paragraph share) is **advisory unless the book declares
`paragraph_convention: commercial-dialogue`**, because its median on that same 13M-word human
corpus is 33.2% — below its own 35% failure line — and 59% of the corpus falls under it. Read
U4's number; do not act on it as a gate unless the book asked to be held to it.

A failure here is **not** fixed by editing sentences. It is fixed by varying chapter length,
changing what a chapter ends on, and letting at least a third of chapters end plainly. Send
it to `quoin` (operation 9) or `catchword` (ending types), not back through this pass.

Step 7 reports and never fails, because nothing about surplus has a measured threshold yet.
Read the **spread across chapters** row, not the mean: a book whose chapters all land within
a couple of points of each other has one tempo for its whole dialogue, and that is the
failure no per-chapter counter here can see. Do not delete dialogue to move the number — the
remedy is a scene in which two people are in a place the plot does not require them to be in.
That is a `setting` brief, and cutting is how you get the thing the check is measuring.

Step 7b reports on **register, not intent**, and that distinction is the whole of its limit. A
tic above 1.0 lives in speech, where a character's voice is the excuse for it; a tic below 1.0
lives in narration, where nothing in the text lets a reader recover it. So the fix is a
**movement** — into a character's mouth — not a deletion, and it is `setting`'s job, not this
one. Two things it will not tell you: whether a clipped sequence was deliberate (the
positional axis that would have tried measured flat, Gini 0.00-0.07 in every corpus), and
whether a tic is present at all. It also cannot help the rare tics, which occur in one to
four documents and have no measurable enrichment. And a book can score well here while being
poor: dialogue is the easiest place to hide a tic, and concentrated slop is still slop. It is
a question to put to the book, never a score to optimise.

Step 8 is not about this book at all — it checks the pipeline's own guidance, and belongs at
the *end* of a project rather than in the per-chapter loop. It exists because this system is
meant to improve across books, and a ledger that nobody validates is a ledger collecting
confident opinions. It also refuses to let the **rejected**-measures registry shrink, which
is the one failure a self-improving layer cannot detect about itself.

## The Review Gate

**You do not apply a diff you have not read.** The counters flag candidates; they do not decide.
Uniformity is the one row you may not silent-pass: a `check-uniformity.py` failure has to be
either fixed or waived in writing, because the whole point of the row is that it cannot be
talked out of by reading the chapter on its own.

For each flagged line: read it in context and decide — defect, or deliberate?

- A simile the Writer deliberately left raw is **not** an Overprint.
- An adverb that is the only correct word in the sentence stays.
- A repeated sentence start can be **anaphora** — a deliberate device. Anaphora is kept; accidental
  repetition is fixed.
- A filter word in dialogue is often characterisation. It stays.
- An em-dash used as the character's actual interrupted thought stays.

Report the false positives you rejected. A pass that "fixes" deliberate prose has done damage.

## What You Must Not Do

- Do not restructure, re-order, or re-write.
- Do not change voice, imagery, or rhythm.
- Do not silently apply a batch replacement. Apply line by line.
- Do not chase a zero score. Human bestsellers score 0–13 on the Tic Scan; the target is
  genre-appropriate, not zero, and 0/20 is suspicious rather than clean.

## Output

Write the report to `evaluations/composing-chapter-[N].md`:

```markdown
# Composing: Chapter [N] (or chapters [range])

**Basis:** [word count] words

| Check | Threshold | Found | Verdict | Applied |
|---|---|---|---|---|
| Em-dashes | <=10 / 1,000 (warn >7) | [n] | pass/fail | [n] fixed |
| Overprint | genre target | [n] | pass/fail | [n] cut |
| Adverb density | <=2 / page | [n] | pass/fail | [n] fixed |
| Sentence-start repeats | no 3+ consecutive | [n] | pass/fail | [n] fixed |
| Filter words | within limit | [n] | pass/fail | [n] fixed |

## Applied
| Line | Rule | Before | After |
|---|---|---|---|

## Rejected as deliberate (false positives)
| Line | Rule | Why kept |
|---|---|---|

## Not verifiable mechanically
[Anything the counters cannot see that the read-aloud pass must still catch]
```

Update `composing` counters in the state file. Then dispatch `proof-panel`.
