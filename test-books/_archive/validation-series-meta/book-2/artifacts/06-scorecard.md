# Phase 6 — Final Score (Book 2)

**Run:** 2026-09-24
**Method:** the seven Genesis Score dimensions, scored against the drafted manuscript (15,148 words, seven
chapters) and the evidence in `../continuity/manuscript-audit.md` and `../continuity/adversarial-audit.md`.

**The honesty note, and it is the same one as Book 1's, only worse.** These numbers are assigned by the
same agent that drafted the prose — and Book 2 was drafted *immediately after* it corrected its own canon,
so the drafting and the scoring share a single context. That is the least independent evidence in the
project. Treat the reasoning as the content and the number as a summary of it.

Scores are **not** calibrated lens scores. That is Phase 5's job, and **Phase 5 has still never been
activated, for either book**, because its activation condition — a quality target set by the author — has
never been met. See `../continuity/adversarial-audit.md` for the case for pointing it here.

---

## Gate compliance

| Gate | Requirement | State |
|---|---|---|
| **Maintenance** | No unrecorded conflicts; primary state file parses | **MET** — `PROJECT_STATE.yaml`, `CANON_LEDGER.yaml` and `ENTITY_STATE.yaml` all parse under `js-yaml`; open conflicts **0** (resolved: `PROBE-001`, `CONF-011`) |
| **Prose** | Green across every chapter before a score is reported | **MET** — 7/7 PASS; warnings recorded, no failures. Controls re-run and green: *ALL CONTROLS PASS* |
| **Continuity** | Phase 2.8 and Phase 5.6 both run | **MET** — outline audit cleared with 3 CRITICALs applied; manuscript audit cleared with **1 CRITICAL found in prose that had already passed the gate**, fixed and re-gated |

**No score would have been reportable with any gate red.** Book 1 shipped with Phase 5.6 unrun; Book 2 did
not, and it is the only reason the woman-at-the-turn defect was caught.

---

## Dimension scores

| # | Dimension | Score | Evidence |
|---|---|---|---|
| 1 | **Originality** | **7.5** | The engine is a clean structural inversion of Book 1 and the *inversion is load-bearing*, not cosmetic: the horror is not that you cannot leave, it is that you can leave and the bill goes to people who never asked you for anything. Docked because the frame is a familiar one — endless necessary labour as a dystopia is well-trodden, and Book 2's mechanism (a work that cannot be finished and needs everyone) is much closer to standard SF than Book 1's hospitality monster was to standard horror. The freshness is in the cost-allocation and in the workers' *contentment*, not in the premise. |
| 2 | **Theme** | **8.0** | *Is being needed the same as being wanted?* is never stated by anyone and is never answered; the narrator spends the book believing the answer is yes and the structure contradicts her without correcting her. Docked for one dilution the first book did not have: ch.5 has Merope **state the pattern out loud** (*"Everyone here came because somebody stopped wanting them"*). Book 1 assembled its equivalent and never said it. Here the statement is immediately put to work as a character beat, so it is setup rather than explanation, but it is still the narrator handing the reader a conclusion. |
| 3 | **Characters** | **7.5** | Merope is stronger here than in Book 1, because the delta gives her something to *do* all book: the testing is her first sustained active behaviour in the series, it is staged rather than announced, and it is paid off in a single wordless beat. Achird is the same excellent construction and remains closed by design. Docked because the cast is still two and the population is a condition: four workers get a face and the rest are hands. Book 1's beings were *allowed* to be one mood; Book 2's workers are supposed to be many people who each chose the same thing, and the manuscript does not fully earn that. |
| 4 | **Prose / voice** | **8.0** | The voice holds across seven chapters and five structural modes (catalogue, chorus, fragmented, reverse, stream) with no drift, and the stream chapter is the best-controlled piece of writing in the series. Docked for a genuine tic this time rather than a nitpick: the hedge-announcement — *"I want to be exact"*, *"I want to be careful"*, *"I want that on the record"* — is the narrator's signature move and Book 2 leans on it harder than Book 1 did, because the delta required more self-examination. It reads as a tic in three chapters and as voice in the other four. |
| 5 | **Pacing / coherence** | **7.0** | The lowest score, and it is structural rather than accidental. The tension map is a plateau — same discomfort from ch.1 to ch.6 — which is the engine working as designed and still produces a flat middle for a plot-motivated reader. Ch.4 holds the only external event before ch.6. Coherence, by contrast, is the highest of any dimension: one CRITICAL found and fixed, no surviving contradiction known. |
| 6 | **Emotion** | **7.0** | Two things land: the ch.6 mirror (she waits for her to finish, as Merope once did to her) and *"They were poorer"*, which is doing all the work of differentiating this ending from Book 1's. Docked twice. The middle is affect-flat by design. And the ending resolves on **two words** — the author struck the pipeline's prohibition on directness (`CONF-011`) and the prose still stops at the minimum, which may be right and is indistinguishable from obeying the rule that was struck. Escalated in `../continuity/adversarial-audit.md` item 1 and listed as an author decision below. |
| 7 | **Worldbuilding** | **7.5** | Better served than Book 1, which was docked to 7.0 for being thin by rule. Book 2 has a society: a work with a shape, rows, a turn, a join, a place where tools are kept, an intake process, and a population with a stated relationship to being needed. All of it survives the naming rule and nothing is named. Docked because the work itself is deliberately undescribed, so the reader gets the *social* texture and no object to hold, and because the mechanics (`R-013`–`R-021`) are pipeline-proposed rather than author-signed. |

