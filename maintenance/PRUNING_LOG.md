# PRUNING LOG

**Append-only. This file is the record of what was pruned, archived, or deliberately left
alone — and the "left alone" half is the point.** A log that only ever lists deletions can
never demonstrate that anything was protected.

`tools/prune-stale.py` writes here when it repairs a standing claim in place: the old
wording is preserved verbatim, with the date and the reason, so a corrected sentence can be
told apart from a sentence that was always true. Dated history — a claim inside an ERRATA
entry, a freeze entry, a session record — is never edited and never logged here: it is
reported for a ruling instead, because a record of what was true then is history and not
drift.

The format, in the maintenance protocol's §7 shape:

```
### YYYY-MM-DD — what changed, and why
- **file:**       which record
- **was:**        the old wording, verbatim
- **now:**        the new wording
- **cause:**      what moved the program
- **authority:**  the rule that permits the repair
```

---

### 2026-11-14 — merged `demo-books/` into `test-books/`

- **file:**       `demo-books/` (the whole tree), `.gitignore`, `README.md`, `PROGRAM_MAP.md`,
                  `release-preview.py`, `tools/prose/ductus-fit.py`, `tools/audio/CLONE_LOCK.md`,
                  `BOOKS.yaml`
- **was:**        two book workspaces. `demo-books/` held `demo-magician`, `marrow-light` and
                  `muzzle-and-marrow` as byte-identical copies of the `test-books/` books, plus
                  the only copies of `the-emptying` and `under-three-coats`; `demo-books/` was
                  also the only place with `muzzle-and-marrow/audiobook/` and `maintenance/WAIVERS.md`.
                  `check-registry.py` scans `test-books/` only, so anything that existed solely in
                  `demo-books/` was invisible to every tool in the repository.
- **now:**        one tree. The three duplicates were verified identical before the copy was
                  removed (`diff -rq`, no differing file, `test-books/` a strict superset); the
                  union was moved, not copied: `audiobook/`, `WAIVERS.md`, `the-emptying/`,
                  `under-three-coats/`. The five demo books are now registered in `BOOKS.yaml` as
                  `status: fixture`, because merging them into the scanned tree without registering
                  them would have turned two invisible books into two new registry failures.
- **cause:**      the author, 2026-11-14: "we should merge test books and demo books, they're the
                  same things." The layout was reproducing the defect the registry exists to catch —
                  a book the suite cannot see.
- **authority:**  the maintenance protocol's prune-and-record rule (append-only log; the old state
                  preserved above), and `check-registry.py`'s own premise that a book outside the
                  registry is governed by nothing.

**Left where it is, deliberately.** `tools/audio/CLONE_LOCK_RUN_LOG.md` and
`tools/prose/calibration/CALIBRATION.md` still say `demo-books/...`, because both are dated
records of commands that were run and measurements that were taken while that tree existed.
Rewriting a path inside a dated record would make history match the present, which is the one
thing this project refuses. They are reported here instead, and `test-books/README.md` says so
where a reader will meet it.

### 2026-11-14 — moved the governing light-novel corpus to its registered path

- **file:**       `tools/prose/calibration/corpus/elaina` (moved in), `tools/prose/calibration/LANES.tsv`,
                  `tools/prose/calibration/CORPUS_MAP.md`, `tools/prose/README.md`
- **was:**        `LANES.tsv` pointed `light-novel` at `tools/prose/calibration/corpus/elaina`,
                  which did not exist. The only copy of the 51 files was under
                  `test-books/incunabula-test/tools/calibration/corpus/elaina`, so the lane carried
                  the status `INSTALLED ELSEWHERE`, and CORPUS_MAP.md recorded it as a stray copy.
                  The fit tool's book-carried fallback only resolves a missing path relative to the
                  book being measured, so for any book outside that one test tree
                  `ductus-fit.py --lane light-novel` exited 3 NOT RUN: the lane that derived every
                  cap in `deslop-check.sh` could not be re-measured at all.
