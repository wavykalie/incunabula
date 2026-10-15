#!/usr/bin/env python3
"""swarm-route.py — turn a reader-swarm run into work each skill can take, without
letting a simulation speak as a community.

WHY THIS EXISTS
  `reader-swarm` writes a run folder full of reports, and the skill's own core rule
  is the one that gets lost the moment the reports become tasks: three kinds of
  claim must stay apart — simulated signal (a hypothesis from fictional readers),
  editorial judgment (the running agent's craft read), and needs human validation
  (anything touching lived culture, religion, trauma, law, medicine, or a protected
  community). A pile of markdown does not enforce that; the routing step does, and
  without it a simulated cohort's objection becomes a revision ticket with nobody
  left to tell where it came from.

  It also enforces the skill's own cap: simulated niche approval is capped at *flag*
  unless a human validated it. A ticket about a niche or sensitivity cohort is
  therefore not routable at all — the tool refuses it into the human pile rather
  than passing it to a skill as work.

WHAT IT WILL NOT DO
  - It will not route a ticket with no evidence. A ticket without a line or scene is
    a wish, and this directory does not accept wishes as work.
  - It will not route a ticket whose claim type, disposition, or owner is missing or
    unknown. An unlabelled ticket is the failure mode, not an incomplete one.
  - It will not report a missing artifact as an absence of findings. A run folder that
    has no risk heatmap is NOT RUN, and NOT RUN is never PASS (the same rule
    run-gates.sh applies to the gates).
  - It will not edit the run's own reports. It reads them and writes routing.md.
  - It is not a gate on prose. Make-ready class, like preflight.sh: it routes records.

usage:  tools/swarm-route.py route <run-dir> [--check] [--self-test]
          <run-dir>  evaluations/book-swarm/<date>-<slug>/
          --check    validate and report only; write no routing.md

EXIT
  0  every ticket routed (or, with --check, every ticket would route)
  1  at least one refusal or missing artifact — the refusal names the rule
  2  could not run (no run folder, no ticket file)
"""

import os
import re
import shutil
import sys
import tempfile

# The three claim types (reader-swarm's core rule) and where a finding goes.
CLAIMS = ("simulated-signal", "editorial-judgment", "needs-human-validation")
DISPOSITIONS = ("fix", "investigate", "ignore", "human-validate")
OWNERS = ("setting", "register", "catchword", "quoin", "composing", "proof-panel",
          "proof-pull", "corrector", "collator", "case-keeper", "forme",
          "voice-matrix", "colophon", "presswork")

# A cohort whose subject is lived culture is never routable to a skill: the skill's
# scoring section caps simulated niche approval at flag until a human validated it.
HUMAN_COHORTS = ("niche", "sensitivity", "cultural", "religious", "geopolitical")

# Simulated approval phrased as approval. Matched narrowly and reported with the
# sentence, so a false positive can be seen and argued with rather than obeyed.
APPROVAL_PATTERNS = (
    r"\b(readers?|audiences?|reviewers?|the community|the market|culture|cohorts?)\s+"
    r"(approve[sd]?|endorse[sd]?|validat\w+|accept[sd]?|agree[sd]?|agree)\b",
    r"\b(culturally|community|socially)\s+(approved|endorsed|validated|sanctioned)\b",
    r"\b(readers?|audiences?)\s+(love[sd]?|loved)\s+it\b",
)

# The artifacts a run folder must hold for its findings to be routable. Named here
# and in the skill's Output section, so the two cannot drift.
CORE_ARTIFACTS = ("sample-map.md", "risk-heatmap.md", "revision-tickets.md", "summary.md")
TICKET_FILE = "revision-tickets.md"
ROUTING_FILE = "routing.md"

