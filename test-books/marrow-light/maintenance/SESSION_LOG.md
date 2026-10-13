# SESSION LOG — MARROW LIGHT

Append-only. One entry per working session, covering decisions, changed files, facts
merged, conflicts, and the next step. Per
`incunabula-codex/references/maintenance-protocol.md`.

---

## 2026-09-29 — Architecture complete, manuscript not started

**Phase:** 2 → 3. Foundation and architecture written. **Zero prose exists.**

**Decisions made:**

1. **Book title left unfixed.** `Marrow Light` is a working title carried from the
   directory name, and `premise.md` records that the directory name does not describe the
   book. Nothing is named until the manuscript is drafted. Chapter titles in the outline
   are placeholders for structure, not title decisions.
2. **The Vell named.** The cave is given a name in the story engine so that it is a place
   rather than a mood. The system is the clock of the book and a clock needs a name.
3. **WR-003 kept load-bearing.** The collapse was water and is knowable from the start.
   The book does not hide behind a last-minute doubt, and **nobody in it ever says *maybe
   it wasn't the water*.** The doubt exists in 1994, in a gauge reading, and it was wrong
   then too. This is the design decision the whole Block IV is built to pay off.
4. **The romance is carried by distance, not by feeling.** Fifty metres of wool between
   them for most of the book. The film's subject and the person filming it are physically
   separated by the length of a rope. This is the answer to the two-hander problem and it
   is the reason the premise's engine is a relationship rather than a question.
5. **No supernatural reading.** The Vell is limestone and water and gravity. The
   supernatural reading is available to Ottoline for about two chapters because she is
   twenty-two and because her mother did something stranger, and it is *wrong*, and the
   book does not pretend otherwise for longer than it takes to kill it.
6. **Nobody dies in the last third.** This is a romance. The tension is structural, not
   fatal, and Block V's threat is a known cycle read off a brass plate by a competent
   person.
7. **Ines is not the prize for having suffered.** The romance is a second problem, not a
   reward. `artifacts/04-theme.md` states this explicitly so a later revision pass cannot
   reinterpret the ending as a consolation.
8. **The length floor was declared at the premise stage**, before drafting, rather than
   after. This is the difference between this book and `muzzle-and-marrow`, where the floor
   was declared late and missed by 5,314 words and recorded as a failure. A number written
   down before anyone can see the result is a number you can honour.

**Artifacts written this session:**

- `artifacts/02-story-engine.md` — world, the Vell, the two engines, escalation, four turns
- `artifacts/03-characters.md` — six cast + two off-page figures, wound/want/need/lie
- `artifacts/04-theme.md` — theme as a question, four restatements, five subthemes, five
  physical symbols
- `artifacts/05-outline.md` — 45 chapters, 10 structural approaches, no consecutive
  repeats, 4 block turns, tension map, 8 carried threads
- `artifacts/06-emotional-curve.md` — five blocks, four valleys, the seven beats that hit
  hardest
- `artifacts/07-opening-strategy.md` — four first lines, one chosen with reasons, where
  ch 1 ends
- `ENTITY_STATE.yaml` — BUILD. 8 figures, 4 locations, 6 objects, 3 world rules, 7
  relationships, 8 carried threads
- `PROJECT_STATE.yaml` — length contract, phase history, gate block present-but-not-run
- `maintenance/PRUNING_LOG.md` — first entry, recording a decision NOT to prune

**Facts merged into canon (no duplicates minted):**

- CHR-001, CHR-002 … CHR-006, OFF-001, OFF-002 — all from `CANON_LEDGER.yaml`, extended
  with the `want`/`need`/`lie`/`voice` fields the foundation phase requires. **No second ID
  was minted for a rephrased fact**, per the maintenance protocol.
- WR-001, WR-002, WR-003 — carried verbatim from the canon ledger. `WR-003` gained an
  `enforced_in` chapter list, which is new information about *where* it is load-bearing
  and not a new rule.

**Conflicts opened:**

None. The two planning-time name collisions (`Wren`, `Delphine`) were resolved before this
session, in `CANON_LEDGER.yaml`, with the reasons recorded on the renamed characters.

**Next step:** draft Chapter 1. Then run the prose gate against the file, per the drafting
prompt's per-chapter requirement. **No per-chapter length target of any kind is to be
written before, during, or after a chapter.**

---

## 2026-09-29 (earlier) — Premise, canon ledger, prediction

Recorded for completeness; the full entries are in the commits `9d167ea` and `23950dc`.

- `premise.md` written and scoped against `check-premise-distinct.py` **before any prose**,
  per the Freeze 5 order. All three axes OK, exit 0.
