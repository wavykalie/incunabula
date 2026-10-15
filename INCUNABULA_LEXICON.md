# Incunabula Lexicon

This is the dictionary. Every unusual word in this system is defined here in plain
English. If a term is not listed here, plain craft language is fine.

Why there are unusual words at all: an *incunabulum* is a book printed before 1501, in
the first fifty years of the press, and the system takes its labels from the letterpress
shop that made those books — the platen, the quoin, the forme, the case, the pull, the
colophon. The names are just labels for specific tools and steps. When one gets in your
way, use the plain meaning given here instead.

This file has two halves: **the machinery words** (gate, freeze, corpus — the words that
make the check documentation hard to read) and **the print-shop names** (the creative
steps and scores).

---

## The machinery words

These are the technical words used in `GATE_FREEZE.md`, `tools/prose/README.md`, and the
gate output. They are ordinary words to a software person and jargon to everyone else.

| Word | What it means |
|---|---|
| **gate** | An automatic check that reads your book and can fail it. A gate passes, warns, or fails; the pipeline will not move past a failed gate. |
| **freeze** | A locked snapshot of the checking tools. When the gates were found trustworthy, their files were fingerprinted and the fingerprints recorded in `GATE_FREEZE.md`. From then on, any change to a gate must be written down there with a date and a reason. The point is simple: every result in this system can be traced back to the exact tools that produced it. A book keeps the freeze it was written under. |
| **manifest** | The list of fingerprinted files at the top of `GATE_FREEZE.md`. It is the "these are the locked tools" table. |
| **hash (sha256)** | A file's fingerprint. Change one character anywhere in the file and the hash changes completely, so two matching hashes prove two files are byte-identical. |
| **verify-freeze.sh** | The one command that compares today's tools against their recorded fingerprints. `FREEZE HOLDS` means the tools are untouched. `CHANGED` means someone edited a gate, and results from before that edit no longer apply. |
| **corpus** | The collection of published books the gates' limits were measured against. It is deliberately not shipped here (it is copyrighted work), so you supply your own to fully re-check the limits. |
| **calibration** | The measurement work behind the limits: read published prose, measure it, and set each limit where published prose passes comfortably. The record of it is `tools/prose/calibration/CALIBRATION.md`. |
| **threshold / cap / limit** | The number a gate enforces — for example, "no more than 3 antithesis formulas per 2,000 words". Every threshold here was measured from published prose, never picked by feel. |
| **row** (U1, D1, A1, N1, L1, …) | One named measurement in a gate's output. Row IDs make results precise: "the book failed U6" means "chapters kept closing with the same signature move too often". |
| **FAIL / warn / advisory / report-only** | The severity ladder. **FAIL** blocks the book. **Warn** flags something to look at. **Advisory** and **report-only** rows print findings but can never fail anything — usually because no corpus exists yet to calibrate them honestly. |
| **control** | A test sample with a known answer, used to test the checkers themselves. A *positive control* is bad prose that must fail; a *negative control* is clean prose that must pass. A checker that cannot fail its positive control is broken. |
| **validate-controls.sh** | The self-test suite for the checkers. It runs every control against every tool and reports which behaved. Exit 0 means all pass. Exit 2 means some controls could not run (usually: no corpus installed) — and "not run" never counts as "passed". |
| **exit code** | The number a command returns to the shell: `0` passed, `1` failed, `2` not run, `3`/`4` special states such as "nothing to check against" or "book is still being drafted". Trust the number as well as the words on screen. |
| **CV (coefficient of variation)** | How much a set of numbers varies, as a percentage of their average. A chapter-length CV under 22% means the chapters are suspiciously all the same length. |
| **provenance** | The recorded origin of a fact or number — where it came from and when. Facts in the canon ledger carry it, so a contradiction can be settled instead of guessed at. |
| **errata** | The append-only ledger of mistakes found in the *measurements themselves* — a wrong limit, a buggy rule — each with evidence, a date, and what was done about it. |
| **attribution** | Being able to say exactly which version of which tool produced a result. The whole freeze protocol exists to keep results attributable. |
| **mode (`fiction` / `nonfiction`)** | What a book declares itself to be in its `PROJECT_STATE.yaml`. Some checks read the two differently (paragraph shape, filler phrases, cast names). |
| **make-ready** | The print-shop word for the setup work before a run — in this system, the tools and rules that manage the *process* (preflight checks, session logs, self-improvement) rather than measuring the book. |

