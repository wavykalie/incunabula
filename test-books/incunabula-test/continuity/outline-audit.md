# Outline Continuity Audit — Phase 2.8

**Mode:** outline (pre-writing). **Run:** 2026-09-25. **Skill:** `collator`.
**Inputs:** foundation.md, outline.md, voice-matrix.md, artifacts/05-outline.md, ENTITY_STATE.yaml.

Five audits, adapted from the fiction form to nonfiction. Findings are graded
**CRITICAL** (must fix before drafting), **WARNING** (fix or log), **MINOR**.

---

## 1 — Timeline feasibility

| Check | Result |
|---|---|
| Every chapter's era is stated and consistent with `ENTITY_STATE.yaml` timeline | **pass** |
| No figure appears in a chapter outside their life span | **pass** (checked against FIG-01…FIG-22) |
| Reign years not conflated with life years | **pass** — Ch 9 keeps Wu Zetian's reign (690–705) distinct from her death (705) |
| Out-of-order narration is deliberate, not accidental | **pass** — Ch 4 is *reverse* by design (outline.md structural ledger) |
| Ch 1 → Ch 2 transition (210 BCE → 210–195 BCE) has no gap or overlap | **pass** — Ch 1 ends at the tomb (210), Ch 2 opens in the succession crisis that year |

**WARNING — W-201.** Ch 4's reverse structure means the reader meets 23 CE before 9 CE.
The `knowledge_gates` (KG-01) allow the narrator to hold the outcome, but the chapter
must *signal* the reversal in its first three sentences or the reader will think the book
has lost its chronology. **Action:** opening-strategy note already specifies a death-first
hook; drafting must make the reversal explicit by sentence three.

## 2 — Figure availability (no one in two places at once)

| Check | Result |
|---|---|
| No figure required in two chapters on the same date | **pass** |
| Sima Qian appears in Ch 3 and Ch 11 — is the Ch 11 appearance a person or a reference? | **MINOR M-201.** In Ch 11 he must be a *reference* (a text cited), not a character. Logged; drafting note added. |
| Li Si appears in Ch 1 and Ch 4 | **pass** — Ch 4 invokes his rat fable as a callback, not as a live scene (outline.md Ch 4 close) |
| Bodhidharma's historicity | **WARNING — W-202.** The figure is semi-legendary. The chapter must not assert the interview as recorded fact. KG-02 already requires this. |

## 3 — Information flow (no one knows what they cannot)

| Check | Result |
|---|---|
| The narrator uses later sources (Shiji, Zhenguan) — flagged? | **pass** — KG-01, KG-03 require the source to be named as a later document |
| No figure acts on a text not yet written | **pass** |
| Anachronistic concepts | **WARNING — W-203.** The book uses modern analytical words — *legitimacy*, *institution*, *bureaucracy*, *propaganda*. These are the narrator's vocabulary, never a figure's. Drafting rule: a figure may not say "legitimacy". Logged. |
| The Bodhidharma interview | **pass** — KG-02 |

## 4 — Thread planning (every thread has a resolution or a deliberate leave-open)

| Thread | Planted | Resolution | Status |
|---|---|---|---|
| The mirror (Taizong's three) | Ch 8 (and Ch 3 as method) | Ch 9 (blank stele = the third mirror on a woman), Ch 11 (syllabus = the third mirror on a class) | planned |
| Li Si's rats | Ch 1 | Ch 4 closes on the callback | planned |
| The canal | Ch 7 | Ch 10 pays it off as the Tang golden age's infrastructure | planned |
| The examination hall | Ch 7 | Ch 11, where it *is* the argument | planned |
| The central question | Ch 1 | **Deliberately left open** at Ch 11 | planned — this is the ending promise, not an unclosed thread |
| The unnamed cost-bearers | running | Never "resolved" — they recur (Ch 1 tomb, Ch 4 famine, Ch 7 corvée, Ch 10 child) | planned as a refrain |

**No orphaned thread.** All closed threads have a planned closing chapter; the two
deliberate open items are the central question and the cost-bearers refrain, both
documented as intentional.

## 5 — World rules (the book's own rules about itself)

| Rule | Source | Enforced in outline? |
|---|---|---|
| No invented quotation | F-006 | **pass** — voice-matrix anti-pattern 1 |
| No invented interiority | foundation.md | **pass** — figures doc |
| Contested material is flagged | ASSUMPTIONS A-15 | **pass** — Ch 1 (buried scholars), Ch 5 (Xu Province toll), Ch 6 (interview), Ch 10 (toll) all carry a flag instruction |
| Pinyin conventions | ENTITY_STATE OQ-01 | **WARNING — W-204.** Unresolved (author-owned). Drafting will use pinyin in running text and note the decision; if the author overrules, a find-and-replace updates the manuscript. Logged as recoverable. |

---

## Verdict

**CRITICAL findings: 0.** The gate (Phase 2.8 → 3) requires zero CRITICALs. **Pass.**

**Warnings logged:** W-201 (reverse-chapter signalling), W-202 (Bodhidharma historicity),
W-203 (modern analytical vocabulary is narrator-only), W-204 (romanisation choice).

**Minor:** M-201 (Sima Qian in Ch 11 is a reference, not a character).

All warnings are addressed by drafting rules already recorded in `outline.md` and
`voice-matrix.md`, or logged in `maintenance/SESSION_LOG.md` as deferred with rationale.
The manuscript may proceed to Phase 3.
