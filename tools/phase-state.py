#!/usr/bin/env python3
"""phase-state.py — the runner's map reader and state writer.

Two jobs, both for tools/run-phases.sh, both python3 stdlib only:

  phases   print tools/phase-map.yaml as TSV for the bash runner to walk
  gates    print the map's gate commands as TSV
  state    read or write the runner's block in the project state file

NOT A GATE. It measures nothing and judges nothing; it parses a file the runner
owns and moves the runner's own bookkeeping. Same exemption class as
check-pass-evidence.py and preflight.sh: make-ready layer, deliberately absent
from GATE_FREEZE.md's manifest.

YAML here is a strict subset — quoted scalars and inline lists, nothing else.
Anything outside it is a refusal (exit 3), not a guess: a map the parser cannot
read exactly is a map the runner must not walk.

The state file is PROJECT_STATE.yaml at the book root. The runner owns exactly
three top-level keys there — `runner`, `proof_pull`, `revision_cycles` — and
rewrites only those, leaving every other byte untouched. When pyyaml is absent
(the known blind spot), the rewrite is applied without a full parse and that is
printed as NOT CHECKED rather than implied to be fine.

Usage:
    python tools/phase-state.py phases
    python tools/phase-state.py gates
    python tools/phase-state.py state show   --root BOOK
    python tools/phase-state.py state halt   --root BOOK --phase P --gate G --exit N --reason TEXT
    python tools/phase-state.py state advance --root BOOK --phase P [--next P2]
    python tools/phase-state.py state set    --root BOOK --key runner --field status --value TEXT

Exit codes:
    0  ok
    2  the map or the state file is missing, or the state has no runner block
       where one is required (NOT RUN, never a pass)
    3  a file could not be parsed in the accepted shape, or pyyaml rejected the
       rewritten state (refusal; the original file is left untouched)
"""

import argparse
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP_PATH = os.path.join(HERE, "phase-map.yaml")
STATE_NAME = "PROJECT_STATE.yaml"

TOP = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$")
LIST_ITEM = re.compile(r"^-\s+(.*)$")


def die(msg, code=3):
    sys.stderr.write("phase-state: %s\n" % msg)
    sys.exit(code)


def strip_comments(text):
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return out


def parse_scalar(tok, where):
    tok = tok.strip()
    if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"':
        return tok[1:-1]
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        if not inner:
            return []
        items = []
        for part in inner.split(","):
            items.append(parse_scalar(part, where))
        return items
    die("unquoted scalar %r at %s - the map format requires quotes" % (tok, where))


def parse_map(path):
    """Parse the strict subset. Returns (top, gates, phases)."""
    if not os.path.isfile(path):
        die("no phase map at %s" % path, 2)
    with open(path, encoding="utf-8") as fh:
        lines = strip_comments(fh.read())
    top, gates, phases = {}, {}, []
    section = None
    current = None
    for n, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        where = "%s:%d" % (os.path.basename(path), n)
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip())
        if indent == 0:
            if section not in (None,):
                section = None
                current = None
            m_item = LIST_ITEM.match(stripped)
            if m_item:
                die("list item at top level at %s" % where)
            m_top = TOP.match(stripped)
            if not m_top:
                die("cannot parse line at %s: %r" % (where, raw))
            key, val = m_top.group(1), m_top.group(2).strip()
            if val == "":
                if key not in ("gates", "phases"):
                    die("unknown section %r at %s" % (key, where))
                section = key
                current = None
                continue
            if key in top:
                die("duplicate top key %r at %s" % (key, where))
            top[key] = parse_scalar(val, where)
            continue
        # indented: inside a section
        if section == "gates":
            m_top = TOP.match(stripped)
            if not m_top:
                die("cannot parse gates line at %s: %r" % (where, raw))
            gid, gval = m_top.group(1), m_top.group(2).strip()
            if gid in gates:
                die("duplicate gate %r at %s" % (gid, where))
            gates[gid] = parse_scalar(gval, where)
        elif section == "phases":
            m_item = LIST_ITEM.match(stripped)
            if m_item:
                body = m_item.group(1)
                kv = TOP.match(body)
                if not kv:
                    die("phase item is not 'key: value' at %s" % where)
                current = {}
                phases.append(current)
                key, val = kv.group(1), kv.group(2).strip()
                if key != "id":
                    die("a phase must start with id: at %s" % where)
                current[key] = parse_scalar(val, where)
                continue
            m_top = TOP.match(stripped)
            if not m_top:
                die("cannot parse phase line at %s: %r" % (where, raw))
            if current is None:
                die("phase field outside a phase item at %s" % where)
            key, val = m_top.group(1), m_top.group(2).strip()
            if key not in ("id", "name", "skill", "artifacts", "gates", "human"):
                die("unknown phase field %r at %s" % (key, where))
            if key in current:
                die("duplicate phase field %r at %s" % (key, where))
            current[key] = parse_scalar(val, where)
        else:
            die("indented line outside any section at %s: %r" % (where, raw))
    # structural checks: refuse a map the runner cannot safely walk
    if not gates:
        die("the map declares no gates")
    if not phases:
        die("the map declares no phases")
    for p in phases:
        for need in ("id", "name", "skill", "artifacts", "gates", "human"):
            if need not in p:
                die("phase %r is missing %r" % (p.get("id"), need))
        for g in p["gates"]:
            if g not in gates:
                die("phase %s names unknown gate %r" % (p["id"], g))
    return top, gates, phases


