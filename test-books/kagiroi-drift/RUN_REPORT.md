# RUN_REPORT — Kagiroi Drift (Short Novel Expansion Run)

Run date: 2026-10-05 · Mode: upgrade pass & structural revision · Status: complete

## Editorial Feedback & Structural Revisions

Implemented from the external structural critique of Draft 12:

1. **Fired the Minato Pod (D-001 RESOLVED)**:
   - Trapped Kaname and Sakuya in Skiff Lock Omega in Chapter 7 under identical sensory conditions (total vacuum silence, freezing cold, failed power, clicking manual purge toggle).
   - Reversal executed: Sakuya anchors Kaname, using voice, breath, and heartbeat to pull Kaname out of the decompression panic, breaking the one-directional somatic circuit and resolving the trauma debt on-page.

2. **Brought Mizore Back (D-002 DEFERRED with series intent)**:
   - Mizore returns in Chapter 5 in the cargo bay of the *Akegata-Maru* with an industrial arc-torch, demanding her salvage cut.
   - Mizore reveals her past role in the Callisto recovery flotilla, forcing the unburied truth of the Minato-9 pod out into the open.
   - Sakuya fiercely defends Kaname, negotiating a clean deal: Mizore takes four deuterium blocks and titanium salvage rights, while Shin-Murakumo secures all 36 remaining coolant canisters.
   - Mizore departs in Chapter 8 burning for the Jovian transit—leaving an open series hook for Book Two.

3. **Broke the Circuit on Purpose (N2 Variety)**:
   - In Chapter 3, during an acute acoustic shear spike, Kaname attempts the familiar physical anchoring.
   - It fails completely: Sakuya violently shoves Kaname back against the conduit rack, calling out Kaname's use of touch as a shield against silence.
   - Crisis resolved through technical competence: manual hydraulic valve bypass and conduit repair.

4. **Realistic Hard-SF Physics & Grounded Dialogue**:
   - Replaced breathless whispering outside intimate scenes with dry, authentic, professional salvage jargon.
   - Fixed acceleration figures: the slingshot burn in Chapter 6 is a realistic 3.8g sustained for 190 seconds with liquid-suspension acceleration couches, pneumatic counter-pressure bio-gel suits, and acoustic thrust vectoring.

5. **Disciplined Intimacy Pacing**:
   - Cut Chapter 2's intimate scene in half to maintain narrative velocity.
   - Preserved Chapter 8's sunrise lovemaking in the cupola as the fully earned emotional resolution.

6. **Canister Arithmetic Reconciled (D-006 RESOLVED)**:
   - Exactly 40 military-grade neuro-coolant canisters on the *Akegata-Maru*.
   - 4 consumed in Chapter 4 for Sakuya's emergency spinal refill.
   - 36 locked safely in Sakuya's vault at Sensor Well 04 in Chapter 5 and Chapter 8.

---

## Gate Status at Delivery

| Gate | Target / Threshold | Result | Status |
| :--- | :--- | :--- | :--- |
| **L1 length** | [15,000–25,000] words | 15,786 words across 8 chapters | **PASS** |
| **N1 debt** | All obligations resolved or deferred | 5 resolved, 1 deferred (D-002 series fuel), 0 open | **PASS** |
| **N2 repetition** | No duplicate beat arcs | 8 distinct chapter arcs | **PASS** |
| **N3 scene function** | 4 balanced functions | 2 character revelation, 2 plot turn, 2 relationship shift, 2 theme payoff | **PASS** |
| **U1 uniformity** | CV >= 22.0% (fail under 22%) | CV 24.7% (range 1,122 to 2,749 words, ratio 2.45x) | **PASS** |
| **A1 arc** | Reversals per bin >= 0.45 | 0.641 reversals/bin (above human median 0.575) | **PASS** |
| **D1 drift** | Voice-step <= 2.47 | 0.83 voice-step | **PASS** |
| **D2 drift** | Sustained trend <= 0.75 | 0.67 rho | **PASS** |
| **Names check** | Zero collisions, zero high-prior tropes | 0 collisions, 0 high-prior tropes | **PASS** |
| **Deslop check** | Zero hard slop violations | PASS across all 8 chapters (0 hard violations) | **PASS** |
| **Drafting lint** | No rule over cap, per chapter | 0 chapters over cap across 36 rules (15,480 words); recorded in `NARRATIVE_LEDGER.yaml` `lint_run`/`lint` | **PASS** |
| **Preflight** | Freezes, skills, LF line endings | 15/15 tools verified, clean state | **PASS** |

### What the drafting lint found (2026-10-05, Freeze 17)

Run over all 8 chapters with `tools/lint-chapter.py`, which reads its rules live out of
`deslop-check.sh` and reports `line:col` spans. Full results in `NARRATIVE_LEDGER.yaml`.

- **No chapter exceeds any cap.** Densest single rows: `D2` rule of three at 2.91/1k in
  ch-07 (cap 5/1000), `D3` -ly adverbs at 12.59/1k in ch-04 (cap 26/1000), `D1` em dash
  at 3.91/1k in ch-01 (cap 10/1000).
- **The linter and the scanner agree on every rule except one, and the scanner is wrong.**
  `A23` (parenthetical dash) reads 0.00 on all 8 chapters under `deslop-check.sh` and 4
  occurrences under the linter — ch-01, ch-04, ch-05 twice. The rule's bracket class is
  `[^—\n]`, which in POSIX ERE means em-dash, backslash, or the letter **n**, so the rule
  can only fire on an n-free parenthetical dash. All four occurrences contain one
  (neuro, sudden, ozone, frozen). Raised as `ERRATA.md` 2026-10-05 at `state: proposed`;
  the frozen scanner is untouched at `20e1976d20312974`. Measured read-only over the
  installed calibration corpus (449 chapter files, 2,562,491 words), the frozen regex
  matches 561 of the 1,159 occurrences the rule is written to match — it cannot see
  51.6% of them. The fix is not a one-character edit: under the intended reading the worst
  fiction chapter reads 6.03/1k, and the file's own "~1.5x the worst calibration
  document" rule would then want a cap near 9/1000. Worst true reading in this book is
  0.80/1k in ch-05, so no gate outcome changes for it either way.
- **`D3` precision.** 3 of 117 hits are not adverbs — `assembly`, `firefly` twice. The
  regex is any word of 4+ lowercase letters ending in `-ly`. Both instruments share it, so
  this is rule precision, not disagreement.
- **`A22b` fired twice in ch-04 and both are true negatives.** "She absorbed the kinetic
  shock" and "shock-absorbing silicone" are the mechanical sense, not the emotional sense
  the canon guard watches for. `WARN_ONLY` firing and correctly costing nothing.

---

## Deliverables Generated

- Complete Formatted Master: `delivery/formatted/kagiroi-drift.md` (15,786 words)
- Full Raw Manuscript: `manuscript/full-manuscript.md`
- Amazon KDP DOCX (6"×9" Trade Paperback): `delivery/formatted/kagiroi-drift.docx`
- Amazon KDP EPUB 3: `delivery/formatted/kagiroi-drift.epub`
- Catalog Mirror: `epubs/kagiroi-drift.epub`
