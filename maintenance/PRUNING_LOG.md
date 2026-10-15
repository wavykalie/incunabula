# PRUNING LOG

**Append-only. This file is the record of what was pruned, archived, or deliberately left
alone — and the "left alone" half is the point.** A log that only ever lists deletions can
never demonstrate that anything was protected.

`tools/prune-stale.py` writes here when it repairs a standing claim in place: the old
wording is preserved verbatim, with the date and the reason, so a corrected sentence can be
told apart from a sentence that was always true. Dated history — a claim inside an ERRATA
entry, a freeze entry, a session record — is never edited and never logged here: it is
reported for a ruling instead, because a record of what was true then is history and not
drift.

The format, in the maintenance protocol's §7 shape:

```
### YYYY-MM-DD — what changed, and why
- **file:**       which record
- **was:**        the old wording, verbatim
- **now:**        the new wording
- **cause:**      what moved the program
- **authority:**  the rule that permits the repair
```

---

**No entries.** Nothing has been pruned, archived, or corrected in this install yet.
Nothing has been protected from pruning either — that is not an omission. It is the
starting state, and it changes the first time a record drifts from the program or a file
is deliberately left where it is.