def cmd_phases():
    # US (0x1f), not tab: tab is IFS whitespace in bash, and a whitespace
    # delimiter silently drops empty fields - a phase with no gates would shift
    # the human column into the gates column and the runner would walk it wrong.
    _, gates, phases = parse_map(MAP_PATH)
    sep = "\x1f"
    for p in phases:
        sys.stdout.write(sep.join([
            p["id"], p["name"], p["skill"],
            ",".join(p["artifacts"]), ",".join(p["gates"]),
            p["human"].replace("\t", " "),
        ]) + "\n")


def cmd_gates():
    _, gates, _ = parse_map(MAP_PATH)
    for gid in sorted(gates):
        sys.stdout.write("%s\t%s\n" % (gid, gates[gid]))


# --- state file ---------------------------------------------------------------

def state_path(root):
    return os.path.join(root, STATE_NAME)


def read_state(root):
    path = state_path(root)
    if not os.path.isfile(path):
        die("no %s at the book root - the runner needs a state file to mark. "
            "Press-ledger owns it; see skills/press-ledger/SKILL.md." % STATE_NAME, 2)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def yaml_check(text):
    """Return '' when the text parses (or cannot be checked), else the error."""
    try:
        import yaml  # optional; the known blind spot
    except ImportError:
        return ""
    try:
        yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 - report any parse failure
        return str(exc)
    return ""


def set_block(text, key, block):
    """Replace or append one top-level key's block. Nothing else moves."""
    pat = re.compile(r"^%s:\n(?:[ \t].*\n?)*" % re.escape(key), re.M)
    block = block.rstrip("\n") + "\n"
    if pat.search(text):
        return pat.sub(lambda _m: block, text, count=1), True
    if re.search(r"^%s:" % re.escape(key), text, re.M):
        # a scalar form like `revision_cycles: 0`
        pat2 = re.compile(r"^%s:.*\n?" % re.escape(key), re.M)
        return pat2.sub(lambda _m: block, text, count=1), True
    sep = "" if text.endswith("\n") or not text else "\n"
    return text + sep + block, False


def runner_block(fields):
    order = ["status", "current_phase", "resume_from", "reason", "updated"]
    lines = ["runner:"]
    for k in order:
        if k in fields:
            v = str(fields[k]).replace('"', "'")
            lines.append('  %s: "%s"' % (k, v))
    for k in sorted(fields):
        if k not in order:
            v = str(fields[k]).replace('"', "'")
            lines.append('  %s: "%s"' % (k, v))
    return "\n".join(lines) + "\n"


def load_runner(text):
    m = re.search(r"^runner:\n((?:[ \t].*\n?)*)", text, re.M)
    fields = {}
    if not m:
        return fields
    for line in m.group(1).splitlines():
        kv = TOP.match(line.strip())
        if kv:
            fields[kv.group(1)] = kv.group(2).strip().strip('"')
    return fields


def write_state(root, fields, extra_blocks=""):
    text = read_state(root)
    new_text, _ = set_block(text, "runner", runner_block(fields))
    if extra_blocks:
        for key, block in extra_blocks:
            new_text, _ = set_block(new_text, key, block)
    err = yaml_check(new_text)
    if err:
        die("the rewritten %s does not parse; original left untouched: %s"
            % (STATE_NAME, err))
    with open(state_path(root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new_text)
    try:
        import yaml  # noqa: F401
        checked = "parsed with pyyaml"
    except ImportError:
        checked = "written WITHOUT a YAML parser on this machine - parse NOT CHECKED"
    sys.stderr.write("phase-state: %s %s\n" % (STATE_NAME, checked))


def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def cmd_state(args):
    root = args.root
    if not root:
        die("state: --root BOOK is required", 2)
    if args.state_cmd == "show":
        sys.stdout.write(read_state(root))
        return
    fields = load_runner(read_state(root))
    if args.state_cmd == "halt":
        fields.update({
            "status": "HALTED",
            "current_phase": args.phase,
            "resume_from": "%s (gate %s, exit %s)" % (args.phase, args.gate, args.exit),
            "reason": args.reason,
            "updated": now(),
        })
    elif args.state_cmd == "advance":
        nxt = args.next if args.next else args.phase
        status = "RUNNING" if args.next else "COMPLETE"
        fields.update({
            "status": status,
            "current_phase": nxt,
            "resume_from": "",
            "reason": "phase %s gates CLEAR" % args.phase,
            "updated": now(),
        })
    elif args.state_cmd == "set":
        if not args.key:
            die("state set: --key runner is required", 2)
        fields[args.field] = args.value
        fields["updated"] = now()
    else:
        die("unknown state command %r" % args.state_cmd, 2)
    write_state(root, fields)


def main():
    ap = argparse.ArgumentParser(description="the runner's map reader and state writer")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("phases")
    sub.add_parser("gates")
    st = sub.add_parser("state")
    st_sub = st.add_subparsers(dest="state_cmd")
    for name in ("show", "halt", "advance", "set"):
        p = st_sub.add_parser(name)
        p.add_argument("--root", required=True)
        if name == "halt":
            p.add_argument("--phase", required=True)
            p.add_argument("--gate", required=True)
            p.add_argument("--exit", required=True)
            p.add_argument("--reason", required=True)
        if name == "advance":
            p.add_argument("--phase", required=True)
            p.add_argument("--next", default="")
        if name == "set":
            p.add_argument("--key", default="runner")
            p.add_argument("--field", required=True)
            p.add_argument("--value", required=True)
    args = ap.parse_args()
    if args.cmd == "phases":
        cmd_phases()
    elif args.cmd == "gates":
        cmd_gates()
    elif args.cmd == "state":
        cmd_state(args)
    else:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
