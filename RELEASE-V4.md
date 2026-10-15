# Incunabula v4 — release record

**Released:** 2026-10-15 · **Origin:** an author-directed improvement pass. The
instruction was to finish the remaining workstreams — outcome wiring, swarm routing, the
press and persona layer, auto-merge and packing, and a release record — and to publish.
The pass began with a status sweep, and the sweep is why the record starts with defects
rather than features: several checks that had been read as green were not looking.

**Amended the same day — workstream 5 was generalised.** The taste layer shipped with
its author lines enumerated in a config file: three of them, named after the three kinds
of book already in this catalogue. That is a guess about identity, and it is the reason
the layer could not be handed to anyone else. It is now **ductus**: `ductus.yaml` holds
the imprint and the directory, a voice exists because a creator made one (`tools/ductus.py
new`), and each voice carries a contract an agent pilots plus its own developing taste
ledger. The row 5 text below is kept as it shipped rather than rewritten, and the
isolation it describes — which is the load-bearing part — is unchanged and still
asserted. Nothing else in this record moved.

## v4 in one sentence

The loop gains the channel that can tell it it is wrong about the world, and the layer
that lets one engine hold three authorial voices apart — while the defects found on the
way (books born failing their own state check, a frozen gate passing a manuscript it
could not read, a store rewriting records an append did not touch) are fixed at the
cause rather than reported as noise.

## What changed

| # | change | where |
|---|---|---|
| 1 | **The scaffold writes clean state.** `init-book.py` wrote `PROJECT_STATE.yaml` through Python's text mode, which is CRLF on Windows, so a book failed `preflight.sh` row 3 at creation — the KF-005 class: a byte `grep` cannot see and the sentence tokenizer splits wrongly on. Seven books carried one. The write is byte-literal now, the seven files and the registry are LF, and the scaffold has the self-test the other harness tools have (seen to fail: exit 1 naming 25 CR bytes when the bug was reintroduced). | `tools/init-book.py`, `tools/preflight.sh`, 6 state files, `BOOKS.yaml` |
| 2 | **The fifteenth run is registered and repaired.** `grand-standing` was on disk and absent from the registry (the suite would have skipped it silently); its `ENTITY_STATE.yaml` did not parse, which is what made a frozen gate blind (below). | `test-books/grand-standing/`, `BOOKS.yaml`, `tools/niche-pool.txt` |
| 3 | **Outcome wiring.** `tools/outcome-ledger.py`: a prediction recorded **before** publication, falsified afterwards, `report` on prediction error. It refuses the three fabrications — an index-less prediction, a prediction recorded after the outcome was known, and a falsification back-filled onto a book that never predicted. It records an actual it cannot map **verbatim** and reports NOT MAPPABLE rather than inventing the sales-to-index mapping the author deferred. It moves the store's usage counters through `errata-store.py`'s own value formula and mutation log, and refuses to move a PINNED measurement record. | new tool; preflight row 4 |
| 4 | **Swarm routing.** `tools/swarm-route.py` turns a `reader-swarm` run folder into work each skill can take, and refuses to let a simulation speak as a community: a ticket with no claim type, no evidence or no owner is refused; a niche or sensitivity cohort must carry `needs-human-validation` + `human-validate` and lands in the human pile; "readers approve of the ending" is refused with the sentence quoted. A run folder missing its sample map, heatmap or summary is NOT RUN. | new tool + the ticket vocabulary in `skills/reader-swarm/SKILL.md` |
| 5 | **The press and its author lines** — *since replaced by the ductus layer, see the amendment above.* `press.yaml` declared three lines — `folio` (long literary), `quarto` (short high-premise), `octavo` (short prescriptive) — each with its own taste store under `press/<line>/`. Isolation was structural: a declared ledger that is missing is a failure, no two lines may share a store, and a line pointing at the press-wide ledger is refused. `press cross` reported an entry appearing in two ledgers. The same isolation now holds over **creator-made voices**: `ductus.yaml` + `ductus/<slug>/ductus.md` + `ductus/<slug>/COMMONPLACE.md`, checked by `tools/ductus.py check`, plus a voice whose own contract sections are still placeholders reported rather than passed in silence. | `ductus.yaml`, `ductus/`, new `tools/ductus.py` |
| 6 | **Auto-merge and packing.** `errata-store.py automerge` applies `record/errata-policy.yaml` after every run, beside the self-prune: rate-limited to one change per pass (SELF_IMPROVEMENT §5), every deferred candidate printed, pinned records never candidates. `pack` concatenates the archive segments into one bundle with a per-segment digest manifest, and `--verify` fails on a single moved byte. | `tools/errata-store.py`, `record/errata-policy.yaml`, `tools/run-gates.sh` |
| 7 | **The store stopped rewriting records an append did not touch.** The `---` between entries was absorbed into every body, so adding an entry rewrote the record before it; and the import warned "the store was rebuilt" whenever it merely grew. Both fixed, with assertions. | `tools/errata-store.py` |
| 8 | **Two ERRATA entries** (the malformed ledger that blinded a frozen gate; the registry debt re-measured), and one duplicated phase table removed. | `ERRATA.md`, `README.md`, `skills/incunabula/SKILL.md` |

