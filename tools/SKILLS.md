# The skill set has one authoritative copy

**`incunabula/skills/` is the source of truth. The copies in your home directory are
installed artifacts and are expected to be byte-identical to it.**

A skill dispatch reads the *installed* copy. That is the whole reason this rule exists.

## The state this replaced

On 2026-09-29 there were three copies of the framework on this machine and no defined
winner:

| location | what it was | state found |
|---|---|---|
| `incunabula/skills/` | the repo, 29 skills | current |
| `~/.agents/skills/` | installed | drifted, 10,693 lines |
| `~/.claude/skills/` | installed | the **pre-rename v4 names** |

The `~/.claude/skills/` copy held `book-genesis`, `book-editor`,
`manuscript-manager`, `narrative-foundation`, `prose-craft` and 15 others — versions
that predate the freeze, `DRAFTING_FRAMEWORK.md`, and the archival rules, and that have
no `maintenance-protocol.md` at all. The installed `incunabula-codex` was a snapshot from
before §7a existed.

So a book drafted from scratch would have been drafted against a specification that no
document in the repo described, and every measurement taken from it would have been
meaningless while looking entirely normal. This is the seventh instance of the failure
recorded in `KNOWN_FINDINGS.md`: the instrument was honest, and the gap between "the
spec exists" and "the spec that runs" was filled with an assumption that they were the
same thing.

## The rule

1. **Edit skills in `incunabula/skills/`, never in a home directory.** A home copy is
   overwritten by the next sync and was not under version control.
2. **After any edit under `skills/`, run the sync** before dispatching anything.
3. **Never install a skill under a superseded name.** The rename map is in
   `_archive/README.md` and in `RENAME_MAP` in `tools/sync-skills.py`.
4. **Third-party skills are never touched.** `mantis-*`, `ponytail*`, `watch`,
   `workctl`, `orca-cli`, `computer-use`, `find-skills`, `gauntlet-loop`,
   `antigravity-protocol`, `aso-appstore-screenshots` and the
   `source-command-seed-templates-planning-*` family are excluded by prefix and survive
   every sync untouched.

## Running it

```bash
cd "D:/KDP Books/incunabula"

python tools/sync-skills.py            # quarantine superseded names, sync, verify
python tools/sync-skills.py --check    # report only; changes nothing; exit 1 on drift
```

The check is a byte-for-byte tree comparison (sha256 over path + content of every file),
not a line count. Exit codes: `0` clean, `1` drift or a pending quarantine.

## Reversibility

Two independent safety nets, because this deletes nothing:

- `~/_skills-backup-20260929/` — a full copy of both skill directories as they were
  before the first sync (8.6 MB).
- `~/_skills-quarantine-20260929/` — the 20 superseded v4-named skills, moved rather
  than removed, each carrying a `_SUPERSEDED_BY` file naming its live successor and
  pointing at `_archive/hollow-bridge/book-genesis-v4/` for the full v4 git history.

To undo a single skill: move it back from the quarantine directory. To undo everything:
restore from the backup.

## Why it is not in GATE_FREEZE.md as a sixteenth row

Freeze 6 closed the instrument class: fifteen rows, all of which measure something about
a manuscript. This measures which copy of the *tool* will run, which is a different
question — and a more dangerous one, because a manuscript affected by it looks entirely
normal. It is exempt from the freeze because it moves no gate file; adding a row would
mean freezing a check about the freeze mechanism itself, so the next session to touch any
gate would have to re-record it.

Run it explicitly rather than on every gate run: at the start of a drafting session, and
after any edit under `skills/`.
