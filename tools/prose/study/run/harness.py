#!/usr/bin/env python3
"""harness.py - the route probe: the two facts the run cannot start without, captured once.

DECISIONS.md §7 left two questions about the Antigravity subagent route unconfirmed, and both
decide what a manifest row is allowed to claim:

  1. can temperature / top-p / a system prompt be set per call, or are they fixed?
  2. does each response return the responding `modelVersion`?

Neither can be answered by reading the design. They are properties of the route, so they are
probed once, on the first call of the first book, written down, and then read by
`run/dispatch.py` for every filing after it. A record per book would be 52 chances to retype
a value that was never observed; the route does not change per book.

WHAT `settable: false` COSTS
  A harness-fixed setting is recorded as what it applied, never as what was asked for. The
  distinction is the whole point: `temperature: 0.8` in a row means the run set 0.8 and the
  model answered at 0.8. If it could not be set, the row says what the harness used and the
  report states sampling was fixed, as a limitation (§7).

WHAT `model_returned: null` MEANS
  Stop. H3 is a claim about the model that actually wrote; a response with no version leaves
  the row unable to say. `--check` refuses that record rather than letting 52 rows be filed
  against an unmeasured model.

usage:
    python run/harness.py --template        # the questions, and a skeleton to fill
    python run/harness.py --init            # write run/harness.json from the skeleton
    python run/harness.py --check           # validate it, and print what every row records
    python run/harness.py --show            # print the record as filed
"""

import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "harness.json")
KNOWN = ("book_id", "probed_at", "route", "model_sent", "model_returned",
         "version_source", "temperature", "top_p", "system_prompt", "evidence")
SAMPLING = (("temperature", "temperature"), ("top_p", "top-p"),
            ("system_prompt", "system prompt"))

QUESTIONS = """\
Answer these on the first call of the first book (A-01), then never again by hand:

  book_id       which book the probe used, so the record can be traced to a response
  probed_at     UTC ISO timestamp of that call
  route         the harness the subagent ran through (product and version if visible)
  model_sent    the model id we asked for: gemini-3.8-flash
  model_returned  the modelVersion the response itself reported. Not the id we sent.
                  If the response reports none, write null and stop: nothing can be filed.
  version_source  where that version came from (a response field name, UI text, nothing)
  temperature / top_p / system_prompt
                each is {settable, observed, applied}:
                  settable   true only if you changed it and the change took effect
                  observed   the value the call actually used, when settable
                  applied    the harness's own value, when it is not settable
  evidence      one line saying what shows the above, e.g. "A-01 response header, 2026-10-31"

A skeleton, to copy into run/harness.json:
"""


def skeleton():
    return {
        "book_id": "A-01",
        "probed_at": "",
        "route": "",
        "model_sent": "gemini-3.8-flash",
        "model_returned": "",
        "version_source": "",
        "temperature": {"settable": None, "observed": None, "applied": ""},
        "top_p": {"settable": None, "observed": None, "applied": ""},
        "system_prompt": {"settable": None, "observed": None, "applied": ""},
        "evidence": "",
    }


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def errors(rec):
    errs = []
    for k in ("book_id", "probed_at", "route", "model_sent", "version_source", "evidence"):
        if not str(rec.get(k) or "").strip():
            errs.append(f"{k} is empty")
    ts = str(rec.get("probed_at") or "").strip()
    if ts:
        try:
            datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            errs.append(f"probed_at {ts!r} is not an ISO timestamp")
    if "model_returned" not in rec:
        errs.append("model_returned is missing; use null only if the response reported none")
    elif rec["model_returned"] in (None, ""):
        errs.append("model_returned is empty: a response that reports no modelVersion is "
                    "design §7 item O3 unresolved. H3 is a claim about the version that "
                    "wrote, so no row can be filed until the route returns one.")
    for key, label in SAMPLING:
        blk = rec.get(key)
        if not isinstance(blk, dict):
            errs.append(f"{key} must be an object with settable/observed/applied")
            continue
        if not isinstance(blk.get("settable"), bool):
            errs.append(f"{key}.settable must be true or false, not a guess")
            continue
        if blk["settable"]:
            if blk.get("observed") in (None, ""):
                errs.append(f"{key}.settable is true but no observed value is recorded; "
                            f"record what the call actually used")
        elif not str(blk.get("applied") or "").strip():
            errs.append(f"{key}.settable is false but applied is empty; record the "
                        f"harness's own value, or the row records nothing")
    unknown = sorted(set(rec) - set(KNOWN))
    if unknown:
        errs.append("unknown field(s): " + ", ".join(unknown) +
                    " - dispatch reads by name, so a typo here is a silent default")
    return errs


