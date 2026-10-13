# Manuscript Continuity Audit — Phase 5.6

**Mode:** full manuscript. **Run:** 2026-09-25. **Skill:** `collator`.
**Scope:** 11 chapters, 28,263 words, plus foundation.md, outline.md, voice-matrix.md,
ENTITY_STATE.yaml.
**Method:** mechanical probes (name and date greps, arithmetic against stated birth and
event years, entity-state cross-check) followed by a read.

---

## Findings

### CRITICAL — 2, both in prose that had already passed the prose gate

**CONT-101 · Chapter 9 — age does not reconcile.**
The chapter states Wu Zetian was born in 624 and deposed in 705, then calls her
"eighty" at the deposition. 705 − 624 = 81.
**Status: FIXED.** Changed to "eighty-one".

**CONT-102 · Chapter 10 — two ages and a reign length do not reconcile.**
The chapter states Xuanzong was born in 685 and took the throne in 712, then calls him
"sixty-nine" at Mawei in 756 and gives his reign as "forty-three years".
756 − 685 = 71; 756 − 712 = 44.
**Status: FIXED.** Changed to "seventy-one" and "forty-four years".

### WARNING — 1

**CONT-201 · Chapter 8 — age does not reconcile.**
The chapter states Taizong died in 649 and records his birth elsewhere as 598, then says
he died "at fifty-two". 649 − 598 = 51.
**Status: FIXED.** Changed to "fifty-one".

### MINOR — 2

- **CONT-301.** `ENTITY_STATE.yaml` did not carry a birth year for FIG-15 (Taizong) or
  FIG-17 (Wu Zetian) or FIG-18 (Xuanzong), which is *why* the three arithmetic errors
  above were possible. **Status: FIXED.** Birth years added to the entity state, and a
  new check added to the audit method (every stated age must reconcile to two stated
  years, both of which must be in the entity state).
- **CONT-302.** `ENTITY_STATE.yaml` listed FIG-22 (Zhu Xi) with death 1200 but no
  activity window; Chapter 11 references the 1127 fall of Kaifeng and a birth "three
  years after that". 1127 + 3 = 1130, which matches the entity state. **No change
  needed**; recorded as verified.

### CLEAN

- **Name consistency:** every occurrence of every principal figure uses one spelling
  (verified by grep: An Lushan ×8, Du Fu ×8, Li Bai ×7, Sima Qian ×23, Taizong ×17,
  Wang Mang ×24, Zhu Xi ×7, and so on — no variants).
- **Timeline:** no figure acts on a fact unavailable to them; all four `knowledge_gates`
  in the entity state hold (the *Records*, the Bodhidharma tradition, the *Zhenguan*
  compilation, the An Lushan casualty estimates).
- **Information flow:** the narrator's use of later sources is flagged at every point.
- **World rules:** the no-invented-quotation rule (F-006) holds across all 11 chapters.
- **Threads:** the mirror (Ch 8 → 9 → 11), Li Si's rats (Ch 1 → 4), the canal (Ch 7 → 10),
  and the examination (Ch 7 → 11) all close as planned.

---

## The finding that matters

**The prose gate passed all three of these errors.**

CONT-101, CONT-102 and CONT-201 are arithmetic, and the scanner checks sentence shape,
adverb density, anaphora, duplication and fragments. It cannot add. Nothing else in the
pipeline can either, which is why this phase exists and why it ran **before** delivery
rather than after.

This is the same class of defect the prior validation run recorded: Phase 5.6 found a
CRITICAL in prose the gate had passed. It has now done so again, and the fix is a
mechanical check that has been added to the method rather than a resolution to be more
careful.

## Verdict

**CRITICAL remaining: 0** (both found and fixed). **WARNING remaining: 0** (fixed).
**MINOR remaining: 0.**
All three numeric fixes were re-scanned: the manuscript still **PASSES** the prose gate,
0 failing rows.