FIELD = re.compile(r"^- \*\*(\w+):\*\*\s+(.*)$")
TICKET = re.compile(r"^#{2,3}\s+(T-\d+)\s+[—-]\s+(.*)$")


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    """LF always: a CR is the byte grep cannot see (KF-005)."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def parse_tickets(text):
    """Tickets in file order: an id, a title, and the fields under it."""
    tickets, cur = [], None
    for i, line in enumerate(text.splitlines(), 1):
        m = TICKET.match(line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "line": i, "fields": {}}
            tickets.append(cur)
            continue
        if cur is not None:
            fm = FIELD.match(line.strip())
            if fm:
                cur["fields"][fm.group(1).lower()] = fm.group(2).strip()
    return tickets


def check_ticket(t):
    """Every rule a ticket must satisfy, each refusal naming the rule it broke."""
    bad = []
    f = t["fields"]
    who = f"{t['id']} {t['title']}"
    if not t["title"]:
        bad.append((t["id"], "the ticket has no subject line"))
    for name, vocab in (("claim", CLAIMS), ("disposition", DISPOSITIONS), ("owner", OWNERS)):
        val = f.get(name, "")
        if not val:
            bad.append((who, f"missing `{name}` — an unlabelled ticket is how a "
                             f"simulation becomes a task. One of: {', '.join(vocab)}"))
        elif val not in vocab:
            bad.append((who, f"`{name}: {val}` is not in the vocabulary "
                             f"({', '.join(vocab)})"))
    if not f.get("evidence"):
        bad.append((who, "no `evidence` — a ticket without a line, scene or file is a "
                         "wish, and a wish is not work"))
    if not f.get("issue"):
        bad.append((who, "no `issue` — what happened, in one sentence"))
    for name in ("issue", "evidence", "title"):
        text = f.get(name, "") if name != "title" else t["title"]
        for pat in APPROVAL_PATTERNS:
            m = re.search(pat, text, re.I)
            if m:
                bad.append((who, f"simulated approval phrased as approval "
                                 f"({m.group(0)!r}): fictional readers cannot approve "
                                 "anything. Say `simulated-signal` or "
                                 "`needs-human-validation`."))
                break
    cohort = (f.get("cohort") or "").lower()
    if any(h in cohort for h in HUMAN_COHORTS):
        if f.get("claim") != "needs-human-validation" or \
                f.get("disposition") != "human-validate":
            bad.append((who, f"cohort {f.get('cohort')!r} is a lived-culture proxy: it "
                             "must carry claim `needs-human-validation` and disposition "
                             "`human-validate` (simulated niche approval is capped at "
                             "flag until a human validated it)"))
    return bad


def route(run_dir, check_only=False):
    if not os.path.isdir(run_dir):
        print(f"swarm-route: {run_dir} is not a directory.")
        return 2, None
    tickets_path = os.path.join(run_dir, TICKET_FILE)
    missing = [a for a in CORE_ARTIFACTS if not os.path.isfile(os.path.join(run_dir, a))]
    if not os.path.isfile(tickets_path):
        print(f"swarm-route: no {TICKET_FILE} in {run_dir}.")
        print("  A run with a heatmap and no tickets has findings nobody can act on;")
        print("  a run with tickets and no heatmap has not looked for the risk.")
        return 2, None

    tickets = parse_tickets(read_text(tickets_path))
    refusals = []
    for t in tickets:
        refusals.extend(check_ticket(t))

    ok_tickets = [t for t in tickets
                  if not any(r[0] == t["id"] or r[0].startswith(t["id"]) for r in refusals)]
    human = [t for t in ok_tickets if t["fields"]["disposition"] == "human-validate"]
    by_owner = {}
    for t in ok_tickets:
        if t["fields"]["disposition"] == "human-validate":
            continue
        by_owner.setdefault(t["fields"]["owner"], []).append(t)

    lines = [
        f"# Routing — {os.path.basename(os.path.normpath(run_dir))}",
        "",
        f"Generated by `tools/swarm-route.py` from `{TICKET_FILE}`. Never hand-edited.",
        "",
        "Three kinds of claim are kept apart here, and the labels are the point:",
        "**simulated signal** is a hypothesis from fictional readers, **editorial",
        "judgment** is a craft read, and **needs human validation** is anything touching",
        "lived culture, religion, trauma, law, medicine, or a protected community.",
        "Nothing in this file is community approval, and nothing in it outranks a real",
        "reader or a paid consultant.",
        "",
        f"tickets: {len(tickets)} · routed: {len(ok_tickets)} · refused: "
        f"{len(refusals)} · to a human: {len(human)}",
        "",
    ]
    if missing:
        lines += ["## NOT RUN — artifacts the run folder does not hold", ""]
        lines += [f"- `{a}` — absent, so nothing was measured by it. NOT RUN is never PASS."
                  for a in missing]
        lines += [""]
    if human:
        lines += ["## To a human — do not route these to a skill", ""]
        for t in human:
            lines.append(f"- **{t['id']}** {t['title']} — cohort "
                         f"{t['fields'].get('cohort', 'n/a')}; "
                         f"claim {t['fields']['claim']}")
        lines += ["", "These stay here until a person answers them. Routing one to a",
                  "skill would be the simulation deciding something it cannot decide.", ""]
    for owner in sorted(by_owner):
        lines += [f"## {owner} — {len(by_owner[owner])}", ""]
        for t in by_owner[owner]:
            lines += [f"- **{t['id']}** {t['title']} "
                      f"({t['fields']['disposition']}, {t['fields']['claim']})",
                      f"  - issue: {t['fields']['issue']}",
                      f"  - evidence: {t['fields']['evidence']}"]
        lines += [""]
    if refusals:
        lines += ["## Refused — not routed, and why", ""]
        lines += [f"- **{who}** {why}" for who, why in refusals]
        lines += [""]

    out = "\n".join(lines).rstrip() + "\n"
    if check_only:
        rp = os.path.join(run_dir, ROUTING_FILE)
        current = read_text(rp) if os.path.isfile(rp) else None
        if current != out:
            print(f"swarm-route: {ROUTING_FILE} is missing or stale in {run_dir}")
            return 1, refusals
    else:
        write_text(os.path.join(run_dir, ROUTING_FILE), out)

    print(f"swarm-route: {os.path.basename(os.path.normpath(run_dir))} — "
          f"{len(tickets)} ticket(s), {len(ok_tickets)} routed, "
          f"{len(refusals)} refused, {len(human)} to a human")
    for a in missing:
        print(f"  NOT RUN  {a} — absent from the run folder")
    for who, why in refusals:
        print(f"  REFUSED  {who}: {why}")
    if not check_only:
        print(f"  wrote {ROUTING_FILE}")
    return (1 if (refusals or missing) else 0), refusals


# --- self-test -------------------------------------------------------------

GOOD = """### T-001 — chapter-03, the fountain scene
- **cohort:**    genre devourer
- **claim:**     simulated-signal
- **evidence:**  manuscript/chapters/chapter-03.md:118
- **issue:**     the reveal reads as withheld
- **disposition:** fix
- **owner:**     corrector
"""

APPROVAL = """### T-002 — the fountain
- **cohort:**    public reviewer
- **claim:**     simulated-signal
- **evidence:**  cohort report 3
- **issue:**     readers approve of the ending
- **disposition:** ignore
- **owner:**     corrector
"""

UNLABELLED = """### T-003 — chapter-07
- **cohort:**    hostile continuity reader
- **evidence:**  chapter-07.md:4
- **issue:**     the ledger says ch 7 but the text says ch 9
- **owner:**     collator
"""

NICHE = """### T-004 — the funeral rite
- **cohort:**    niche-risk proxy
- **claim:**     simulated-signal
- **evidence:**  risk-heatmap.md:12
- **issue:**     the rite is described without a source
- **disposition:** investigate
- **owner:**     setting
"""

NOWISH = """### T-005 — pacing
- **cohort:**    genre devourer
- **claim:**     editorial-judgment
- **issue:**     chapter 12 sags
- **disposition:** fix
- **owner:**     corrector
"""


def selftest():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    tmp = tempfile.mkdtemp(prefix="swarm-route-")
    try:
        run = os.path.join(tmp, "evaluations", "book-swarm", "2026-10-15-demo")
        os.makedirs(run)
        for a in ("sample-map.md", "risk-heatmap.md", "summary.md"):
            write_text(os.path.join(run, a), f"# {a}\n")
        write_text(os.path.join(run, TICKET_FILE),
                   "\n".join([GOOD, APPROVAL, UNLABELLED, NICHE, NOWISH]))

        rc, refusals = route(run)
        # one ticket can break more than one rule, and each broken rule is named:
        # T-003 carries neither claim nor disposition, so it owes two refusals.
        reasons = {}
        for who, why in refusals:
            reasons.setdefault(who.split()[0], []).append(why)

        def refused(tid, needle):
            return any(needle in why for why in reasons.get(tid, []))

        ok(rc == 1, "route: a run with refusals exits 1")
        ok(len(refusals) == 5 and set(reasons) == {"T-002", "T-003", "T-004", "T-005"},
           f"route: the bad tickets are refused, T-001 is not ({len(refusals)} refusal(s))")
        ok(refused("T-002", "simulated approval phrased as approval"),
           "route: a simulated cohort 'approving' is refused, the phrasing quoted")
        ok(refused("T-003", "missing `claim`") and refused("T-003", "missing `disposition`"),
           "route: an unlabelled ticket is refused once per missing label")
        ok(refused("T-004", "lived-culture proxy"),
           "route: a niche cohort cannot be routed as an ordinary ticket")
        ok(refused("T-005", "no `evidence`"),
           "route: a ticket without evidence is refused")

        routing = read_text(os.path.join(run, ROUTING_FILE))
        ok("## corrector" in routing and "T-001" in routing,
           "route: the good ticket is routed to its owner")
        ok("## Refused" in routing and "T-002" in routing.split("## Refused")[1],
           "route: refusals land in the file, so the run cannot claim clean routing")
        ok("\r" not in routing, "route: nothing written carries a CR (KF-005)")

        # a clean run routes with exit 0, and --check reports before writing
        clean = os.path.join(tmp, "evaluations", "book-swarm", "2026-10-15-clean")
        os.makedirs(clean)
        for a in ("sample-map.md", "risk-heatmap.md", "summary.md"):
            write_text(os.path.join(clean, a), f"# {a}\n")
        write_text(os.path.join(clean, TICKET_FILE), GOOD + "\n" + NICHE.replace(
            "claim:**     simulated-signal", "claim:**     needs-human-validation").replace(
            "disposition:** investigate", "disposition:** human-validate"))
        ok(route(clean, check_only=True)[0] == 1, "--check: a stale routing.md is reported")
        ok(not os.path.isfile(os.path.join(clean, ROUTING_FILE)),
           "--check: writes nothing")
        rc_clean, _ = route(clean)
        ok(rc_clean == 0, "route: a clean run exits 0")
        ok("To a human" in read_text(os.path.join(clean, ROUTING_FILE))
           and "T-004" in read_text(os.path.join(clean, ROUTING_FILE)),
           "route: a properly-labelled niche ticket goes to the human pile, not a skill")
        ok(route(clean, check_only=True)[0] == 0, "--check: a fresh routing.md passes")

        # a missing core artifact is NOT RUN, never a silent pass
        thin = os.path.join(tmp, "evaluations", "book-swarm", "2026-10-15-thin")
        os.makedirs(thin)
        write_text(os.path.join(thin, TICKET_FILE), GOOD)
        rc_thin, _ = route(thin)
        ok(rc_thin == 1 and "NOT RUN" in read_text(os.path.join(thin, ROUTING_FILE)),
           "route: a run folder missing its heatmap exits 1 and says NOT RUN")

        # no ticket file at all
        ok(route(os.path.join(tmp, "nowhere")) == (2, None),
           "route: a missing run folder is exit 2")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions (routing, claim types, human pile, "
          "evidence, approval phrasing, NOT RUN, --check).")
    return 0


# --- main ------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    if args[0] in ("selftest", "--self-test"):
        return selftest()
    if args[0] != "route":
        print(f"swarm-route: unknown command {args[0]}")
        return 2
    rest = args[1:]
    if not rest:
        print("swarm-route: route needs a run directory.")
        return 2
    rc, _ = route(rest[0], check_only="--check" in rest)
    return rc


if __name__ == "__main__":
    sys.exit(main())
