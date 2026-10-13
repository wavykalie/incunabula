# PRUNING LOG — The Origin Point

**Append-only.** Never edit or delete an entry. Corrections are new entries that
supersede an earlier ID, with the earlier entry kept and marked superseded.

Format: date · action · original path · archive path · replacement · reason

---

## 2026-09-27 — project created

- **action:** create
- **original path:** —
- **archive path:** —
- **replacement:** —
- **reason:** NEW project, book 2 of the 7-genre proof suite. Narrative nonfiction
  (*Sons of Heaven, Students of Dust*) completed first; this is the first fiction
  book, and the first observation of the fiction branch of the calibration.

- **action:** create (scaffold)
- **paths:** `PROJECT_STATE.yaml`, `premise.md`, `outline.md`, `CANON_LEDGER.yaml`,
  `ASSUMPTIONS.md`, `RUN_REPORT.md`, `maintenance/`, `research/`,
  `manuscript/chapters/`, `evaluations/`, `continuity/`, `feedback/`,
  `voice-bank/`, `delivery/`
- **reason:** Directory structure per the pipeline contract. `manuscript/chapters/`
  created EMPTY and stays empty until Phase 3. A gate that reads nothing proves
  nothing — an empty directory must report as NOT RUN, never as a pass.

## 2026-09-27 — STATE.yaml deliberately NOT created

- **action:** withhold
- **reason:** The pipeline contract allows either `STATE.yaml` or `PROJECT_STATE.yaml`
  and says to preserve both when present. `check-length.py` reads **only**
  `PROJECT_STATE.yaml` (hardcoded at line ~140 of that script), so the length contract
  lives there. Creating a second `STATE.yaml` would introduce a second source of truth
  for a number that decides whether the book is a failure — and `check-length.py`
  would not read it. One state file, the one the gate actually reads.

## 2026-09-27 — length contract declared before any prose

- **action:** declare
- **path:** `PROJECT_STATE.yaml` → `target_floor_words: 80000` / `target_ceiling_words: 95000`
- **reason:** Book 1 shipped at 56% of target and nothing caught it, because
  `intake-schema.md` defaulted `target_range_words` to `[0, 0]` and five skills push
  length variation with no floor beneath them. That schema/template hole is fixed in
  the pipeline; this book declares the range at Phase 0 instead.
- **verified:** `check-length.declared_target()` returns `(80000, 95000, 'PROJECT_STATE.yaml')`
  — enforced, not the single-figure advisory path. Checked with a real parser before
  any prose existed.

## 2026-09-27 — chapter-length variance engineered, not discovered

- **action:** plan
- **path:** `outline.md`
- **reason:** `U1` is **advisory** on nonfiction and **enforced** on fiction. Book 1
  chased variance during Phase 3 and landed at CV 24.0% against a planned 34.8%.
  The 30 chapter targets here were computed to CV **35.7%** (published fiction band
  33.4–45.1%) before a single chapter was drafted. First draft set scored CV 21.7%,
  which would have FAILED — the plan was widened and re-verified. Recorded because
  the first attempt failing is the evidence that the gate is load-bearing here.