def notes(rec):
    out = []
    sent = str(rec.get("model_sent") or "")
    got = str(rec.get("model_returned") or "")
    if sent and got and not got.startswith(sent):
        out.append(f"model_returned {got!r} does not extend model_sent {sent!r}; that is a "
                   f"real finding only if the route really served a different model")
    return out


def describe(rec):
    lines = [f"Probe record for `{rec.get('book_id')}`, {rec.get('probed_at')}, "
             f"route: {rec.get('route')}."]
    lines.append("")
    lines.append("Every subsequent ingest records these, and finalize writes them into the "
                 "manifest row:")
    lines.append("")
    for key, label in SAMPLING:
        blk = rec.get(key) or {}
        if blk.get("settable"):
            lines.append(f"  {label:<14} {str(blk.get('observed'))!r}")
        else:
            lines.append(f"  {label:<14} {str(blk.get('applied'))!r}   "
                         f"(the harness does not accept one)")
    lines.append(f"  {'model':<14} {str(rec.get('model_returned'))!r}   "
                 f"(from {rec.get('version_source')})")
    lines.append("")
    lines.append("A response reporting any other modelVersion is refused at filing unless "
                 "`--deviation` explains it: design §7 makes a mid-run model change a stop "
                 "condition, and a second sub-cohort is reported, never pooled.")
    fixed = [label for key, label in SAMPLING
             if (rec.get(key) or {}).get("settable") is False]
    if fixed:
        lines.append("")
        lines.append(f"Fixed by the harness: {', '.join(fixed)}. The report carries that as "
                     f"a limitation, and no row claims to have chosen those values.")
    return "\n".join(lines)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--template", action="store_true", help="print the questions")
    ap.add_argument("--init", action="store_true", help="write the skeleton")
    ap.add_argument("--check", action="store_true", help="validate and say what rows record")
    ap.add_argument("--show", action="store_true", help="print the record")
    ap.add_argument("--out", default=DEFAULT)
    ap.add_argument("--force", action="store_true", help="overwrite on --init")
    args = ap.parse_args(argv)

    if args.template:
        print(QUESTIONS)
        print(json.dumps(skeleton(), indent=2))
        return 0

    if args.init:
        if os.path.exists(args.out) and not args.force:
            print(f"{args.out} already exists. A probe record is a measurement: if it was "
                  f"wrong, say so in --check and rewrite it deliberately with --force.")
            return 2
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(skeleton(), fh, indent=2)
            fh.write("\n")
        print(f"wrote {args.out} - fill it from A-01's first call, then run --check")
        return 0

    if args.show:
        if not os.path.exists(args.out):
            print(f"no record at {args.out}; run `--init` on the first book")
            return 2
        print(json.dumps(load(args.out), indent=2))
        return 0

    if args.check:
        if not os.path.exists(args.out):
            print(f"no record at {args.out}: the two route facts are unmeasured, so every "
                  f"row would say 'unrecorded'. Run `--init`, fill it, then `--check`.")
            return 1
        rec = load(args.out)
        errs = errors(rec)
        for e in errs:
            print(f"  problem: {e}")
        for n in notes(rec):
            print(f"  note: {n}")
        if errs:
            print(f"\n{len(errs)} problem(s). A record with blanks is not a measurement.")
            return 1
        print(describe(rec) + "\n")
        return 0

    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
