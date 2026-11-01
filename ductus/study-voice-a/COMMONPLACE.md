# COMMONPLACE — Study Voice A

This voice's own taste ledger, and only this voice's. Nothing outside this directory is
evidence for a Study Voice A decision, and nothing here is enforced against a book.

The entry types and the ceremony are the root `COMMONPLACE.md`'s — `decision`,
`preference`, `outcome`, `promotion` — with the same formats and the same limits:

- **`decision`** — one real editorial choice, made between named alternatives.
- **`preference`** — distilled taste, written only after three agreeing decisions, and
  written `emergent`: guidance the next book may decline with a reason. A `limit:` line
  is required, because a preference without one is a rule.
- **`outcome`** — what readers did, with the prediction recorded before publication.
- **`promotion`** — a change the verifier stack adopted, with its falsifier.

**A preference that turns out to hold for another voice is not copied across.** It is
merged deliberately, dated, in `ductus/PROMOTIONS.md`, naming the evidence that
justified it in the second voice. A preference that appears in two ledgers by accident
has stopped being either one's, and `python tools/ductus.py cross` reports it.

**No decisions recorded yet.** An empty ledger is the honest state of a new voice —
seeding it with invented taste would make taste a default.