- **now:**        the corpus is at its registered path, verified byte-identical before and after the
                  move (51 files, md5 `e41e5e31...` both sides) and still gitignored there
                  (`calibration/.gitignore`). `corpus-report.py` reads it as 48 documents /
                  175,144 words **MATCH**, where before it could only report it missing. The lane's
                  status is `INSTALLED`; Flaw 2 in CORPUS_MAP.md is marked repaired.
- **cause:**      the author, 2026-11-14: move the stray copy so the governing lane can be
                  re-measured. Redundant data filed where the record already said it belonged.
- **authority:**  the maintenance protocol's repair-a-standing-claim rule. Dated evidence is not
                  edited: `CALIBRATION.md` (both the root copy and the book-carried one),
                  `.private/record/GATE_FREEZE.md` and `KNOWN_FINDINGS.md` still describe the corpus
                  as unshipped or absent, because that is what was true when they were written.

**What this does not fix.** Flaw 1 stands untouched: 175,144 words, one author, one translator,
three volumes of one series. The lane is now readable; it is still the reason every cap is a
series' habits with a plausible story attached. And a second, byte-identical copy remains under
`test-books/_archive/validation-series-meta/tools/calibration/corpus/elaina`, deliberately kept:
it ships with the archived `validate-controls.sh` that defaults to that path. 1.1 MB of duplicate
prose, reported and left in place rather than deleted with the tree it belongs to.

### 2026-11-14 — `check-agency.py` counts R1 as two rows; the standing claims follow

- **file:**       `README.md`, `skills/incunabula/SKILL.md`, `tools/prose/README.md`,
                  `GATE_FREEZE.md` (a new dated entry; the previous entry untouched)
- **was:**        "`check-agency.py` is the one with a measurement under its second row";
                  "`check-agency.py` (objects given a mind, and motives stated by absence)";
                  the limits bullet, which described one object row and no measurement of its
                  own.
- **now:**        "under its last row"; "places and objects given a mind, and motives stated
                  by absence"; and the limits bullet carries the split and the measurement that
                  forced it — fifteen R1 hits in 517,822 words, fifteen place, zero object.
- **cause:**      R1 was answering an object question with place nouns. Every one of the fifteen
                  hits was a setting — hall, room, town, street, ceiling, office, House — so the
                  row's name was wrong about its own output, and no reader could have seen that
                  from a single count.
- **authority:**  the author, 2026-11-14: "Keep going with splitting by noun class." Standing
                  claims only. The freeze entry that introduced the row is dated history and was
                  not edited; the split is recorded in its own entry beneath it.

### 2026-11-14 — the agency row's own numbers were measured with a retyped instrument

- **file:**       `tools/prose/check-agency.py`, `tools/run-gates.sh`, `tools/prose/README.md`,
                  `README.md`, `tools/prose/calibration/CALIBRATION.md` (new section),
                  `GATE_FREEZE.md` (a correction entry; both dated entries untouched)
- **was:**        "23 hits in 4,531,815 words = 0.005/1k"; "the worst human document reads
                  0.37/1k … the 1.5x convention puts the cap at ~0.55/1k, and every manuscript
                  measured passes it"; "0.00/1k in all six human corpora" for R2; "of 23 hits in
                  the human corpora, about a third are genuine" — and the same four numbers
                  repeated in the runner's comment, two READMEs and the freeze entry.
- **now:**        11 R1 hits (0.0024/1k; 6 place, 5 object); worst published document 0.21/1k,
                  so a 1.5x cap lands at ~0.32/1k — which the project book's deliberate chapter
                  14 fails at 0.74/1k; R2 at 2 hits, not zero; precision 5 of 11 by reading,
                  with all five misses named. Full table in CALIBRATION.md.
- **cause:**      the numbers came from a scratch copy of the patterns taken before the tool was
                  tightened, so the shipped instrument could not reproduce them. One instrument
                  measured, another ships — the error Freeze 23 records in the other direction.
- **authority:**  the maintenance protocol's repair-a-standing-claim rule, and the author's
                  2026-11-14 instruction to give the split rows a human baseline instead of a
                  ratio measured only on this tree. Dated freeze entries were not edited; the
                  correction is its own entry beneath them.