### Row IDs in plain words

Gate results quote row IDs like `U1` or `N4`. `tools/prose/README.md` points here for the
plain meaning of each; this is that table.

| row | what it measures, in plain words |
|---|---|
| `U1` | Are the chapters suspiciously the same length? (The spread of chapter lengths against each other.) |
| `U2` | Do sentence lengths vary, or does everything sit at one length? |
| `U3` | Does more than a quarter of the book's chapters close on an explanatory coda? |
| `U4` | How many paragraphs are a single line? (A market convention — advisory by default.) |
| `U5` | Are all the paragraphs the same length? |
| `U6` | Does one signature closing move — a distinctive line or construction — keep recurring across chapters? |
| `D1` | Em dashes per 1,000 words (report-only). |
| `D2` | The rule of three: things listed in threes (report-only). |
| `D3` | `-ly` adverb density. |
| `A1` | Does the book's emotional direction ever change? A book that never reverses fails (gates). |
| `A24` / `A25` | How often a chapter uses the explanatory coda or the antithesis formula (`It was not X. It was Y.`), counted per 1,000 words. |
| `F1` | Does any chapter close on an explanatory coda? Never allowed — a position, not a rate. |
| `P1`–`P3` | Repeated sentence openers (anaphora), duplicate sentences, runs of short fragments. |
| `S1`–`S4` | Surplus dialogue — speech that carries no plot (report-only). |
| `N1`–`N4` | The narrative ledger: are the book's declared debts, beat arcs, and scene functions recorded and resolved? |
| `L1` | Did the book deliver the length it declared for itself? |
| `Q1`–`Q4` | Do the numbers in the book agree with each other? (report-only) |

The letters follow the tool: `U` = uniformity, `D` = density rules in the scanner,
`A`/`F`/`P` = per-chapter style rules, `S` = surplus dialogue, `N` = narrative,
`L` = length, `Q` = quantities.

**Two craft words those tables assume you know:**

- **coda** — a closing passage that re-explains the ending ("this is why…"). Fine once;
a book that does it in every chapter gets flagged.
- **anaphora** — the same sentence opening repeated ("She went. She saw. She took.").
Deliberate once, a tic when it repeats.

---

## The print-shop names

### Scoring

| Term | What it means |
|---|---|
| **Incunabula Score** | The book's overall quality score across seven dimensions. |
| **the Platen** | The weakest-link rule behind that score: the overall score is the **lowest** of the seven dimension scores, never an average. Six 9.0s and one 7.0 is a 7.0. (The platen is the flat plate that presses the paper against the type; the weakest impression sets the whole sheet.) |
| **Press Run Index** | The market score — how the book is expected to perform commercially. |
| **First Impression** | The prediction of first-year sales. |
| **Standing Type** | The prediction of long-run (twenty-year) sales. (Type kept *standing* was kept ready for reprints.) |
| **Fine Press Score** | The literary-quality threshold a book must clear. |
| **Fine Press Loop** | The revision loop that lifts a book above that threshold. |
| **Fine Press** | The literary tier itself — the level at which the book counts as genuinely well made. |

### The tests

| Term | What it means |
|---|---|
| **Keepsake Test** | What the reader carries away from the book. (A keepsake is a small memento.) |
| **Shelf Test** | The bookshop browser's verdict, given in three words: BUY / MAYBE / PUT BACK. |
| **Afterimage Test** | What stays with the reader after the last page. |
| **Blind Sort** | The voice-individuation test: hand a reader unlabelled dialogue lines and see whether they can tell who is speaking. (A *sort* is one piece of type.) |

### The passes and phases