## The defects the pass found

**A frozen gate that passed a book it could not read.** `check-names.py` reads
`ENTITY_STATE.yaml`. With that file malformed — three sections crammed several keys onto
one line — the tool exited 0 and printed **no cast line at all**: it loaded no names and
reported `NAME CHECK OK`. Repaired, the same command reads `cast: 5 first names, 5
surnames`. This is the 2026-10-12 entry's class one layer down: a pass that was never
possible looks exactly like a pass. Recorded in `ERRATA.md` 2026-10-15, `state: observed`,
with two craft-channel candidates noted and not proposed (`check-names.py` is frozen, so
naming an unreadable record as NOT RUN needs the recorded freeze procedure).

**The defect was invisible twice over.** `preflight.sh` row 3 does check that a state
file parses — but only `if import yaml` succeeds, so on a machine without a YAML parser
every canonical state file reports SKIP: named, and correctly not passed, but not a
check either. The audit that found the malformed file ran only after `pyyaml` was
installed, at which point row 3 printed `DOES NOT PARSE` at line 48.

**A "missing record file" that passed.** Before this pass, `prune-stale.py` did not
notice a record file named in its own list had been deleted.

**My own store, found by its own import.** Adding one ERRATA entry changed the previous
record's body, because the entry separator was inside it. A store whose claim is that a
record survives until something falsifies it cannot rewrite one on append.

## What did not change

- **No frozen instrument moved.** `tools/prose/` is byte-identical and `verify-freeze.sh`
  holds at **19/19 rows** — including after `GATE_FREEZE.md` gained a corrected standing
  count (54 → 56 entries, corrected by the self-prune through its recorded path, old
  wording in `maintenance/PRUNING_LOG.md`). No cap, threshold, regex, or corpus changed.
- **No gate can fail differently.** Every new tool is make-ready or routing: it reads
  records, never prose, and no book is judged by it.
- **No book's status was changed, no pass file was written, and no manuscript was
  re-run.** The registry's six problems stand exactly as they stood, at the author's
  ruling.
- **The firewall held.** Reader outcomes cannot move a measurement (asserted), a line's
  taste store cannot receive another line's preference, and no new tool moves a threshold.

## Verification