- `CANON_LEDGER.yaml` written with the two-declaration cast pattern after probing the
  frozen name gate. **Two collisions caught before drafting**: `Wren` (in
  `the-origin-point` archived premise 1) and `Delphine` (in `the-origin-point` cast plus
  two chapters, and in `demo-magician`). Renamed to Ottoline and Fabiola, reasons recorded
  on the characters. `NAME CHECK OK` after.
- `PREDICTION.md` written before chapter 1. **P3 falsified in advance** against six
  published volumes, 303 chapters, median r = 0.00. P1 and P2 open and to be measured at
  chapters 11–45.
- `paragraph_convention: commercial-dialogue` declared → **U4 ENFORCED**, the first book
  in the project to opt in, declared before drafting rather than after a failure.

---

## 2026-09-29/30 — Manuscript complete. 38 chapters, 78,070 words.

**Phase:** 3 → 4. All 45 rows drafted. All six gates run on the finished manuscript.

### Gate results, as they came

| gate | exit | result |
|---|---|---|
| deslop | 0 | PASS with warnings |
| uniformity | 0 | **PASS** — U1 CV 26.2%, U4 65% (enforced) |
| drift | 0 | PASS — voice-step 0.65 against a 1.40 line |
| length | 1 | **FAIL** — 78,070 against a 100,000 floor |
| names | 0 | PASS |
| premise | 0 | PASS |

**The length failure is not being fixed and the floor is not being moved.** 21,930 words
short, declared in advance in September, missed. `PROJECT_STATE.yaml` carries the three real
options and deliberately withholds a recommendation, because this is the author's contract.
The specific temptation — that U1 wants a longer book and L1 requires one, so expanding the
short chapters satisfies both — is named in the file as the padding failure, because it is
the failure `DRAFTING_FRAMEWORK.md` exists to prevent.

### The two results worth keeping

**U1 passed without being consulted.** CV went 10.9% (ch 19) → 21.3% (ch 26) → 26.3% (ch 28)
→ 26.2% (final) purely as the joined chapters ran long. `check-uniformity.py` was run per
chapter throughout drafting because the drafting prompt requires it, and it was run to read
the output, never to steer to it. The move from fail to pass is a consequence of Amendment 1
and of the author's instruction that long chapters were fine.

**This is the book's real finding and it is about scale, not method.** The pilot scored
12.1% over 10 chapters on the same method with the same rules. This book scored 26.2% over
38 with a 2.77× range. **The difference is chapter count, not technique** — 38 chapters is
enough shape for a distribution to be a distribution. That is a hypothesis about the
relationship between book length and U1, it is stated here as a hypothesis, and it is
untested.

### P1 / P2 / P3, recorded unedited in `PREDICTION.md`

- **P1 HOLDS** — 24 of 28 chapters (86%) above the pilot's 25.0. Comfortably a majority.
- **P2 HOLDS, weakly** — 0.84 words of difference against a 3-word tolerance, **on a
  three-chapter window where ten were predicted**, because the book finished at 38 chapters
  and the window could not be filled. Marked as the weakest result in the file.
- **P3 already falsified in advance.** Unchanged.

The whole climb from ch 11 to ch 38 is **1.18 words** (28.34 → 28.93 → 29.52). The pilot's
16.4 → 25.0 climb does not recur. `PREDICTION.md` explicitly declines to convert this into a
claim about how to write a book.

### Chapter count: 38, not 41

Four joins per Amendment 1 gave 41. Three further adjacent pairs turned out to be one scene
each once drafted and were not split. The count was never a target. Recorded in the outline
and in `PROJECT_STATE.yaml` so a later session does not read 38 as a shortfall against 41.

### Gates that fired during drafting and were fixed in the PROSE

- **A1b** (harness/leverage, 1 per 2,000 words) — fired on ch 1. A vocabulary collision
  between a slop rule and a book set in caves. The word is *waist belt*, the first line was
  reworked around it, and the frozen gate was not touched. Reasoning recorded in
  `artifacts/07-opening-strategy.md` under Amendment.
- **A8** (false suspense) — fired twice on ch 7 and ch 12, both times on phrasing doing honest
  work. Both reworked.
- **U6 signature frames** — fired on `I want to be X` as a disarming preamble, four times in
  five chapters, which is Ottoline's actual verbal move. The construction was varied three
  times and the voice kept.

### Not run, and recorded as not run

- **Blind Sort** — the foundation predicted a two-hander would be the hardest shape to pass
  it. Not run. This is the most significant untested claim about the book.
- **check-arc.py, check-recoverable.py, check-surplus.py, check-comps.py, check-errata.py** —
  not run; their applicability to a novel was not established.
- **Phase 4 devil's audit** — not run. Deliberately deferred: the length failure should be
  resolved first, because a revision pass on a book 22% under its floor is the exact
  condition that produces padding.

### Next step

Resolve the length contract. Everything else waits on it.