| Term | What it means |
|---|---|
| **Devil's Audit** | The adversarial pre-scoring audit: an independent read whose only job is to find the book's faults before it gets scored. (The printer's devil was the apprentice who fetched type — and, legend says, ate the mistakes.) |
| **the Quoin** | The predictability-breaking pass: deliberate noise and disorder injected into a drafted chapter so it stops sounding machine-ordered. (The quoin is the wedge that locks type in place; loosen it and the page falls apart.) |
| **Proof Pull** | The chapter quality loop: pull a proof, score it, fix the single weakest point, score again — at most three rounds. |
| **Composing** | The mechanical cleanup pass: spelling, punctuation, repetition, formatting. No structural or creative changes. (Composing is setting type into words.) |
| **Catchword** | The opening and ending hook work on a chapter: the first lines pull the reader in, the last lines pull them on. (A catchword was printed at the foot of a page to be "caught" by the first line of the next.) |
| **Register** | The dialogue-alignment pass: every character's speech is checked against their voice card. |
| **Case Tracking / Case Update** | The entity ledger (`ENTITY_STATE.yaml`): who and what exists, and what each character knows, kept current as chapters are written. (The type case holds every sort of type.) |
| **Collation** | The continuity audit: checking the manuscript against the outline and the ledger for contradictions. (Collation is comparing copies against each other.) |
| **Forme** | The foundation document (`foundation.md`) — the book's assembled plan: premise, theme, characters, world. Everything else locks into it. (The forme is the locked-up page, ready for the press.) |
| **Readership** | The reader personas — who the book is for. |
| **Voice Matrix** | The per-character voice specification: how each character speaks, including how their voice breaks under pressure. (The matrix is the mould each character is shaped from.) |
| **Ductus** | One authorial voice — the individual character of a writing hand — kept in `ductus/<name>/`. A book may be drafted *under* one: the agent pilots that voice, reading its contract before it writes a line. Its ledger of taste is its own, and voices are held apart the way channels are. (In manuscript studies the ductus is the particular way one scribe's hand forms its letters — the style that belongs to that hand and no other.) |
| **Voice contract** | The ductus document the agent drafts under (`ductus/<name>/ductus.md`): identity, register, refusals, how the voice breaks, and the benchmark lines it is blind-sorted against. A contract nobody has authored is a skeleton, and a run assigned to one stops rather than drafting without it. |
| **Colophon** | The editorial package — the closing deliverables: synopsis, back-cover copy, query letter, cover brief. (A colophon is the printer's note at the end of a book.) |
| **Presswork** | Production preparation — formatting and packaging the book for delivery. |

### The anti-AI scan

| Term | What it means |
|---|---|
| **the Tic Scan** | The 20-pattern scan for machine-writing tells (described in `deslopify`). |
| **the Overprint** | Pattern #11: one simile extended and laid over another — "as if … as if …". (An overprint is a second impression printed on top of the first.) |

---

## The skills

Each specialist skill is one job. The folders keep their print-shop names because they
are installed paths — call them by name, know them by the job.

| Skill | The job, in plain words |
|---|---|
| `scout` | Market research: genre map, comp titles, positioning |
| `readership` | Builds the reader personas |
| `forme` | Writes the foundation document (the book's plan) |
| `voice-matrix` | Specifies how every character speaks |
| `case-keeper` | Tracks who and what exists, and what everyone knows |
| `collator` | Audits continuity across chapters |
| `setting` | Drafts the prose, one chapter at a time |
| `register` | Aligns dialogue with each character's voice |
| `catchword` | Works the chapter openings and endings |
| `quoin` | Breaks up machine predictability in a draft |
| `composing` | Mechanical cleanup (spelling, punctuation, repetition) |
| `proof-panel` | Evaluates the chapter with independent readers |
| `proof-pull` | The fix-and-remeasure quality loop |
| `corrector` | Revises from evaluation feedback |
| `colophon` | Builds the editorial package |
| `presswork` | Prepares the book for production |
| `press-ledger` | The project's state and decision ledger |
| `series-binder` | Plans series scope and continuity |
| `incunabula-auto` | Runs the whole pipeline in one command |
| `bestseller-studio` | The commercial (bestseller) profile |
| `reader-swarm` | Large simulated reader panels; `--light` runs the four-voice market panel |
| `agent-panel` | retired — the market panel now runs as `reader-swarm --light` |

### Plain craft language

Not every term needs a print-shop name. These stay ordinary: *oscillation*, *emotional
anchor*, *engagement type*, *commercial pacing*, *scene*, *chapter*, *beat*, *voice under
pressure*, *character chaos*, *anti-AI scan*, *narrative debt*, *beat arc*, *scene
function*, *setup and payoff*. The narrative layer (`NARRATIVE_LEDGER.yaml`, rows N1–N4)
speaks plainly.

Utility skills that are not part of this system keep their own names: `copy-editing`,
`deslopify`. (`good-idea` is not part of this system at all: `bundles/good-idea/`, its
own bundle.)
