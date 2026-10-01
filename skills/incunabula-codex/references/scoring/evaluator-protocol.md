# Evaluator protocol

Use this for the fine-press pass and the final score. Its purpose is to reduce
self-grading, threshold anchoring, and praise that cites nothing.

## Blind inputs

An evaluator receives only the manuscript or the declared sample, the stable foundation and
architecture facts needed for continuity, the rubric, and the market position where the
market dimension is being scored.

It does not receive writer self-reports, revision rationale, any desired pass threshold,
earlier numeric scores, or another evaluator's verdict.

## Role boundaries

- The writer drafts and never issues the final score.
- The evaluator diagnoses and scores and never edits the manuscript.
- The revision editor receives evidence-backed tickets and edits only what was assigned.
- A fresh evaluator verifies revisions without seeing earlier numeric scores.
- The orchestrator applies calibration and thresholds only after the reports are frozen.

## Independence grades

- **A** — three or more fresh evaluator contexts, with at least two model families where available.
- **B** — three or more fresh evaluator contexts within one model family.
- **C** — evaluation happened inside the writer's or revision editor's context, or earlier scores leaked in.

Grade C is diagnostic only. Never describe it as independent validation.

## Required output

Every evaluator reports a score per dimension; the strongest and weakest passages with their
locations; the evidence behind any score above 8.0; the blocking defect; the smallest viable
intervention; its confidence; its coverage; and any explicit conflicts in the evidence.

## Aggregation and integrity

1. Freeze the raw reports before calibration.
2. Take the median per dimension, and the lowest median as the floor.
3. Keep disagreement visible: a spread of 1.5 or more requires another blind evaluator or a low-confidence flag.
4. Thresholds enter only once calibration is done.
5. Mark an evaluation degraded if the evaluator edited the text, saw the target first, gave no textual evidence, claimed full coverage from excerpts, or treated missing output as a pass.

A degraded evaluation can still produce revision tickets, but it cannot approve publication
readiness.
