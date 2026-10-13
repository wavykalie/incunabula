# v1 manuscript — recovered 2026-09-28

The seven-chapter Merope manuscript is **here**, in `book-1/manuscript/chapters/` and
`book-2/manuscript/chapters/`. The v2 re-chaptered books (eleven chapters each) are the live
versions, at `validation-series/book-1/` and `validation-series/book-2/`.

Nothing here is a draft of the eleven-chapter books, and nothing here was rewritten. This is the
**earlier build**, kept because it is evidence.

---

## What happened

v1 was seven chapters per book. The books were later re-chaptered to eleven to break the uniform
lengths, and that rewrite **overwrote the chapter files in place**. The v1 metadata — outline,
scene packets, ledgers, audits, the build script — was moved out to this archive. The v1
**manuscript** was not archived with it. Its only surviving copy was inside the three v1 EPUBs
in `epubs/`.

So the prose was recovered from the EPUBs on 2026-09-28.

## How it was verified

Recovering text out of a build artefact is the kind of thing that can quietly lose a paragraph,
so it was checked rather than trusted.

**The test:** the archived `tools/build-epub.py` is the exact inverse of the recovery — it turns
paragraph-separated markdown back into `<p>` elements. Rebuilding from the recovered markdown and
diffing against the original v1 EPUBs gives:

| entry | result |
|---|---|
| all 14 chapter XHTML files | **byte-identical** |
| `OEBPS/content.opf` | differs only in the `dcterms:modified` build timestamp |
| `OEBPS/title.xhtml` | differs only by a `Working title.` note the archived script no longer emits |

**The corroboration:** the recorded v1 figures in `incunabula-test/RUN_REPORT.md` are reproduced.

| | recorded | recovered |
|---|---|---|
| vol. 1 CV | 5.8% | **5.7%** |
| vol. 2 CV | 10.8% | **10.8%** |
| vol. 1 chapters | 7 | **7** |
| vol. 2 chapters | 7 | **7** |

The two runs are different tokenizers, which is why the word ranges differ by about ten words per
chapter (2,077–2,402 recorded vs 2,066–2,392 recovered). The CV agreeing to a tenth of a point on
one book and exactly on the other is not something a lossy recovery would produce.

## What this archive is, and is not

- It **is** the v1 prose, verified.
- It is **not** governed by the live pipeline. These books have no `PROJECT_STATE.yaml` at their
  own root — the one here describes v1 and plans **seven** chapters and 2,450 words each, which is
  why `check-length.py` reports them `UNGOVERNED` from the book directory.
- **The uniformity finding lives here.** Seven chapters, a CV near 6% and 11% — this is the
  machine-shaped output that `DRAFTING_FRAMEWORK.md` was written to stop. Keep it for that reason
  above all others.

## The rule this exposed

Archiving moved the *metadata* out of the book and left the *manuscript* behind, in a form nothing
indexed. Nothing reported a gate had gone blind, because no gate was watching for this. Recorded
as an open finding in `incunabula/KNOWN_FINDINGS.md`; the protocol rule that would have caught it
belongs in `incunabula/skills/incunabula-codex/references/maintenance-protocol.md`.