| check | result |
|---|---|
| `verify-freeze.sh` | **FREEZE HOLDS** — 19/19 rows ok |
| `preflight.sh` (no root) | **PASS**, 1 row SKIPPED (state hygiene, no root given), 8 harness self-tests PASS |
| `preflight.sh` over all 19 book roots | **PASS**, 3 named SKIPs (non-book directories) |
| `init-book.py --self-test` | **PASS** — and seen to fail (exit 1, "25 CR bytes") when the CR was reintroduced |
| `errata-store.py --self-test` | **PASS** — 35 assertions (import, append stability, pins, merge/restore, expire, automerge rate limit, pack digest proven by a moved byte) |
| `errata-store.py check` | **exit 0** — 69 records (55 pinned measurement, 14 craft) |
| `outcome-ledger.py --self-test` | **PASS** — 20 assertions (predict, supersede, falsify, NOT MAPPABLE, firewall) |
| `swarm-route.py --self-test` | **PASS** — 16 assertions (routing, claim types, human pile, approval phrasing, NOT RUN) |
| `ductus.py --self-test` | **PASS** — 17 assertions (creation, slug safety, the unauthored report and its clearing, isolation, leak detection, dispatch); `ductus cross` proven on the real ledgers (injected leak → exit 1 naming it → byte-identical restore → exit 0) |
| `check-errata.py` (frozen) | **OK** — 56 entries, all fields, valid motives and states |
| YAML audit, whole tree | **57/57 files parse** (1 failed before the repair) |
| `validate-controls.sh` | **PARTIAL (exit 2), by design** — the corpus is not at the default path; exit 2 never means fully validated |
| `check-registry.py` | **FAIL — 6 problems, all pre-existing and recorded** (see below) |
| `run-gates.sh` (a demo book) | ran end to end; verdict **FAIL** on 2 rows (length, pass evidence) — the demo books are demos, not gated runs |

## Still open

1. **The registry debt** — five books claim `complete` with zero gated words and no pass
   evidence (`demo-magician` twice, `marrow-light`, `muzzle-and-marrow`,
   `sons-of-heaven-v2`, `kagiroi-drift`), and `quiet-hours` is unregistered. Recorded
   again 2026-10-15 by author ruling; the repair is still either the missing
   `evaluations/*chNN*pass*` files or a status that tells the truth.
2. **The two craft candidates from the new ERRATA entry** — `check-names.py` should name
   an absent or unreadable `ENTITY_STATE.yaml` as NOT RUN (needs the freeze procedure);
   `preflight.sh` row 3 checks four state files but not `NARRATIVE_LEDGER.yaml`, the
   ledger `check-narrative.py` reads.
3. **`validate-controls.sh` full run** — an environment variable, not an acquisition.
4. **The KDP metric set** — deferred by the author, so the outcome ledger reports NOT
   MAPPABLE for any actual not on the index scale, and `report` refuses to compute a
   fitness number rather than guessing the mapping. **No prediction has been recorded
   yet, for any book** — the channel exists and is empty.
5. **Voice assignment** — 14 books carry no `ductus:` in `BOOKS.yaml`; `ductus.py check`
   names them and assigns none. Until then every book is drafted under the root ledger,
   which is where the whole catalogue was drafted. **No voice exists yet either** —
   `ductus/` ships with its README and the merge channel and no voices, because a voice
   is the creator's to make.
6. **automerge and pack are no-ops on the live store**, and that is the measured result,
   not a failure: the duplicate pairs it holds are PINNED measurement records, which
   compaction must never merge, and no pass has archived anything yet.
7. **`A23`** (from v3) — still awaiting the author's ruling on the re-derivation.

## Attribution

Author direction throughout: the instruction was to finish the remaining workstreams and
publish. Where the plan named a workstream but no specification — the ticket vocabulary,
the author voices' identity, the outcome record's shape — the design is the agent's, it
is labelled as such in the tools and in the ERRATA motive lines, and nothing was adopted
on a held-out comparison. Where the agent's design was wrong the author said so and it
was replaced, which is what workstream 5's amendment records: the voices are the
creator's to declare, not the tool author's to enumerate. The measurement channel did not move: every number
above is either a frozen instrument's output or a count taken from the files at the moment
it is printed. The registry's six problems were deliberately left standing, because a
status is a claim by the author about the author's books.

Two of the eight changes were repairs to work from the previous pass rather than new
construction — the store's append instability and the scaffold's line endings — and both
are listed in the table above rather than folded into the features, because a pass that
only reports its additions is not a record.
