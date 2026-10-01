---
name: proof-pull
description: Quality gate auto-loop for a chapter. Evaluates, identifies the single top weakness, dispatches a targeted fix, and re-evaluates, up to three iterations. Clears the genre threshold or escalates a structural failure to the orchestrator instead of churning. Use in Incunabula Phase 4.5.
---

# Proof Pull

In a hand press you do not print the edition on the first impression. You *pull a proof*, look at
it, correct the forme, and pull again. The proof is not the book. It is the check that tells you
whether the book is ready.

You run that loop. You do not write, and you do not judge the whole manuscript — you gate one
chapter at a time.

## When You Run

Phase 4.5, after `proof-panel` has evaluated the chapter. Maximum **three iterations**. A chapter
that has been revised twice and is still short is not improved by a third pass — it is escalated.

## Thresholds

The gate is the **Platen** — the lowest dimension of the Incunabula Score, not the average.

| Positioning | Floor threshold |
|---|---|
| Literary | 7.5 |
| Memoir | 7.5 |
| Commercial | 7.0 |
| Thriller | 7.0 |
| Prescriptive NF | 7.0 |

- **>= 8.0** — recommended for editorial submission.
- **>= 8.5** — bestseller / award level.
- Below the genre threshold after three iterations → **escalate**, do not loop again.

Also required before the chapter may advance:

- **Prose gate:** the calibrated scanner (`tools/deslop-check.sh`) passes. A passing scan is never
  evidence that the prose is good — it is an input, not a verdict.
- **Passing Reader:** if the verdict is "would not keep reading," treat it as CRITICAL regardless of
  score. This overrides the floor.

## The Loop

1. **Read** the evaluation at `evaluations/eval-chapter-[N].md`. Take the score per dimension with
   its evidence.
2. **Identify the single top weakness** by the revision taxonomy, in this order — structural,
   connective, prose, factual. Never fix prose before structure. One weakness per iteration.
3. **Dispatch a targeted fix.** Structural → `corrector` (or loop back to `forme` if the problem is
   the outline). Prose → `corrector`. Factual → `corrector`.
4. **Preserve the strengths.** Carry forward the Evaluator's top-3 strengths as explicit constraints
   on the fix. A revision that improves the weakness and degrades a strength has failed.
5. **Re-evaluate** with `proof-panel`. Compare to the previous score.
6. **Score integrity:** no jump greater than **+0.5** per revision cycle. A larger jump must be
   justified with textual evidence or the score is rejected and re-run. Assume self-scoring is
   inflated by 0.5–1.0.
7. **Stop** when the floor clears the threshold and the strengths survive, or after three iterations.

### The two whole-book checks that this loop does not own

`check-surplus.py` and `check-arc.py` operate on a **book**, not a chapter, so they do not
belong in this per-chapter loop and running them here would produce numbers too small to
read. Run them in `composing` at manuscript stage, and carry the result into the loop in one
specific way — as a **constraint on the fix**, never as a score to optimise:

- **Arc (`A1`).** A book failing the reversal floor is travelling in one direction. The fix is
  a **scene that changes the reader's expectation** — not sentiment words, which move arc
  *range* and not the reversal rate, and not a cut, which is how you get a book that is
  uniformly varied and emotionally flat. The null is 0.5: human prose sits at 0.571, machine
  prose at 0.501. Below 0.45 is not merely flat, it is *smoother than noise*.
- **Surplus (`S1`).** A book whose speech-turn lengths all sit within a couple of points of
  each other has one tempo for its whole dialogue. The fix is a **scene**, briefed to
  `setting` — two people in a place the plot does not require them to be in. Never a trim.

Both are `aesthetic` constraints in the sense `PRINTERS_COPY.md` §1 defines, and neither is a
score to raise. If a revision improves the Incunabula Score while pushing a chapter's
emotional arc flatter, that is a regression wearing a pass, and the strengths-to-preserve list
is the thing that should catch it.

## Escalation

Escalate to the orchestrator — do not run a fourth iteration — when:

- The floor has not moved after three iterations.
- The weakness is **structural** (arc, chapter order, repeated thesis) — that is a Phase 2 problem;
  return to `forme`.
- **Oscillation** is reported below 6, above 12, or "highly irregular" — macro-structural, not
  editor-fixable.
- The fix cannot be made without violating a recorded canon fact or a content boundary.
- The Evaluator disagrees with itself across iterations by more than 1.0 on the same dimension.

## Output

```markdown
# Proof Pull: Chapter [N]

**Positioning:** [commercial / literary / ...] — threshold [x.x]
**Prose gate:** PASS / FAIL ([scanner output], control run [result])
**Passing Reader:** would keep reading / would not — [override applied: yes/no]

| Iteration | Weakness (taxonomy) | Fix dispatched | Floor before | Floor after | Delta |
|---|---|---|---|---|---|
| 1 | prose | corrector | 6.8 | 7.2 | +0.4 |
| 2 | connective | corrector | 7.2 | 7.6 | +0.4 |

**Verdict:** PASS / ESCALATE
**Strengths preserved:** [top 3, with evidence]
**Escalation reason:** [if any]
```

If a whole-book check fired and a revision touched the chapter it concerns, add one line naming
the constraint it was given and whether it held:

```
**Book-level constraints honoured:** arc A1 (floor 0.45) — held; surplus S1 spread — improved 0.18 to 0.31
```

Record `chapters_passed` or `chapters_escalated` in the state file under `proof_pull`, and append
the gate evidence — the command, its exit status, and the control run — so the gate can be re-checked
by anyone with a terminal.