**Composite floor: 7.5** (mean of the seven). **Lowest dimension: pacing/coherence, 7.0, tied with emotion.**
Book 1 scored **7.7**.

**The comparison is not flattering and should not be read as one.** Book 2 is a harder book to write than
Book 1 was: it had a decided engine, a decided location, an author-corrected delta and a series contract to
hold, and it was written in one session by an agent operating under a rule it had just been caught
breaking. Book 1 scored half a point higher against a much looser brief.

---

## Commercial viability

Scored for what this is: a ~15.1k-word **second** installment, unnamed and untitled, from an unknown
author, in the same thin cross-genre niche.

| Metric | Score | Reasoning |
|---|---|---|
| **CVI — launch** | **4.0** | Lower than Book 1's 4.5, and for a structural reason rather than a quality one. Book 2 is an **inversion book**: its whole effect depends on the reader having the first one, which makes it a worse entry point and makes a launch beyond the existing readership harder. Its own first third is also colder than Book 1's first third — Book 1 opened on wonder, Book 2 opens on nobody looking up. |
| **CVI — legacy** | **6.5** | Level with Book 1, by a different route. Book 1 travelled on retroactive verification. Book 2 travels on **the pair**: read together, the two engines are the argument, and the second book changes what the first one was. That is a real word-of-mouth property in a niche and it is the reason the two-book shape is a better asset than either volume. |
| **Primary engagement** | fascination | The mechanism, not the narrator — a reversal of Book 1, where the voice carried it |
| **Secondary engagement** | empathy | Merope's testing is the first thing she has ever *done*; readers who disliked her in Book 1 have a reason to come back |
| **Tertiary engagement** | intellectual | The unanswered question, now doubled |
| **Commercial pacing** | 4.5 | Flatter than Book 1's 5.0 by design |
| **Tomorrow-test anchors** | **3** | *"Nobody looked up."* · *"We'll be poorer."* · *"I know."* One fewer than Book 1, and the first is the strongest opening line in the series. |
| **Casual reader verdict** | **finishes** | Predicted, **not simulated** — Book 1's personas were run; Book 2's were inherited (`ASSUMPTIONS.md → A-5`) and not re-run, which is a gap and is recorded as one |
| **Shareability — quote** | **4/5** | The short lines are as short as Book 1's |
| **Shareability — plot** | **2/5** | Spoilable in one sentence and there is nothing to spoil: no twist, no reversal of fact |
| **Shareability — emotional** | **3/5** | Quiet and mutual again, and slightly quieter than Book 1 |

### Concept pitch (Book 2)

> Two girls land on a world where everyone has a job and the job is the whole point. Nobody is kept.
> Everybody is needed. Merope, who has never been useful to anybody in her life, is handed a tool and
> told it needs holding — and the work will need it held forever.

### Human closeness

**High, with one caveat.** The voice is unmistakably human and the cruel scene in ch.6 is the least
performed writing in the series. The caveat is the tic in dimension 4: the hedge-announcement is the one
place a reader can feel the writer checking her own work.

---

## Verdict, and the next action

**Gate verdict: PASSES on quality at 7.5, with pacing and emotion as the weak lenses. Launch viability
lower than Book 1's.** The series is now a two-book asset whose value is greater than either volume.

**Next action, in order:**

1. **One author decision is genuinely owed, and it is not the population.** The population's mechanics
   (`R-013`–`R-021`) are the pipeline's design and want sign-off, but the more consequential question is
   `../continuity/adversarial-audit.md` **item 1**: the corrected rule did not reach the prose. Ch.7
   resolves on two words. If striking the prohibition meant *more* should be said, that is a revision, and
   it is the only change likely to move both **emotion** and **theme**.
2. **Phase 5 still has not run, for either book.** If a target is set, point it at **pacing/coherence
   (7.0)** for Book 2 and **structure** for Book 1 — the two books' weak lenses are different, which is
   itself information.
3. **The reader personas were inherited and not re-run.** Book 1's four personas were carried forward as
   Book 2's starting audience (`A-5`) and the horror-first persona has *less* to hold in this book. Running
   them is cheap and is the single highest-value missing piece of evidence.
4. **The commercial questions are unchanged and unanswered.** No comps have ever been approved for this
   series, and Book 1's market map was desk analysis only. Book 2's is too.
