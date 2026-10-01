# Demo books

Three complete books produced by this pipeline, shipped so the gates can be run
against real manuscripts before you point them at your own. Each directory is a
self-contained book: `PROJECT_STATE.yaml` (the contract the gates read),
`manuscript/chapters/` (one file per chapter), and the phase artifacts the run
produced.

| book | what it shows |
|---|---|
| `demo-magician/` | *The Trick* — a 1930s conjuring mystery, 34 chapters, complete and swept. The clean run. |
| `muzzle-and-marrow/` | The from-scratch pilot. Its `U1`/`L1` failures are deliberately kept findings — an example of what the gates catch, and what a record of "found, not repaired" looks like. |
| `marrow-light/` | 38 chapters. The book a hand-typed suite list silently omitted — the failure that created `BOOKS.yaml` and `tools/check-registry.py`. |

Run the gates from the repository root:

```bash
bash tools/prose/deslop-check.sh demo-books/demo-magician/manuscript/chapters
python tools/prose/check-uniformity.py demo-books/demo-magician
python tools/prose/check-drift.py demo-books/demo-magician
python tools/prose/check-length.py demo-books/muzzle-and-marrow   # kept L1 finding: exits 1
```

`BOOKS.yaml` registers these books at their production workspace paths, so
`check-registry.py` output will not name `demo-books/` — the copies here are
fixtures for a clone. Workflow artifacts that reference machine paths
(`maintenance/` logs, scratch scripts) are deliberately not shipped.
