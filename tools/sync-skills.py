"""Make incunabula/skills/ the authoritative copy of the Incunabula skill set.

WHY THIS EXISTS
---------------
There were three copies of the framework on this machine and no defined winner:

    incunabula/skills/   the repo        current
    ~/.agents/skills/    installed       drifted (10,693 lines)
    ~/.claude/skills/    installed       the PRE-RENAME v4 names

A skill dispatch reads the installed copy. So a book drafted from scratch would have
been drafted against a snapshot predating the freeze, DRAFTING_FRAMEWORK, and the
archival rules - while every document in the repo described the current one. The
measured result would have meant nothing, and "it worked" would have been
unfalsifiable. This is the seventh instance of the failure in KNOWN_FINDINGS:
the instrument was honest and the gap was filled with an assumption.

SAFETY
------
- Third-party skills (mantis-*, ponytail-*, watch, workctl, ...) are never touched.
  Only names in the rename map and names present in the repo are candidates.
- Superseded skills are MOVED to a quarantine directory, never deleted. There is
  already a `.trash` precedent in .claude/skills.
- Idempotent. Safe to re-run.
- The repo is read-only to this script. It never writes to incunabula/skills/.

Usage:  python tools/sync-skills.py [--check]
        --check  report only, change nothing, exit 1 if drift or quarantine pending
"""

import filecmp
import hashlib
import os
import shutil
import sys
from pathlib import Path

REPO = Path("D:/KDP Books/incunabula/skills")
CLAUDE = Path.home() / ".claude" / "skills"
AGENTS = Path.home() / ".agents" / "skills"
QUARANTINE = Path.home() / "_skills-quarantine-20260929"

# The 20 v4 names superseded by the rename, with their successors. Used to decide
# what is safe to quarantine and to write the provenance line in the README.
RENAME_MAP = {
    "book-genesis": "incunabula",
    "book-genesis-codex": "incunabula-codex",
    "book-genesis-full": "incunabula-auto",
    "book-bestseller-studio": "bestseller-studio",
    "book-editor": "corrector",
    "book-researcher": "scout",
    "manuscript-manager": "press-ledger",
    "narrative-foundation": "forme",
    "prose-craft": "setting",
    "beta-reader": "proof-panel",
    "literary-agent-panel": "agent-panel",
    "book-swarm-panel": "reader-swarm",
    "series-architect": "series-binder",
    "production-prep": "presswork",
    "editorial-package": "colophon",
    # promoted out of v4's optional/ rather than dropped
    "entity-tracker": "case-keeper",
    "continuity-guardian": "collator",
    "reader-persona": "readership",
    "voice-fingerprint": "voice-matrix",
    "book-auto": "incunabula-auto",
}

# Never touch these, whatever else happens. They are not ours.
FOREIGN_PREFIXES = (
    "mantis-", "ponytail", "source-command-seed-templates-", "sync",
    "antigravity", "aso-appstore", "gauntlet-loop", "watch", "workctl",
    "orca-cli", "orchestration", "computer-use", "find-skills",
)
# Ours, but not part of the book pipeline: a video-idea verdict tool.
OURS_EXTRA = {"good-idea"}


def repo_skills():
    return sorted(p.name for p in REPO.iterdir() if p.is_dir())


def is_ours(name):
    if name.startswith(FOREIGN_PREFIXES):
        return False
    return True


def tree_digest(root: Path):
    """sha256 over (relpath, filehash) for every file, order-independent."""
    h = hashlib.sha256()
    if not root.is_dir():
        return None
    files = sorted(p for p in root.rglob("*") if p.is_file())
    for p in files:
        h.update(str(p.relative_to(root)).encode("utf-8"))
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def compare(dest_root: Path, name: str):
    """Return 'missing', 'drift', or 'ok' for one skill in one destination."""
    src, dst = REPO / name, dest_root / name
    if not dst.exists():
        return "missing"
    return "ok" if tree_digest(src) == tree_digest(dst) else "drift"


def main():
    check_only = "--check" in sys.argv
    names = repo_skills()
    targets = [("~/.claude/skills", CLAUDE), ("~/.agents/skills", AGENTS)]

    print("Authoritative source: %s" % REPO)
    print("  %d skills\n" % len(names))

    # ---- 1. quarantine superseded v4 names -------------------------------
    print("1. Superseded v4-named skills")
    pending_q = []
    for label, root in targets:
        if not root.is_dir():
            continue
        for old, new in sorted(RENAME_MAP.items()):
            if not (root / old).is_dir():
                continue
            dest = QUARANTINE / root.parent.name / old
            if dest.exists():
                print("   %-22s %-12s already quarantined" % (label, old))
                continue
            pending_q.append((label, root, old, new, dest))

    if not pending_q:
        print("   none present in either destination - already done\n")
    for label, root, old, new, dest in pending_q:
        succ = "successor: %s (in repo)" % new if (REPO / new).is_dir() else "NO SUCCESSOR"
        if check_only:
            print("   WOULD QUARANTINE %-22s %-12s %s" % (label, old, succ))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(root / old), str(dest))
        (dest / "_SUPERSEDED_BY").write_text(
            "%s\nMoved 2026-09-29 by tools/sync-skills.py.\n"
            "The v4 name is superseded. The live successor is in\n"
            "D:/KDP Books/incunabula/skills/.\n"
            "Full v4 history: D:/KDP Books/_archive/hollow-bridge/book-genesis-v4/\n"
            % succ,
            encoding="utf-8",
        )
        print("   quarantined %-20s -> %s" % (old, dest))
    if pending_q and not check_only:
        print("")

    # ---- 2. sync ---------------------------------------------------------
    print("2. Sync repo -> destinations")
    counts = {}
    for label, root in targets:
        if not root.is_dir():
            print("   %s: MISSING, skipped" % label)
            continue
        root.mkdir(parents=True, exist_ok=True)
        st = {"ok": 0, "updated": 0, "added": 0}
        for name in names:
            state = compare(root, name)
            if state == "ok":
                st["ok"] += 1
                continue
            if check_only:
                if state == "missing":
                    st["added"] += 1
                else:
                    st["updated"] += 1
                continue
            src, dst = REPO / name, root / name
            if dst.exists():
                shutil.rmtree(dst)
                shutil.copytree(src, dst)
                st["updated"] += 1
            else:
                shutil.copytree(src, dst)
                st["added"] += 1
        counts[label] = st
        verb = "would change" if check_only else "synced"
        print("   %-20s %d ok, %d updated, %d added  (%s)"
              % (label, st["ok"], st["updated"], st["added"], verb))
    print("")

    # ---- 3. verify -------------------------------------------------------
    print("3. Verify")
    bad = 0
    for label, root in targets:
        if not root.is_dir():
            continue
        for name in names:
            state = compare(root, name)
            if state != "ok":
                bad += 1
                print("   %-20s %-22s %s" % (label, name, state))
        if not check_only and bad == 0:
            print("   %-20s all %d match the repo byte-for-byte" % (label, len(names)))
    if bad:
        print("   %d skill(s) not matching" % bad)
    else:
        print("   no drift")

    if QUARANTINE.is_dir():
        qn = sum(1 for _ in QUARANTINE.rglob("*/SKILL.md"))
        print("\n   quarantine: %s (%d skills, reversible)" % (QUARANTINE, qn))
    print("   backup:     ~/_skills-backup-20260929 (pre-change copy of both dirs)")

    if check_only and (bad or pending_q):
        print("\nCHECK FAILED - drift or pending quarantine above")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
