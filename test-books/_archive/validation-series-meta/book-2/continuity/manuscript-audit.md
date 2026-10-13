# Manuscript continuity audit — Book 2 (Phase 5.6)

**Run:** 2026-09-24, against the seven drafted chapters (15,077 words, all passing `tools/deslop-check.sh`).
**Authority loaded:** `../CANON_LEDGER.yaml` · `../book-1/CANON_LEDGER.yaml` · `foundation.md` ·
`outline.md` · `ENTITY_STATE.yaml` (`R-013`–`R-021`) · the Book 2 additions to `../book-1/voice-dna.md`.

**This is the phase Book 1 shipped without running, and the phase that found its two worst defects.** It
ran here before the score, as the run brief requires.

**Result: 1 CRITICAL (found and fixed), 3 MINOR, 1 STATE note, 9 CLEARED.**

---

## CRITICAL

### [CONT-201] A character who leaves in ch.4 is present in ch.5 and ch.7

- **Audit:** 3a (knowledge/state) · **Severity:** CRITICAL · **Status: FOUND AND FIXED**
- **The defect.** Ch.4 is built on a worker leaving: *"A woman put down what she was holding… Her part was
  the turn."* She is the woman at the turn — the one established in ch.3 who would not tell Merope about
  herself. Ch.5 then opens *"I know how the woman at the turn got here… she is standing at the turn"*
  (present tense), and ch.7 gives her a closing scene at the turn in which she speaks to Merope. **She had
  walked out four chapters' worth of story earlier.** Any reader tracking one character would have caught
  it; the prose gate cannot see it, because the chapters are individually clean.
- **This is the same class as Book 1's `CONT-001`** — a chapter asserting a state no other chapter
  supports. It is the exact failure Phase 5.6 exists to catch, and it is why this phase is not optional.
- **Fix applied — and why this direction.** Two fixes were possible: keep her, so ch.4's leaver is
  somebody else; or keep the departure, and make ch.5 and ch.7 reflect that she is gone. **The second was
  chosen**, because her leaving is what makes ch.5 land: the reveal that every worker arrived when someone
  stopped wanting them is much heavier when the one person who would not tell Merope about herself has
  already walked out, and Merope has to learn it about her from somebody else, afterwards, when it is too
  late to ask her.
- **Edits made:**
  - `chapter-05.md` — the account now ends where it actually ended: a woman walking down the outside of
    the rail, and a new woman taking the turn before the hour is out.
  - `chapter-06.md` — the reference to her history changed from present to past.
  - `chapter-07.md` — the closing turn scene rewritten. The turn is watched by the **new** woman; Merope
    goes there to ask the old one the plain question and she is not there; and the beat lands the
    replaceability of the work — *"I could not have told you the difference if I had not known there was
    one."* The chapter now also closes Merope's *habit* rather than the character: she has walked the whole
    length of the rows to collect a thing she declined to collect while it was standing in front of her.
- **Re-run after the fix:** all three chapters re-gated and PASS.

---

## MINOR

### [MINOR-201] `eleven` is used for two unrelated quantities

`chapter-01.md` counted *fourteen* rows and `chapter-07.md` reports holding the tool for *eleven days*.
The first was originally **eleven** as well — an accidental echo, not a motif. Changed ch.1 to **fourteen**
so the reader does not read a parallel that was not intended.

### [MINOR-202] The day-count holds, but loosely

Arrival is day 1; ch.2 is the second morning; ch.3 is the third day; ch.4 spans roughly days four to six
(*"four days"*, *"five days"*); ch.5 is the sixth morning; ch.6 reports *"a week"*; ch.7 reports eleven
days. Consistent, and deliberately imprecise. **Recorded, not changed:** the prose never states a total
and never dates anything, which is what `book-2.interval` requires. No defect.

### [MINOR-203] Ch.3 attributes a first-afternoon kindness to the woman at the turn that ch.1 does not show

Ch.3: *"she was the first person there who made room for me, and she did it on the first afternoon."*
Ch.1 shows a man moving his work out of the way of her hand, but not this woman. **Not a contradiction** —
ch.1 is a partial account by a narrator who says so — and it is the kind of retrospection the voice is
built on. Recorded so a later editor does not "fix" it.

---

## STATE note

### [STATE-201] Merope's knowledge is staged correctly and must stay that way

She has the individual parts of the pattern from ch.3 (the house, the door, the person, the season) and
assembles the meaning only in ch.5, then immediately explains it away. **Checked chapter by chapter:** no
earlier chapter states the pattern, and no chapter after ch.5 states the theme. This is the same
information-flow shape as Book 1 and it is intact.

---

## CLEARED

| # | Check | Evidence | Verdict |
|---|---|---|---|
| 1 | **`WARN-101` — the tool is present across the middle chapters** (the outline audit's standing check) | `grep -oi tool` per chapter: 6, 6, 7, 5, 3, 3, 1 | **CLEARED.** It never leaves her hands, and ch.3's "heavier" and ch.6's "did not put it down" are consistent with it. |
| 2 | **`WARN-102` — the hand-count** | `grep` for hand-taking / fingers: **0 hits** | **CLEARED.** No hand is taken in Book 2, so Book 1's stated count of four is untouched. |
| 3 | **`MINOR-103` — no interval leak** | `grep -i` for weekdays, months, "a year since": **0 hits** | **CLEARED.** Nothing dates the gap. |
| 4 | **`COL-001` does not appear** | `grep -i beings`: **0 hits** | **CLEARED.** |
| 5 | **Excluded-book residue** | one `absorbed` found in ch.5 and **removed** (the `A22b` canon guard fired on it) | **CLEARED.** No trap, no absorption, no ledger, no record of the dead. |
| 6 | **Naming rule** | every capitalised word in the manuscript deduplicated: only `Achird` and `Scorpius` are proper nouns. Merope never names herself | **CLEARED.** Nothing on the world is named; the constellation is. |
| 7 | **No em dashes / arrows** | `grep -oE "—|→|⇒"`: **0 hits** | **CLEARED**, and consistent with Book 1's draft. |
| 8 | **No host, no spokesperson, no chase** | every worker utterance is an answer to a question about their own part; no pursuit anywhere; no authority figure | **CLEARED.** |
| 9 | **The theme is never stated** | `grep` for "needed is not", "same as being wanted": **0 hits** | **CLEARED.** One incidental use of the word *theme* (*"the theme of the afternoon"*, ch.1) is ordinary English. |

---

## Gate

**Phase 5.6: GATE CLEARED.** One CRITICAL found in prose that had already passed the prose gate 7/7, fixed,
and re-gated. Three minors and one state note recorded.

**What this says about the layer.** The prose gate is mechanical and the outline audit works on plans. The
only thing that catches "a character who left is still in the room" is a pass that reads all seven
chapters against each other, and there is no way to fake it. That is the finding, and it is the same
finding as Book 1's — which is why it is being written down twice.
