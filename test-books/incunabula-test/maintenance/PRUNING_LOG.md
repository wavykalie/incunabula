# Pruning Log

Append-only. It records **restraint as well as removal**: decisions NOT to prune, NOT
to archive, and NOT to overrule a source are entries. A log that lists only deletions
cannot show that anything was protected.

Format: `date — target — action — replacement — reason — authority`

---

- **2026-09-25 — `CANON_LEDGER.yaml` (all facts F-001…F-007) — KEPT as `inference`, not promoted to canon — no replacement —** These are intake hypotheses, not settled facts. Promoting an inference to canon is the exact failure mode the prior validation run recorded (Book 2 `CONF-011`). They stay labelled. — authority: maintenance protocol
- **2026-09-25 — `ASSUMPTIONS.md` A-16 (narrator person) — KEPT OPEN, not decided —** Raised as `CONF-001` in the ledger. The pipeline does not get to choose the narrator's grammatical person. — authority: safety boundary, stop-and-ask
- **2026-09-25 — repository `README.md` — CREATED —** System documentation only, by user direction. No test-run content. — authority: user_decision
- **2026-09-25 — `_archive/validation-series-meta/tools/` — COPIED into `incunabula-test/tools/`, original retained —** The prose gate needs a scanner and a control runner in the project. The archive keeps the canonical copy; nothing was moved or deleted. — authority: pipeline requirement
- **2026-09-25 — `tools/deslop-check.sh` caps — NOT LOOSENED — no replacement —** Six chapters failed the D2 cap on first pass. Every failure was fixed by rewriting the clause and by writing genuinely missing material. No threshold was moved. This is an entry because the decision *not* to act is the point. — authority: prose-gate contract
- **2026-09-25 — `evaluations/revision-plan.md` (R-001…R-008) — RETAINED, tickets left OPEN —** The revision plan was produced and not executed. The tickets are the evidence that the defects were found; executing none of them does not license deleting them. — authority: maintenance protocol §7
- **2026-09-25 — `CONF-001` (narrator person) — KEPT OPEN, not decided —** The pipeline does not get to choose the narrator's grammatical person. The third-person manuscript stands as a proposal, not a resolution. — authority: safety boundary, stop-and-ask
- **2026-09-25 — Chapter prose, three arithmetic errors (CONT-101/102/201) — CORRECTED, superseded wording recorded here —** "at eighty" → "at eighty-one" (ch.9); "sixty-nine" / "forty-three years" → "seventy-one" / "forty-four years" (ch.10); "at fifty-two" → "at fifty-one" (ch.8). The superseded values are preserved in this entry rather than only in git-less history. — authority: Phase 5.6 collation
- **2026-09-25 — `dist/*.epub` and `manuscript/full-manuscript.md` — EXCLUDED from the document registry by policy, not by omission —** `dist/` is build output and `manuscript/` is governed by the continuity audits; both are excluded in the checker's own rules. Recorded here so the exclusion is a decision rather than an oversight. — authority: document policy §2

- **2026-10-13 — `tools/check-drift.py`, `tools/check-uniformity.py`, `tools/deslop-check.sh`, `tools/validate-controls.sh`, `tools/calibration/extract.py`, `tools/calibration/measure.py` — QUARANTINED to `_archive/tools/` (relative paths kept; nothing deleted) — replaced by the frozen instruments at `tools/prose/` —** These are copies of the gate toolchain that have gone stale: `tools/check-uniformity.py` fails U1 at 30% where the frozen copy fails at 22%, so any verdict from it is unattributable to one known instrument. `tools/preflight.sh` row 6 flags book-carried instrument copies and names quarantine as the fix; the author directed it ("Quarantine the stale gate copies under test-books/incunabula-test/tools/ so preflight goes green", 2026-10-13). The canonical archived copy at `_archive/validation-series-meta/tools/` (see the 2026-09-25 entry) is untouched. — authority: author direction
- **2026-10-13 — `tools/build-epub.py`, `tools/build-omnibus-epub.py`, `tools/check-docs.py`, `tools/check-stale-status.sh`, `tools/check-structure-drift.sh`, `tools/run-checks.sh`, `tools/calibration/` data — KEPT in place — no replacement —** Not copies of anything in `tools/` or `tools/prose/`: this book's own apparatus, outside the stale-copy rule. The archive does not take what it was not asked for. Recorded because restraint is an entry. — authority: maintenance protocol
